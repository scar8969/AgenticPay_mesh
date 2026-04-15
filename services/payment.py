import uuid, time

class PaymentService:
    """
    Mock USDC payment service.
    To use real payments, replace the pay() body with:
      - Circle Nanopayments API
      - x402 payment request + verification
      - Arc USDC settlement -> return tx hash
    """
    def __init__(self):
        self.transactions = []

    def pay(self, sender: str, receiver: str, amount: float) -> dict:
        tx = {
            "id": str(uuid.uuid4()),
            "from": sender,
            "to": receiver,
            "amount": amount,
            "currency": "USDC",
            "timestamp": time.time(),
            "status": "confirmed",
            "chain": "Arc (mock)"
        }
        self.transactions.append(tx)
        print(f"[PAY] {sender} -> {receiver}: ${amount:.4f} USDC  tx={tx['id'][:8]}")
        return tx

    def get_all(self):
        return self.transactions

    def get_total(self):
        return round(sum(t["amount"] for t in self.transactions), 6)

    def get_stats(self):
        agg = {}
        for t in self.transactions:
            agg[t["to"]] = agg.get(t["to"], 0) + t["amount"]
        return {
            "total_transactions": len(self.transactions),
            "total_paid_usdc": self.get_total(),
            "by_receiver": {k: round(v, 6) for k, v in agg.items()}
        }
