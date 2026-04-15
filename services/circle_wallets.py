"""
Circle Developer-Controlled Wallets — create wallets per agent on Arc Testnet.
Docs: https://developers.circle.com/w3s/developer-controlled-create-your-first-wallet
REST API: https://api.circle.com/v1/w3s/developer/wallets

Setup:
  1. Create Circle account at https://console.circle.com
  2. Generate API key
  3. Generate Entity Secret (random 32-byte hex, encrypt with Circle's RSA public key)
  4. Call POST /setup/wallets to create one wallet per agent
  5. Fund from https://faucet.circle.com (select Arc Testnet)
"""
import os, uuid, httpx
from typing import Optional

CIRCLE_API_KEY                  = os.getenv("CIRCLE_API_KEY", "")
CIRCLE_ENTITY_SECRET_CIPHERTEXT = os.getenv("CIRCLE_ENTITY_SECRET_CIPHERTEXT", "")
BASE_URL                        = "https://api.circle.com/v1/w3s"
BLOCKCHAIN                      = os.getenv("CIRCLE_BLOCKCHAIN", "ARC-TESTNET")
USDC_TOKEN_ID                   = os.getenv("CIRCLE_USDC_TOKEN_ID", "USDC-ARC-TESTNET")


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {CIRCLE_API_KEY}",
        "Content-Type":  "application/json",
    }


async def create_wallet_set(name: str = "AgentPayMesh") -> dict:
    """Create a WalletSet — a parent group for all agent wallets."""
    async with httpx.AsyncClient() as c:
        r = await c.post(
            f"{BASE_URL}/developer/walletSets",
            headers=_headers(),
            json={"idempotencyKey": str(uuid.uuid4()), "name": name},
        )
        r.raise_for_status()
        return r.json()["data"]["walletSet"]


async def create_wallet(wallet_set_id: str, label: str = "AgentWallet") -> dict:
    """
    Create a single EOA developer-controlled wallet on Arc Testnet.
    Returns: {"id": "...", "address": "0x...", "blockchain": "ARC-TESTNET", ...}
    """
    async with httpx.AsyncClient() as c:
        r = await c.post(
            f"{BASE_URL}/developer/wallets",
            headers=_headers(),
            json={
                "idempotencyKey":          str(uuid.uuid4()),
                "blockchains":             [BLOCKCHAIN],
                "count":                   1,
                "walletSetId":             wallet_set_id,
                "entitySecretCiphertext":  CIRCLE_ENTITY_SECRET_CIPHERTEXT,
                "metadata":                [{"name": label, "refId": label}],
            },
        )
        r.raise_for_status()
        return r.json()["data"]["wallets"][0]


async def get_wallet_balance(wallet_id: str) -> list:
    """Return USDC (and other token) balances for a wallet."""
    async with httpx.AsyncClient() as c:
        r = await c.get(
            f"{BASE_URL}/wallets/{wallet_id}/balances",
            headers=_headers(),
        )
        r.raise_for_status()
        return r.json()["data"].get("tokenBalances", [])


async def transfer_usdc(
    from_wallet_id: str,
    to_address:     str,
    amount:         str,              # e.g. "0.002"
    idempotency_key: Optional[str] = None,
) -> dict:
    """
    Transfer USDC from a Circle-managed wallet to any address on Arc.
    Circle's Gas Station covers the Arc gas fees.
    """
    async with httpx.AsyncClient() as c:
        r = await c.post(
            f"{BASE_URL}/developer/transactions/transfer",
            headers=_headers(),
            json={
                "idempotencyKey":         idempotency_key or str(uuid.uuid4()),
                "walletId":               from_wallet_id,
                "tokenId":                USDC_TOKEN_ID,
                "destinationAddress":     to_address,
                "amounts":                [amount],
                "entitySecretCiphertext": CIRCLE_ENTITY_SECRET_CIPHERTEXT,
                "fee": {"type": "level", "config": {"feeLevel": "MEDIUM"}},
            },
        )
        r.raise_for_status()
        return r.json()["data"]["transaction"]


async def get_transaction(transaction_id: str) -> dict:
    """Poll a transfer transaction for its final status."""
    async with httpx.AsyncClient() as c:
        r = await c.get(
            f"{BASE_URL}/transactions/{transaction_id}",
            headers=_headers(),
        )
        r.raise_for_status()
        return r.json()["data"]["transaction"]
