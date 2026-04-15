import os
import time
import asyncio
from .base_agent import BaseAgent

try:
    from anthropic import AsyncAnthropic
except ImportError:
    AsyncAnthropic = None

class SummaryAgent(BaseAgent):
    def __init__(self):
        super().__init__("SummaryAgent", 0.001)
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.client = AsyncAnthropic(api_key=self.api_key) if AsyncAnthropic and self.api_key else None

    async def execute(self, data: str) -> dict:
        self._record()
        start = time.time()

        if self.client:
            try:
                message = await self.client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=100,
                    messages=[
                        {"role": "user", "content": f"Summarize this analysis into one actionable recommendation in 2 sentences: {data}"}
                    ]
                )
                result_text = message.content[0].text
            except Exception as e:
                result_text = f"Summary error: {str(e)}"
        else:
            result_text = "[Summary] Best value: Product A at $349."

        elapsed = (time.time() - start) * 1000

        return {
            "agent": self.name,
            "input": data,
            "output": result_text,
            "latency_ms": round(elapsed, 2)
        }
