"""
Circle Nanopayments — gas-free USDC sub-cent transfers on Arc.
Docs: https://developers.circle.com/cctp/nanopayments

How it works:
  1. Agent signs an EIP-3009 TransferWithAuthorization message (entirely off-chain)
  2. POST signed payload to Circle Nanopayments API
  3. API validates signature, updates internal ledger instantly
  4. Merchant gets immediate confirmation → releases service
  5. Circle batches thousands of txs → settles on Arc periodically (zero gas for you)

Key numbers:
  Minimum transfer:  $0.000001 USDC
  Gas cost to you:   $0.00 (Circle absorbs batch settlement gas)
  Confirmation time: ~instant (ledger) / periodic (Arc on-chain)
"""
import os, time, uuid, httpx
from web3 import Web3
from eth_account import Account

CIRCLE_API_KEY    = os.getenv("CIRCLE_API_KEY", "")
NANOPAY_BASE      = os.getenv("CIRCLE_NANOPAY_URL",
                               "https://api.circle.com/v1/w3s/nanopayments")
USDC_CONTRACT_ARC = os.getenv("USDC_CONTRACT_ARC", "0x_FILL_FROM_ARC_DOCS")
CHAIN_ID          = int(os.getenv("ARC_CHAIN_ID", "480"))   # Arc Testnet


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {CIRCLE_API_KEY}",
        "Content-Type":  "application/json",
    }


def build_eip3009_signature(
    from_address: str,
    to_address:   str,
    value_usdc:   float,    # human-readable, e.g. 0.002
    private_key:  str,
) -> dict:
    """
    Sign an EIP-3009 TransferWithAuthorization for Nanopayments.
    USDC uses 6 decimal places on Arc.
    """
    value_atomic = int(value_usdc * 1_000_000)   # convert to micro-USDC
    valid_after  = int(time.time()) - 60
    valid_before = int(time.time()) + 3600
    nonce        = Web3.to_hex(uuid.uuid4().bytes)

    structured_data = {
        "domain": {
            "name":              "USD Coin",
            "version":           "2",
            "chainId":           CHAIN_ID,
            "verifyingContract": USDC_CONTRACT_ARC,
        },
        "message": {
            "from":        from_address,
            "to":          to_address,
            "value":       value_atomic,
            "validAfter":  valid_after,
            "validBefore": valid_before,
            "nonce":       nonce,
        },
        "types": {
            "EIP712Domain": [
                {"name": "name",              "type": "string"},
                {"name": "version",           "type": "string"},
                {"name": "chainId",           "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "TransferWithAuthorization": [
                {"name": "from",        "type": "address"},
                {"name": "to",          "type": "address"},
                {"name": "value",       "type": "uint256"},
                {"name": "validAfter",  "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce",       "type": "bytes32"},
            ],
        },
        "primaryType": "TransferWithAuthorization",
    }

    account = Account.from_key(private_key)
    signed  = account.sign_typed_data(structured_data)

    return {
        "from":        from_address,
        "to":          to_address,
        "value":       str(value_atomic),
        "validAfter":  str(valid_after),
        "validBefore": str(valid_before),
        "nonce":       nonce,
        "v":           signed.v,
        "r":           Web3.to_hex(signed.r),
        "s":           Web3.to_hex(signed.s),
    }


async def nanopay(
    from_address: str,
    to_address:   str,
    amount_usdc:  float,
    private_key:  str,
    resource_url: str = "",
) -> dict:
    """
    Submit a Nanopayment to Circle's API.
    Returns instant ledger confirmation. On-chain settlement is async.
    """
    authorization = build_eip3009_signature(
        from_address, to_address, amount_usdc, private_key
    )

    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(
            f"{NANOPAY_BASE}/transfers",
            headers=_headers(),
            json={
                "idempotencyKey": str(uuid.uuid4()),
                "chain":          f"eip155:{CHAIN_ID}",   # e.g. "eip155:480"
                "authorization":  authorization,
                "metadata": {
                    "resource":    resource_url,
                    "amount_usdc": str(amount_usdc),
                },
            },
        )
        r.raise_for_status()
        return r.json()["data"]


async def get_nanopay_balance(address: str) -> dict:
    """Query the off-chain Nanopayments ledger balance for an address."""
    async with httpx.AsyncClient() as c:
        r = await c.get(
            f"{NANOPAY_BASE}/balances/{address}",
            headers=_headers(),
        )
        r.raise_for_status()
        return r.json()["data"]
