import time, asyncio, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from agents import SearchAgent, ReviewAgent, SummaryAgent
from services.payment_service import PaymentService
from services.credential_validation import is_placeholder

class Coordinator:
    def __init__(self, payment_service: PaymentService):
        self.search  = SearchAgent()
        self.review  = ReviewAgent()
        self.summary = SummaryAgent()
        self.payment = payment_service
        self.name    = "Coordinator"

        # Secure credential loading with placeholder detection
        addr = os.getenv("WALLET_ADDR_COORDINATOR", "")
        self.address = addr if not is_placeholder(addr) else ""

        key = os.getenv("PRIVKEY_COORDINATOR", "")
        self.privkey = key if not is_placeholder(key) else ""

    def credentials_configured(self) -> bool:
        """Check if coordinator credentials are properly configured"""
        return bool(self.address and self.privkey and
                   len(self.address) > 10 and len(self.privkey) > 10)

    async def handle_request(self, query: str) -> dict:
        start = time.time()
        txs   = []
        for agent, resource in [
            (self.search,  f"/search?q={query}"),
            (self.review,  "/review"),
            (self.summary, "/summary"),
        ]:
            tx = await self.payment.pay(
                sender           = self.name,
                receiver         = agent.name,
                amount_usdc      = agent.cost,
                sender_address   = self.address or None,
                sender_privkey   = self.privkey or None,
                receiver_address = agent.wallet_address or None,
                resource         = resource,
            )
            txs.append(tx)

        r1 = await self.search.execute(query)
        r2 = await self.review.execute(r1["output"])
        r3 = await self.summary.execute(r2["output"])

        return {
            "query":           query,
            "final_output":    r3["output"],
            "steps":           [r1, r2, r3],
            "transactions":    txs,
            "total_cost_usdc": round(sum(t["amount"] for t in txs), 6),
            "latency_ms":      round((time.time() - start) * 1000, 1),
        }

    async def handle_batch(self, queries: list) -> dict:
        results = [await self.handle_request(q) for q in queries]
        return {
            "batch_size":      len(queries),
            "results":         results,
            "total_cost_usdc": round(sum(r["total_cost_usdc"] for r in results), 6),
        }
