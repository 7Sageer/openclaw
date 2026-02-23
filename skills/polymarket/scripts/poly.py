#!/usr/bin/env python3
"""Polymarket CLI — scan markets, check balance, place orders."""

import os, sys, json, argparse, httpx

PROXY = os.environ.get("POLY_PROXY", "http://localhost:10808")
KEY_PATH = os.path.expanduser(os.environ.get("POLY_KEY_PATH", "~/.polymarket/key"))
FUNDER = os.environ.get("POLY_FUNDER", "")
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

# --- helpers ---

def _proxy_client():
    return httpx.Client(http2=True, proxy=PROXY, timeout=20)

def _load_key():
    return open(KEY_PATH).read().strip()

def _clob_client():
    """Return authenticated ClobClient with proxy patched in."""
    import py_clob_client.http_helpers.helpers as h
    h._http_client = _proxy_client()
    from py_clob_client.client import ClobClient
    key = _load_key()
    kwargs = dict(key=key, chain_id=137)
    if FUNDER:
        kwargs.update(signature_type=2, funder=FUNDER)
    else:
        kwargs.update(signature_type=0)
    client = ClobClient(CLOB_API, **kwargs)
    creds = client.create_or_derive_api_creds()
    client.set_api_creds(creds)
    return client

# --- commands ---

def cmd_scan(args):
    """Scan top markets by volume or liquidity."""
    c = _proxy_client()
    params = {
        "closed": "false",
        "order": args.order,
        "ascending": "false",
        "limit": str(args.limit),
    }
    r = c.get(f"{GAMMA_API}/markets", params=params)
    r.raise_for_status()
    for m in r.json():
        prices = json.loads(m.get("outcomePrices") or "[]")
        if not prices:
            continue
        yes, no = float(prices[0]), float(prices[1])
        if args.mid_only and (yes < 0.10 or yes > 0.90):
            continue
        print(f"[YES {yes:.1%} / NO {no:.1%}]  {m['question']}")
        print(f"  liq=${float(m.get('liquidity',0)):,.0f}  vol24h=${float(m.get('volume24hr',0)):,.0f}  end={m.get('endDate','?')}")
        tokens = json.loads(m.get("clobTokenIds") or "[]")
        if tokens:
            print(f"  yes_token={tokens[0][:20]}...  no_token={tokens[1][:20]}...")
        print()

def cmd_search(args):
    """Search markets by keyword (paginated, client-side filter)."""
    c = _proxy_client()
    q = args.query.lower()
    found = 0
    for offset in range(0, args.limit, 100):
        r = c.get(f"{GAMMA_API}/markets", params={
            "closed": "false", "limit": "100", "offset": str(offset),
        })
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        for m in batch:
            if q not in m.get("question", "").lower():
                continue
            prices = json.loads(m.get("outcomePrices") or "[]")
            if len(prices) < 2:
                continue
            tokens = json.loads(m.get("clobTokenIds") or "[]")
            print(f"[YES {float(prices[0]):.1%} / NO {float(prices[1]):.1%}]  {m['question']}")
            print(f"  end={m.get('endDate','?')}  liq=${float(m.get('liquidity',0)):,.0f}")
            if tokens:
                print(f"  yes_token={tokens[0]}")
                print(f"  no_token={tokens[1]}")
            print()
            found += 1
    if not found:
        print("No markets found.")

def cmd_balance(args):
    """Check USDC balance and allowances."""
    client = _clob_client()
    from py_clob_client.clob_types import BalanceAllowanceParams, AssetType
    print(f"Address: {client.get_address()}")
    if FUNDER:
        print(f"Funder:  {FUNDER}")
    params = BalanceAllowanceParams(asset_type=AssetType.COLLATERAL)
    ba = client.get_balance_allowance(params)
    bal = int(ba["balance"]) / 1e6
    print(f"USDC:    ${bal:.2f}")
    approved = all(int(v) > 0 for v in ba["allowances"].values())
    print(f"Approved: {'✅' if approved else '❌ (need to approve on polymarket.com first)'}")

def cmd_book(args):
    """Show orderbook for a token."""
    client = _clob_client()
    book = client.get_order_book(args.token_id)
    print(f"Market: {book.market if hasattr(book, 'market') else '?'}")
    # Handle both object and string representations
    book_str = str(book)
    if "bids=" in book_str:
        print("\nBids (buy):")
        for part in book_str.split("OrderSummary("):
            if "price=" in part and "bids" in book_str[:book_str.index(part)] if part in book_str else True:
                # Just print raw for agent to parse
                pass
    print(book_str[:2000])

def cmd_order(args):
    """Place a limit order."""
    client = _clob_client()
    from py_clob_client.clob_types import OrderArgs, OrderType
    order_args = OrderArgs(
        price=args.price,
        size=args.size,
        side=args.side.upper(),
        token_id=args.token_id,
    )
    signed = client.create_order(order_args)
    resp = client.post_order(signed, OrderType.GTC)
    print(json.dumps(resp, indent=2, default=str))

def cmd_orders(args):
    """List open orders."""
    client = _clob_client()
    orders = client.get_orders()
    if not orders:
        print("No open orders.")
        return
    for o in orders:
        print(json.dumps(o, indent=2, default=str))

def cmd_cancel(args):
    """Cancel an order by ID."""
    client = _clob_client()
    resp = client.cancel(args.order_id)
    print(json.dumps(resp, indent=2, default=str))

def cmd_positions(args):
    """Show current positions via data API."""
    c = _proxy_client()
    client = _clob_client()
    addr = client.get_address()
    r = c.get(f"https://data-api.polymarket.com/positions", params={"user": addr})
    r.raise_for_status()
    data = r.json()
    if not data:
        print("No positions.")
        return
    for p in data:
        print(json.dumps(p, indent=2, default=str)[:500])
        print()

# --- main ---

def main():
    p = argparse.ArgumentParser(description="Polymarket CLI")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("scan", help="Scan top markets")
    s.add_argument("--order", default="volume24hr", choices=["volume24hr", "liquidity"])
    s.add_argument("--limit", type=int, default=30)
    s.add_argument("--mid-only", action="store_true", help="Only show 10-90% odds")

    s = sub.add_parser("search", help="Search markets by keyword")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=200)

    s = sub.add_parser("balance", help="Check USDC balance")

    s = sub.add_parser("book", help="Show orderbook")
    s.add_argument("token_id")

    s = sub.add_parser("order", help="Place limit order")
    s.add_argument("token_id")
    s.add_argument("side", choices=["BUY", "SELL", "buy", "sell"])
    s.add_argument("price", type=float, help="Price 0.01-0.99")
    s.add_argument("size", type=float, help="Number of shares")

    s = sub.add_parser("orders", help="List open orders")

    s = sub.add_parser("cancel", help="Cancel order")
    s.add_argument("order_id")

    s = sub.add_parser("positions", help="Show positions")

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        sys.exit(1)

    globals()[f"cmd_{args.cmd}"](args)

if __name__ == "__main__":
    main()
