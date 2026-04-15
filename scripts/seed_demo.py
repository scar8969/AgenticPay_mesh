#!/usr/bin/env python3
"""
Seed Demo Script
Fires 5 sequential queries with 200ms delay between each.
Displays a live table of: query | agents called | tx count | total cost
"""
import asyncio
import httpx
import time
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def format_table_row(query: str, agents: int, tx_count: int, cost: float) -> str:
    """Format a single row of the results table."""
    return f"{query[:40]:<40} | {agents:>3} agents | {tx_count:>3} txs | ${cost:>8.6f}"


def print_header():
    """Print the table header."""
    print("\n" + "=" * 80)
    print(f"{'QUERY':<40} | {'AGENTS':>8} | {'TXS':>4} | {'COST':>10}")
    print("=" * 80)


def print_footer(total_queries: int, total_txs: int, total_cost: float, elapsed: float):
    """Print the summary footer."""
    print("=" * 80)
    print(f"TOTAL: {total_queries} queries | {total_txs} transactions | ${total_cost:.6f} USDC | {elapsed:.2f}s")
    print("=" * 80 + "\n")


async def fire_query(client: httpx.AsyncClient, query: str, index: int) -> dict:
    """Fire a single query and return the result."""
    start = time.time()
    try:
        response = await client.get(f"http://localhost:8000/query?q={query}")
        response.raise_for_status()
        result = response.json()
        elapsed = time.time() - start

        return {
            "index": index,
            "query": query,
            "success": True,
            "agents_called": len(result.get("steps", [])),
            "tx_count": len(result.get("transactions", [])),
            "cost": result.get("total_cost_usdc", 0.0),
            "latency": elapsed,
            "result": result
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "index": index,
            "query": query,
            "success": False,
            "error": str(e),
            "latency": elapsed
        }


async def main():
    """Main demo function."""
    print("\n🚀 AgentPay Mesh - Seed Demo Script")
    print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Define test queries
    queries = [
        "best mechanical keyboard under $100",
        "top noise-canceling headphones 2024",
        "affordable gaming laptop recommendations",
        "best wireless mouse for productivity",
        "portable SSD with best value"
    ]

    print(f"\n📋 Will fire {len(queries)} sequential queries with 200ms delay between each")
    print("Make sure the backend is running: python run.py\n")

    # Wait a moment for user to see the message
    await asyncio.sleep(2)

    print_header()

    total_txs = 0
    total_cost = 0.0
    start_time = time.time()

    async with httpx.AsyncClient(timeout=30) as client:
        for i, query in enumerate(queries, 1):
            result = await fire_query(client, query, i)

            if result["success"]:
                # Update totals
                total_txs += result["tx_count"]
                total_cost += result["cost"]

                # Print row
                print(f"[{i:02d}] {format_table_row(result['query'], result['agents_called'], result['tx_count'], result['cost'])}")

                # Print additional info
                if result["result"].get("final_output"):
                    print(f"     → {result['result']['final_output'][:60]}...")
            else:
                print(f"[{i:02d}] ERROR: {result.get('error', 'Unknown error')}")

            # Delay between queries (except for the last one)
            if i < len(queries):
                await asyncio.sleep(0.2)

    elapsed = time.time() - start_time
    print_footer(len(queries), total_txs, total_cost, elapsed)

    print(f"✅ Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Transaction rate: {total_txs/elapsed:.2f} tx/second")
    print(f"💰 Average cost per transaction: ${total_cost/total_txs:.6f} USDC")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)