import httpx
import time
from .base_agent import BaseAgent

class SearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("SearchAgent", 0.002)

    async def execute(self, query: str) -> dict:
        self._record()
        start = time.time()

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    "https://api.duckduckgo.com/",
                    params={
                        "q": query,
                        "format": "json",
                        "no_html": "1"
                    }
                )
                response.raise_for_status()
                data = response.json()

                # Extract the main answer or related topics
                result_text = (
                    data.get("AbstractText") or
                    (data.get("RelatedTopics") and
                     len(data.get("RelatedTopics", [])) > 0 and
                     data.get("RelatedTopics")[0].get("Text", "")) or
                    f"No results found for: {query}"
                )

                if not result_text or result_text == "":
                    result_text = f"Search completed for: {query}"

        except Exception as e:
            result_text = f"Search error: {str(e)}"

        elapsed = (time.time() - start) * 1000

        return {
            "agent": self.name,
            "input": query,
            "output": result_text,
            "latency_ms": round(elapsed, 2)
        }
