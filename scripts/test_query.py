"""
test_query.py — Test the RAG pipeline from the command line without starting the API.

Usage:
  python scripts/test_query.py "I can't stop procrastinating on my project"
  python scripts/test_query.py  # interactive mode
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.agent.graph import run_coach


SAMPLE_QUERIES = [
    "I keep procrastinating on my most important work",
    "I feel completely lost and don't know what to do with my life",
    "I can't focus for more than 5 minutes without checking my phone",
    "I keep making impulsive financial decisions I regret",
    "I'm afraid to start my business because I might fail",
    "I react with anger and regret it every time",
]


async def test_query(message: str):
    print(f"\n{'='*60}")
    print(f"Query: {message}")
    print("=" * 60)

    result = await run_coach(message)

    print(f"\n📌 Problem Detected: {result.get('problem_detected', 'Unknown')}")
    print(f"📚 Book Recommended: {result.get('book_recommended')} by {result.get('author')}")

    if result.get("action_steps"):
        print(f"\n⚡ Action Steps:")
        for i, step in enumerate(result["action_steps"], 1):
            print(f"  {i}. {step}")

    print(f"\n💬 Response:\n{result['response']}")

    if result.get("sources"):
        print(f"\n🔍 Sources Used:")
        for s in result["sources"]:
            print(f"  - {s['book']} (relevance: {s['relevance']})")


async def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        await test_query(query)
    else:
        print("Lumio — Illuminate Your Blind Spots with AI")
        print("Interactive Test Mode | Type your challenge and press Enter. Ctrl+C to quit.\n")

        while True:
            try:
                query = input("Your challenge: ").strip()
                if query:
                    await test_query(query)
                print()
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break


if __name__ == "__main__":
    asyncio.run(main())
