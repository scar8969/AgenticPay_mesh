import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.credential_validation import is_placeholder

class BaseAgent:
    def __init__(self, name: str, cost_per_call: float):
        self.name         = name
        self.cost         = cost_per_call
        self.calls        = 0
        self.total_earned = 0.0

        # Secure credential loading with placeholder detection
        addr = os.getenv(f"WALLET_ADDR_{name.upper()}", "")
        self.wallet_address = addr if not is_placeholder(addr) else ""

        key = os.getenv(f"PRIVKEY_{name.upper()}", "")
        self.private_key = key if not is_placeholder(key) else ""

    def execute(self, task_input: str) -> dict:
        raise NotImplementedError

    def _record(self):
        self.calls += 1
        self.total_earned += self.cost

    def credentials_configured(self) -> bool:
        """Check if both wallet address and private key are properly configured"""
        return bool(self.wallet_address and self.private_key and
                   len(self.wallet_address) > 10 and len(self.private_key) > 10)

    def stats(self) -> dict:
        """Return agent statistics without exposing sensitive data"""
        return {
            "agent": self.name,
            "calls": self.calls,
            "total_earned": round(self.total_earned, 6),
            "wallet_configured": self.credentials_configured(),
            "wallet_length": len(self.wallet_address) if self.wallet_address else 0
        }
