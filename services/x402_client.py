"""
x402 HTTP-native payment client.
Standard: https://x402.org | github.com/coinbase/x402

x402 flow (3 steps):
  1. GET /resource → HTTP 402 with JSON body describing price + payment address
  2. Client signs EIP-3009 auth → includes as X-PAYMENT header
  3. Server forwards to facilitator → verifies + settles → returns resource

Useful for paying x402-enabled data APIs (weather, DeFi yields, risk scores, etc.)
that the hackathon has exposed via Circle Nanopayments.
"""
import os, time, uuid, json, httpx
from web3 import Web3
from eth_account import Account

X402_FACILITATOR_URL = os.getenv("X402_FACILITATOR_URL",
                                   "https://facilitator.chaoscha.in")
USDC_CONTRACT_ARC    = os.getenv("USDC_CONTRACT_ARC", "0x_FILL_FROM_ARC_DOCS")
CHAIN_ID             = int(os.getenv("ARC_CHAIN_ID", "480"))


def sign_x402_payment(
    payer_address: str,
    private_key:   str,
    pay_to:        str,
    amount_atomic: int,     # USDC in 6-decimal units, e.g. 2000 = $0.002
    resource:      str,
) -> dict:
    """Build a signed x402 payment payload using EIP-3009."""
    valid_after  = int(time.time()) - 30
    valid_before = int(time.time()) + 300   # 5-minute window
    nonce        = Web3.to_hex(uuid.uuid4().bytes)

    structured = {
        "domain": {
            "name": "USD Coin", "version": "2",
            "chainId": CHAIN_ID, "verifyingContract": USDC_CONTRACT_ARC,
        },
        "message": {
            "from": payer_address, "to": pay_to,
            "value": amount_atomic,
            "validAfter": valid_after, "validBefore": valid_before, "nonce": nonce,
        },
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"}, {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"}, {"name": "verifyingContract", "type": "address"},
            ],
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"}, {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"}, {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"}, {"name": "nonce", "type": "bytes32"},
            ],
        },
        "primaryType": "TransferWithAuthorization",
    }
    signed = Account.from_key(private_key).sign_typed_data(structured)
    return {
        "x402Version": 1,
        "scheme":      "exact",
        "network":     f"eip155:{CHAIN_ID}",
        "payload": {
            "signature": signed.signature.hex(),
            "authorization": {
                "from": payer_address, "to": pay_to, "value": str(amount_atomic),
                "validAfter": str(valid_after), "validBefore": str(valid_before),
                "nonce": nonce,
            },
        },
        "resource": resource,
    }


async def x402_fetch(
    url:            str,
    payer_address:  str,
    private_key:    str,
    method:         str  = "GET",
    body:           dict = None,
    verify_first:   bool = True,
) -> dict:
    """
    Fetch any x402-protected resource, automatically handling the
    402 Payment Required challenge-response cycle.

    Example:
        result = await x402_fetch(
            "https://api.example.com/defi-yields",
            payer_address=coordinator_wallet,
            private_key=coordinator_privkey,
        )
        data = result["data"]
        cost = result["amount_usdc"]
    """
    async with httpx.AsyncClient(timeout=30) as client:
        # Step 1: Initial request — expect 402 or immediate success
        r = await client.request(method, url, json=body)

        if r.status_code != 402:
            return {"status": r.status_code, "data": r.json(), "amount_usdc": 0.0}

        # Step 2: Parse payment requirements from 402 response body
        payment_req  = r.json()
        accepts      = payment_req.get("accepts", [{}])[0]
        pay_to       = accepts.get("payTo", "")
        max_amount   = int(accepts.get("maxAmountRequired", "0"))
        resource     = payment_req.get("resource", url)

        # Step 3: Sign payment
        payment_payload = sign_x402_payment(
            payer_address, private_key, pay_to, max_amount, resource
        )

        # Step 4: (Optional) Verify with facilitator before sending
        if verify_first:
            vr = await client.post(
                f"{X402_FACILITATOR_URL}/verify",
                json={
                    "x402Version":        1,
                    "paymentHeader":      payment_payload["payload"]["authorization"],
                    "paymentRequirements": accepts,
                },
            )
            if vr.status_code == 200 and not vr.json().get("isValid", True):
                raise ValueError(f"x402 facilitator rejected payment: {vr.json()}")

        # Step 5: Retry with X-PAYMENT header
        retry = await client.request(
            method, url, json=body,
            headers={
                "X-PAYMENT":     json.dumps(payment_payload),
                "X-402-Version": "1",
            },
        )
        return {
            "status":     retry.status_code,
            "data":       retry.json(),
            "payment":    payment_payload,
            "amount_usdc": max_amount / 1_000_000,
            "paid_to":    pay_to,
        }
