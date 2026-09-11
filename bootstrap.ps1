<#
========================================================================================
AUTONOMOUS OS DEBUGGING AGENT - 1-LINE CLOUD BOOTSTRAPPER & RECOVERY RUNNER
========================================================================================
Usage in WinRE / PowerShell / Command Prompt:
    irm https://raw.githubusercontent.com/<YOUR_GITHUB_USERNAME>/os-debug-agent/main/bootstrap.ps1 | iex

Or in CMD / WinRE Command Prompt:
    powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/<YOUR_GITHUB_USERNAME>/os-debug-agent/main/bootstrap.ps1 | iex"
========================================================================================
#>

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ErrorActionPreference = 'SilentlyContinue'

Write-Host @"
===============================================================================
       ⚡ AUTONOMOUS OS DEBUGGING AGENT - CLOUD RESCUE INSTALLER ⚡
===============================================================================
[+] Initializing live cloud recovery environment...
"@ -ForegroundColor Cyan

# 1. Determine Working Directory (Permanent User Directory)
$targetDir = if ($env:USERPROFILE) { "$env:USERPROFILE\os-debug-agent" } elseif ($env:LOCALAPPDATA) { "$env:LOCALAPPDATA\os-debug-agent" } else { "C:\os-debug-agent" }
if (!(Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}
Set-Location $targetDir
Write-Host "[1/4] Permanent user workspace set to: $targetDir" -ForegroundColor Green

# 2. Check for Python on the machine or in internal drives (C:, D:, etc.)
Write-Host "[2/4] Searching for functional Python runtime across system..." -ForegroundColor Cyan
$pythonExe = $null

function Test-PythonCandidate($path) {
    if (-not $path) { return $false }
    if ($path -like "*\AppData\Local\Microsoft\WindowsApps\*") { return $false }
    if (-not (Test-Path $path)) { return $false }
    try {
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $path
        $psi.Arguments = '-c "import sys; print(''PYTHON_OK'')"'
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true
        $proc = [System.Diagnostics.Process]::Start($psi)
        $procOut = $proc.StandardOutput.ReadToEnd()
        $proc.WaitForExit(4000)
        if ($proc.ExitCode -eq 0 -and $procOut -match "PYTHON_OK") {
            return $true
        }
    } catch {}
    return $false
}

# 2.1 Check if local portable Python already exists in workspace
if (Test-PythonCandidate "$targetDir\python_env\python.exe") {
    $pythonExe = "$targetDir\python_env\python.exe"
}

# 2.2 Check py launcher
if (-not $pythonExe) {
    $pyCmd = (Get-Command py.exe -ErrorAction SilentlyContinue).Source
    if ($pyCmd -and (Test-PythonCandidate $pyCmd)) {
        $pythonExe = $pyCmd
    }
}

# 2.3 Check system PATH python.exe (strictly filtering out WindowsApps fake alias)
if (-not $pythonExe) {
    $allPython = Get-Command python.exe -All -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
    foreach ($p in $allPython) {
        if (Test-PythonCandidate $p) {
            $pythonExe = $p
            break
        }
    }
}

# 2.4 Scan common drive locations
if (-not $pythonExe) {
    $searchDrives = @("C:", "D:", "E:", "X:")
    foreach ($drive in $searchDrives) {
        if (Test-Path $drive) {
            $candidates = Get-ChildItem -Path "$drive\Users\*\AppData\Local\Programs\Python\Python*\python.exe", "$drive\Python*\python.exe", "$drive\Program Files\Python*\python.exe", "$drive\ProgramData\*\python.exe" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
            foreach ($c in $candidates) {
                if (Test-PythonCandidate $c) {
                    $pythonExe = $c
                    break
                }
            }
            if ($pythonExe) { break }
        }
    }
}

if ($pythonExe) {
    Write-Host "[✓] Found verified Python runtime: $pythonExe" -ForegroundColor Green
} else {
    Write-Host "[!] No functional Python runtime found on system." -ForegroundColor Yellow
    Write-Host "[*] Downloading lightweight portable Python runtime (~15MB)..." -ForegroundColor Cyan
    $portableUrl = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip"
    $zipPath = "$targetDir\python_portable.zip"
    $pyDir = "$targetDir\python_env"
    
    # 1. Extract embedded Python
    if (!(Test-Path $pyDir)) {
        New-Item -ItemType Directory -Path $pyDir -Force | Out-Null
    }
    Invoke-WebRequest -Uri $portableUrl -OutFile $zipPath -UseBasicParsing
    Expand-Archive -Path $zipPath -DestinationPath $pyDir -Force
    $pythonExe = "$pyDir\python.exe"

    # 2. Enable site-packages in embedded Python ._pth file
    Get-ChildItem -Path $pyDir -Filter "*._pth" | ForEach-Object {
        $pthLines = @(
            "python310.zip",
            ".",
            "Lib",
            "Lib\site-packages",
            "import site"
        )
        Set-Content $_.FullName ($pthLines -join "`r`n")
    }

    # 3. Create Lib and site-packages directories
    New-Item -ItemType Directory -Path "$pyDir\Lib\site-packages" -Force | Out-Null

    # 4. Bootstrap pip in embedded Python
    if (-not (Test-Path "$pyDir\Scripts\pip.exe")) {
        Write-Host "[*] Bootstrapping pip package manager for portable runtime..." -ForegroundColor DarkGray
        $getPipUrl = "https://bootstrap.pypa.io/get-pip.py"
        $getPipPath = "$pyDir\get-pip.py"
        Invoke-WebRequest -Uri $getPipUrl -OutFile $getPipPath -UseBasicParsing
        & $pythonExe $getPipPath --no-warn-script-location --quiet
    }

    Write-Host "[✓] Portable Python successfully configured: $pythonExe" -ForegroundColor Green
}

# 3. Download Latest Agent Source from GitHub Repository
Write-Host "[3/4] Fetching latest Autonomous OS Debugging Agent files from cloud..." -ForegroundColor Cyan

# Official repository raw content URL
$rawBase = "https://raw.githubusercontent.com/Ansh00031/Build-In-Bharat_NIT-Delhi/main"

$coreFiles = @(
    "agent.py",
    "core/__init__.py",
    "core/collector.py",
    "core/config.py",
    "core/executor.py",
    "core/llm.py",
    "core/remediation.py",
    "core/security.py",
    "core/snapshot.py",
    "core/system_paths.py",
    "core/reboot_manager.py",
    "core/autostart.py",
    "core/blockchain.py",
    "core/storage_cleaner.py",
    "core/web_threat_cleaner.py",
    "core/ui.py",
    "fix.bat"
)

# Create core directory
if (!(Test-Path "$targetDir\core")) {
    New-Item -ItemType Directory -Path "$targetDir\core" -Force | Out-Null
}

foreach ($f in $coreFiles) {
    $fileUrl = "$rawBase/$f"
    $dest = "$targetDir\$f"
    Write-Host "  -> Downloading: $f" -ForegroundColor DarkGray
    Invoke-WebRequest -Uri $fileUrl -OutFile $dest -UseBasicParsing -ErrorAction SilentlyContinue
}

# Install minimal CLI dependencies
Write-Host "`n[*] Installing required CLI dependencies..." -ForegroundColor Cyan
& $pythonExe -m pip install typer rich pydantic python-dotenv --break-system-packages --disable-pip-version-check --quiet

# 4. Install permanent 1-word 'fix' shortcut across user & system PATH
Write-Host "`n[4/4] ⚡ Registering permanent 1-word 'fix' emergency command..." -ForegroundColor Cyan
try {
    & $pythonExe "$targetDir\agent.py" install-shortcut | Out-Null
    if (Test-Path "$targetDir\fix.bat") {
        if ($env:USERPROFILE) { Copy-Item "$targetDir\fix.bat" "$env:USERPROFILE\fix.bat" -Force -ErrorAction SilentlyContinue }
        if ($env:LOCALAPPDATA) { Copy-Item "$targetDir\fix.bat" "$env:LOCALAPPDATA\Microsoft\WindowsApps\fix.bat" -Force -ErrorAction SilentlyContinue }
    }
} catch {}

# 5. Launch the Autonomous Diagnostic Agent
Write-Host "`n🚀 Launching Autonomous OS Debugging Agent..." -ForegroundColor Green
Write-Host "===============================================================================" -ForegroundColor Cyan

& $pythonExe "$targetDir\agent.py" startup-monitor

# Keep interactive shell ready
Write-Host @"

[✓] Agent and 'fix' shortcut are permanently installed in user files ($targetDir)!
You can now open ANY Command Prompt or PowerShell anytime and run:
    fix                                  <-- ⚡ 1-Word Emergency Shortcut (Interactive Menu)
    fix checkup                          <-- 🛡️ Full 4-Phase PC Security & Health Scan
    fix junk                             <-- 🧹 Scan and Clean Temporary Junk & Caches
    fix dups                             <-- 📑 Scan and Delete Duplicate Copies
    fix adware                           <-- 🛡️ Remove Malicious Web Notifications & Adware
    fix 0x80070005                       <-- 🔵 Diagnose specific error code
    fix rollback                         <-- 🛡️ 1-Click instant system rollback
==============================================================================="
"@ -ForegroundColor Yellow
