from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import sys
import os
import time
import asyncio
import json
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from coordinator import Coordinator
from services.payment_service import PaymentService
from services.circle_wallets  import create_wallet_set, create_wallet, get_wallet_balance
from services.x402_client import x402_fetch

app = FastAPI(title="AgentPay Mesh", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

payment_service = PaymentService()
coordinator     = Coordinator(payment_service)

# SSE queue for live transactions
_transaction_queue = asyncio.Queue()

class QueryRequest(BaseModel):
    query: str

class BatchRequest(BaseModel):
    queries: List[str]

class X402Request(BaseModel):
    url: str
    query: str = ""

@app.get("/")
def root():
    return {"status": "AgentPay Mesh v2 running",
            "stack": ["Arc", "USDC", "Circle Wallets", "Nanopayments", "x402"],
            "docs":  "/docs"}

@app.get("/health")
async def health():
    """Enhanced health check with credential status, API connectivity, and system readiness."""

    # Basic system info
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "uptime": "active",  # Could add actual uptime tracking
        "tx_count": len(payment_service.transactions),
        "total_paid_usdc": payment_service.get_total()
    }

    # Credential status
    credentials = {
        "circle_api_key": _check_credential_configured('CIRCLE_API_KEY', 'your_circle_api_key_here'),
        "circle_entity_secret": _check_credential_configured('CIRCLE_ENTITY_SECRET_CIPHERTEXT', 'your_encrypted_entity_secret_here'),
        "anthropic_api_key": _check_credential_configured('ANTHROPIC_API_KEY', 'your_anthropic_api_key'),
    }

    # Wallet configuration
    agent_wallets = {}
    for agent_name in ['COORDINATOR', 'SEARCHAGENT', 'REVIEWAGENT', 'SUMMARYAGENT']:
        addr_key = f'WALLET_ADDR_{agent_name}'
        key_key = f'PRIVKEY_{agent_name}'

        addr = os.getenv(addr_key, '')
        privkey = os.getenv(key_key, '')

        agent_wallets[agent_name.lower()] = {
            "address_configured": bool(addr and addr != '0x...' and len(addr) > 10),
            "privkey_configured": bool(privkey and privkey != '0x...' and len(privkey) > 10)
        }

    # System mode determination
    credentials_configured = sum(1 for v in credentials.values() if v['configured'])
    wallets_configured = sum(1 for w in agent_wallets.values() if w['address_configured'] and w['privkey_configured'])

    if credentials_configured == 2 and wallets_configured == 4:
        system_mode = "real"
        mode_description = "Full nanopayments and AI capabilities"
    elif credentials_configured > 0 or wallets_configured > 0:
        system_mode = "hybrid"
        mode_description = "Partial capabilities with some mock fallbacks"
    else:
        system_mode = "mock"
        mode_description = "Demo mode with simulated payments and responses"

    # Service configuration
    services = {
        "nanopayments": {
            "enabled": os.getenv('USE_NANOPAYMENTS', 'false').lower() == 'true',
            "api_url": os.getenv('CIRCLE_NANOPAY_URL', 'https://api.circle.com/v1/w3s/nanopayments')
        },
        "blockchain": {
            "chain": os.getenv('CIRCLE_BLOCKCHAIN', 'ARC-TESTNET'),
            "chain_id": os.getenv('ARC_CHAIN_ID', '480'),
            "rpc_url": os.getenv('ARC_RPC_URL', 'https://rpc.arc-testnet.circle.com'),
            "usdc_contract": os.getenv('USDC_CONTRACT_ARC', 'not configured')
        },
        "x402": {
            "facilitator_url": os.getenv('X402_FACILITATOR_URL', 'not configured')
        }
    }

    # Agent status
    agents = []
    for agent in [coordinator.search, coordinator.review, coordinator.summary]:
        agents.append({
            "name": agent.name,
            "calls": agent.calls,
            "total_earned": agent.total_earned,
            "cost_per_call": agent.cost,
            "wallet_configured": bool(agent.wallet_address and len(agent.wallet_address) > 10)
        })

    # Compile comprehensive health status
    health_status.update({
        "system_mode": system_mode,
        "mode_description": mode_description,
        "credentials": credentials,
        "agent_wallets": agent_wallets,
        "services": services,
        "agents": agents,
        "configuration_complete": credentials_configured == 2 and wallets_configured == 4
    })

    return health_status

def _check_credential_configured(env_var: str, placeholder: str) -> dict:
    """Helper function to check if a credential is properly configured without exposing values"""
    value = os.getenv(env_var, '')
    configured = bool(value and value not in ['your_circle_api_key_here',
                                               'your_encrypted_entity_secret_here',
                                               'your_anthropic_api_key',
                                               '0x...'] and len(value) > 5)

    return {
        "configured": configured,
        "length": len(value) if configured else 0
    }

@app.post("/query")
async def run_query(req: QueryRequest):
    result = await coordinator.handle_request(req.query)
    # Notify SSE subscribers
    for tx in result.get("transactions", []):
        await _transaction_queue.put(tx)
    return result

@app.get("/query")
async def run_query_get(q: str):
    result = await coordinator.handle_request(q)
    # Notify SSE subscribers
    for tx in result.get("transactions", []):
        await _transaction_queue.put(tx)
    return result

@app.post("/batch")
async def run_batch(req: BatchRequest):
    result = await coordinator.handle_batch(req.queries)
    # Notify SSE subscribers
    for res in result.get("results", []):
        for tx in res.get("transactions", []):
            await _transaction_queue.put(tx)
    return result

@app.get("/batch/demo")
async def demo():
    """25 queries → 75 Nanopayments on Arc. Use this for the judge demo."""
    queries = [f"best laptop under ${300 + i*20}" for i in range(25)]
    result = await coordinator.handle_batch(queries)
    # Notify SSE subscribers
    for res in result.get("results", []):
        for tx in res.get("transactions", []):
            await _transaction_queue.put(tx)
    return result

@app.get("/transactions")
def get_txs():
    return payment_service.get_all()

@app.get("/transactions/live")
async def transactions_live():
    """SSE endpoint for live transaction feed."""
    async def event_generator():
        try:
            while True:
                # Wait for new transactions
                tx = await _transaction_queue.get()
                # Send SSE event
                yield f"data: {json.dumps(tx)}\n\n"
        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@app.get("/agents")
def get_agents():
    """Get list of all agents with stats and wallet addresses."""
    return [
        {
            **coordinator.search.stats(),
            "cost_per_call": coordinator.search.cost,
            "wallet_address": coordinator.search.wallet_address
        },
        {
            **coordinator.review.stats(),
            "cost_per_call": coordinator.review.cost,
            "wallet_address": coordinator.review.wallet_address
        },
        {
            **coordinator.summary.stats(),
            "cost_per_call": coordinator.summary.cost,
            "wallet_address": coordinator.summary.wallet_address
        }
    ]

@app.post("/x402/fetch")
async def x402_fetch_endpoint(req: X402Request):
    """Fetch data from x402-enabled API."""
    try:
        # Use coordinator's credentials
        result = await x402_fetch(
            url=req.url,
            payer_address=coordinator.address,
            private_key=coordinator.privkey
        )
        return result
    except Exception as e:
        return {"error": str(e), "status": "failed"}

@app.get("/stats")
def stats():
    s = payment_service.get_stats()
    s["agents"] = [
        {
            **coordinator.search.stats(),
            "cost_per_call": coordinator.search.cost
        },
        {
            **coordinator.review.stats(),
            "cost_per_call": coordinator.review.cost
        },
        {
            **coordinator.summary.stats(),
            "cost_per_call": coordinator.summary.cost
        }
    ]
    return s

@app.delete("/reset")
def reset():
    payment_service.transactions.clear()
    for a in [coordinator.search, coordinator.review, coordinator.summary]:
        a.calls = 0; a.total_earned = 0.0
    return {"status": "reset"}

@app.post("/setup/wallets")
async def setup_wallets():
    """One-time: create Circle wallets for each agent on Arc Testnet."""
    ws   = await create_wallet_set("AgentPayMesh")
    wsid = ws["id"]
    out  = {}
    for name in ["Coordinator", "SearchAgent", "ReviewAgent", "SummaryAgent"]:
        w = await create_wallet(wsid, name)
        out[name] = {"walletId": w["id"], "address": w["address"]}
    return {"walletSet": wsid, "wallets": out,
            "fundAt": "https://faucet.circle.com  (select Arc Testnet)"}

@app.get("/wallets/{wallet_id}/balance")
async def balance(wallet_id: str):
    return await get_wallet_balance(wallet_id)
