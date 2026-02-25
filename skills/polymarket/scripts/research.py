#!/usr/bin/env python3
"""Automated research helper for Polymarket bets."""

import os, sys, json, argparse, httpx

PROXY = os.environ.get("POLY_PROXY", "http://localhost:10808")
BRAVE_KEY = os.environ.get("BRAVE_API_KEY", "")

def _client():
    return httpx.Client(proxy=PROXY, timeout=15)

def brave_search(query, count=5):
    """Search via Brave API."""
    c = _client()
    r = c.get("https://api.search.brave.com/res/v1/web/search",
              params={"q": query, "count": str(count)},
              headers={"X-Subscription-Token": BRAVE_KEY})
    r.raise_for_status()
    results = r.json().get("web", {}).get("results", [])
    return [{"title": r["title"], "desc": r.get("description",""), "url": r["url"]} for r in results]

def crypto_price(ids="bitcoin,ethereum,solana"):
    """Get current prices from CoinGecko."""
    c = _client()
    r = c.get("https://api.coingecko.com/api/v3/simple/price",
              params={"ids": ids, "vs_currencies": "usd", "include_24hr_change": "true"})
    r.raise_for_status()
    return r.json()

def research_crypto(query):
    """Crypto market research pipeline."""
    print("=" * 60)
    print(f"CRYPTO RESEARCH: {query}")
    print("=" * 60)

    # 1. Current prices
    print("\n📊 Current Prices:")
    prices = crypto_price()
    for coin, data in prices.items():
        chg = data.get("usd_24h_change", 0)
        print(f"  {coin}: ${data['usd']:,.2f} ({chg:+.1f}% 24h)")

    # 2. News search
    print(f"\n📰 Recent News:")
    for r in brave_search(f"{query} crypto latest news 2026", 5):
        print(f"  • {r['title']}")
        print(f"    {r['desc'][:150]}")
        print()

    # 3. Macro calendar
    print("📅 Macro Calendar Search:")
    for r in brave_search("economic calendar this week FOMC PCE CPI 2026", 3):
        print(f"  • {r['title']}")
        print(f"    {r['desc'][:150]}")
        print()

    # 4. ETF flows
    print("💰 ETF Flow Sentiment:")
    for r in brave_search("bitcoin ETF inflow outflow this week 2026", 3):
        print(f"  • {r['title']}")
        print(f"    {r['desc'][:150]}")
        print()

def research_geopolitical(query):
    """Geopolitical event research pipeline."""
    print("=" * 60)
    print(f"GEOPOLITICAL RESEARCH: {query}")
    print("=" * 60)

    # 1. Wire services
    print("\n📰 Wire Services (Reuters/AP):")
    for r in brave_search(f"{query} site:reuters.com OR site:apnews.com 2026", 3):
        print(f"  • {r['title']}")
        print(f"    {r['desc'][:150]}")
        print()

    # 2. Expert analysis
    print("🔍 Expert Analysis:")
    for r in brave_search(f"{query} analysis ISW OR criticalthreats OR IAEA 2026", 3):
        print(f"  • {r['title']}")
        print(f"    {r['desc'][:150]}")
        print()

    # 3. Official statements
    print("🏛️ Official Statements:")
    for r in brave_search(f"{query} official statement latest 2026", 3):
        print(f"  • {r['title']}")
        print(f"    {r['desc'][:150]}")
        print()

    # 4. Timeline
    print("⏰ Timeline & Deadlines:")
    for r in brave_search(f"{query} deadline timeline schedule 2026", 3):
        print(f"  • {r['title']}")
        print(f"    {r['desc'][:150]}")
        print()

def research_sports(query):
    """Sports research pipeline."""
    print("=" * 60)
    print(f"SPORTS RESEARCH: {query}")
    print("=" * 60)

    print("\n📊 Recent Form & Odds:")
    for r in brave_search(f"{query} odds prediction form 2026", 5):
        print(f"  • {r['title']}")
        print(f"    {r['desc'][:150]}")
        print()

    print("🏥 Injury Reports:")
    for r in brave_search(f"{query} injury report lineup 2026", 3):
        print(f"  • {r['title']}")
        print(f"    {r['desc'][:150]}")
        print()

CATEGORIES = {
    "crypto": research_crypto,
    "geopolitical": research_geopolitical,
    "geo": research_geopolitical,
    "sports": research_sports,
}

def main():
    p = argparse.ArgumentParser(description="Research helper for Polymarket")
    p.add_argument("query", help="Search query")
    p.add_argument("--category", "-c", default="crypto", choices=list(CATEGORIES.keys()))
    args = p.parse_args()
    CATEGORIES[args.category](args.query)

if __name__ == "__main__":
    main()
