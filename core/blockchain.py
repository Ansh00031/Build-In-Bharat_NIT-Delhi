"""Algorand TestNet integration and AlgoKit Lora Explorer anchor engine.

Provides cryptographic on-chain audit trails for OS diagnostic and remediation sessions.
Explorer URL: https://lora.algokit.io/testnet
"""

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Try importing algosdk or auto-install if missing
try:
    import algosdk
    from algosdk import account, mnemonic
    from algosdk.transaction import PaymentTxn, SuggestedParams
    from algosdk.v2client import algod
except ImportError:
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "py-algorand-sdk", "--disable-pip-version-check", "--quiet"]
        )
        import algosdk
        from algosdk import account, mnemonic
        from algosdk.transaction import PaymentTxn, SuggestedParams
        from algosdk.v2client import algod
    except Exception:
        algosdk = None

# Free public Algorand TestNet Algod endpoint (no API key needed)
DEFAULT_ALGOD_SERVER = "https://testnet-api.algonode.cloud"
DEFAULT_ALGOD_PORT = 443
DEFAULT_ALGOD_TOKEN = ""

LORA_BASE_URL = "https://lora.algokit.io/testnet"
FAUCET_URL = "https://bank.testnet.algorand.network"


def get_algod_client(server: str = DEFAULT_ALGOD_SERVER) -> Optional[Any]:
    """Get an Algod client connected to Algorand TestNet."""
    if algosdk is None:
        return None
    try:
        return algod.AlgodClient(DEFAULT_ALGOD_TOKEN, server, headers={"User-Agent": "AutonomousOSDebugAgent/1.0"})
    except Exception:
        return None


def get_or_create_wallet() -> Tuple[str, str, bool]:
    """Retrieve existing Algorand TestNet wallet from .env / .backups/wallet.json, or create a new one.

    Returns:
        Tuple[str, str, bool]: (address, mnemonic_phrase, is_newly_created)
    """
    from core.snapshot import get_backups_dir

    backups_dir = get_backups_dir()
    wallet_file = backups_dir / "algorand_wallet.json"

    # Check environment variable first
    env_mnemonic = os.getenv("ALGORAND_MNEMONIC", "").strip()
    if env_mnemonic and algosdk:
        try:
            sk = mnemonic.to_private_key(env_mnemonic)
            addr = account.address_from_private_key(sk)
            return addr, env_mnemonic, False
        except Exception:
            pass

    # Check local saved wallet file
    if wallet_file.exists():
        try:
            data = json.loads(wallet_file.read_text(encoding="utf-8"))
            if data.get("address") and data.get("mnemonic"):
                return data["address"], data["mnemonic"], False
        except Exception:
            pass

    # Generate new account
    if algosdk is None:
        return "ALGORAND_SDK_NOT_AVAILABLE", "", False

    private_key, address = account.generate_account()
    passphrase = mnemonic.from_private_key(private_key)

    # Save locally to .backups
    backups_dir.mkdir(parents=True, exist_ok=True)
    wallet_payload = {
        "address": address,
        "mnemonic": passphrase,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "network": "testnet",
        "explorer": f"{LORA_BASE_URL}/account/{address}",
    }
    wallet_file.write_text(json.dumps(wallet_payload, indent=2), encoding="utf-8")

    return address, passphrase, True


def get_wallet_balance(address: str) -> Dict[str, Any]:
    """Query account balance on Algorand TestNet."""
    client = get_algod_client()
    if not client or not address or address == "ALGORAND_SDK_NOT_AVAILABLE":
        return {"balance_algo": 0.0, "microalgos": 0, "status": "CLIENT_UNAVAILABLE"}

    try:
        account_info = client.account_info(address)
        microalgos = account_info.get("amount", 0)
        algo_balance = microalgos / 1_000_000.0
        return {
            "balance_algo": algo_balance,
            "microalgos": microalgos,
            "status": "ONLINE",
            "min_balance": account_info.get("min-balance", 100_000) / 1_000_000.0,
        }
    except Exception as ex:
        return {"balance_algo": 0.0, "microalgos": 0, "status": f"ERROR: {str(ex)}"}


def compute_session_hash(session_id: str) -> str:
    """Compute a SHA-256 cryptographic digest of a session's metadata and fix script."""
    from core.snapshot import get_backups_dir

    session_dir = get_backups_dir() / session_id
    hasher = hashlib.sha256()

    if session_dir.exists():
        for file_name in ["metadata.json", "fix.ps1", "rollback.ps1"]:
            fpath = session_dir / file_name
            if fpath.exists():
                hasher.update(fpath.read_bytes())
    else:
        hasher.update(session_id.encode("utf-8"))

    return hasher.hexdigest()


def anchor_session_on_chain(
    session_id: str,
    error_code: str,
    status: str = "VERIFIED_SUCCESS",
    fix_title: str = "Automated Remediation",
) -> Dict[str, Any]:
    """Commit a cryptographic proof of the OS repair session to Algorand TestNet.

    Returns:
        Dict[str, Any]: Transaction result containing tx_id, lora_url, and note payload.
    """
    client = get_algod_client()
    if not client:
        return {
            "success": False,
            "error": "Algorand SDK / Algod client is not available.",
        }

    address, passphrase, _ = get_or_create_wallet()
    if not passphrase:
        return {
            "success": False,
            "error": "No Algorand TestNet wallet configured. Run 'python agent.py blockchain setup'.",
        }

    # Check balance
    balance_info = get_wallet_balance(address)
    if balance_info.get("microalgos", 0) < 1000:
        return {
            "success": False,
            "error": "Insufficient TestNet ALGO for transaction fee (min 0.001 ALGO required).",
            "address": address,
            "faucet_url": FAUCET_URL,
            "lora_account_url": f"{LORA_BASE_URL}/account/{address}",
        }

    try:
        private_key = mnemonic.to_private_key(passphrase)
        digest = compute_session_hash(session_id)

        # Build Structured Immutable Audit Note
        audit_note = {
            "standard": "arc-0002",
            "app": "AutonomousOSDebugAgent",
            "version": "1.0.0",
            "session_id": session_id,
            "error_code": error_code,
            "status": status,
            "fix_title": fix_title[:50],
            "sha256": digest,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        note_bytes = json.dumps(audit_note, separators=(",", ":")).encode("utf-8")

        # Get suggested network parameters
        params: SuggestedParams = client.suggested_params()

        # Build zero-ALGO self-transaction with the note
        txn = PaymentTxn(
            sender=address,
            sp=params,
            receiver=address,
            amt=0,
            note=note_bytes,
        )

        # Sign transaction
        signed_txn = txn.sign(private_key)

        # Broadcast to Algorand TestNet
        tx_id = client.send_transaction(signed_txn)

        # Wait for confirmation (usually 1 block ~3.3 seconds)
        confirmed_txn = wait_for_confirmation(client, tx_id, max_rounds=5)

        lora_tx_url = f"{LORA_BASE_URL}/transaction/{tx_id}"
        lora_account_url = f"{LORA_BASE_URL}/account/{address}"

        # Record blockchain receipt in session folder
        from core.snapshot import get_backups_dir
        session_dir = get_backups_dir() / session_id
        if session_dir.exists():
            receipt = {
                "tx_id": tx_id,
                "confirmed_round": confirmed_txn.get("confirmed-round"),
                "lora_url": lora_tx_url,
                "sender": address,
                "audit_note": audit_note,
                "anchored_at": datetime.now(timezone.utc).isoformat(),
            }
            (session_dir / "blockchain_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")

        return {
            "success": True,
            "tx_id": tx_id,
            "confirmed_round": confirmed_txn.get("confirmed-round"),
            "lora_tx_url": lora_tx_url,
            "lora_account_url": lora_account_url,
            "address": address,
            "sha256": digest,
            "audit_note": audit_note,
        }

    except Exception as ex:
        return {
            "success": False,
            "error": str(ex),
            "address": address,
            "lora_account_url": f"{LORA_BASE_URL}/account/{address}",
        }


def wait_for_confirmation(client: Any, tx_id: str, max_rounds: int = 5) -> Dict[str, Any]:
    """Wait until transaction is confirmed by Algorand TestNet consensus."""
    status = client.status()
    last_round = status.get("last-round")
    current_round = last_round

    while current_round < last_round + max_rounds:
        try:
            pending_info = client.pending_transaction_info(tx_id)
            if pending_info.get("confirmed-round", 0) > 0:
                return pending_info
        except Exception:
            pass
        time.sleep(1)
        status = client.status()
        current_round = status.get("last-round")

    return client.pending_transaction_info(tx_id)
