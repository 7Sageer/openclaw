---
name: polymarket
description: Trade on Polymarket prediction markets. Use when placing bets, scanning markets, checking positions/balance, or researching prediction market opportunities. Covers authentication (proxy wallet + geoblock bypass), market analysis, order placement, and portfolio management via py-clob-client SDK.
---

# Polymarket Trading

## Setup

### Environment Variables

```
POLY_PROXY       — HTTP proxy for geoblock bypass (default: http://localhost:10808)
POLY_KEY_PATH    — Path to private key file (default: ~/.polymarket/key)
POLY_FUNDER      — Proxy wallet address (required if deposited via website)
```

### Key File

`~/.polymarket/key` must contain a 32-byte private key (0x + 64 hex chars), chmod 600.
Common mistake: users put their wallet **address** (20 bytes) instead of **private key** (32 bytes).

### First-Time Checklist

1. Verify key file: `wc -c ~/.polymarket/key` → should be 67 bytes (0x + 64 hex + newline)
2. Find proxy wallet address (Polymarket UI → Settings) and set `POLY_FUNDER`
3. Run `poly.py balance` — if allowances show ❌, make one trade on polymarket.com first
4. Verify proxy exit IP is in an allowed region (not US/CN/SG/FR) — see `references/api.md` for full geoblock list

## CLI Tools

### `scripts/poly.py` — Market Operations

```bash
python poly.py scan [--order volume24hr|liquidity] [--limit 30] [--mid-only]
python poly.py search "bitcoin"
python poly.py balance
python poly.py book <token_id>
python poly.py order <token_id> BUY 0.20 25    # buy 25 shares at $0.20
python poly.py orders                            # list open orders
python poly.py cancel <order_id>
python poly.py positions
```

### `scripts/research.py` — Information Gathering

```bash
python research.py "bitcoin 60000"       -c crypto        # prices + news + macro + ETF flows
python research.py "US strikes Iran"     -c geopolitical  # wire services + experts + officials + timeline
python research.py "Arsenal Premier"     -c sports        # form + odds + injuries
```

## Trading Workflow

**Core rule: no edge → no bet. "Feels right" is not edge.**

### Phase 1: Scan & Filter

`poly.py scan --mid-only` → only consider markets with:

- Liquidity > $5k, odds 10-90%, end date > 24h away
- A topic you can form an independent opinion on

### Phase 2: Research (mandatory before any bet)

1. Run `research.py` with appropriate category
2. Read the exact resolution criteria on polymarket.com
3. Gather ≥3 sources across ≥2 categories
4. Articulate **specifically** why the market price is wrong
5. If you can't → **PASS**, move to next market

Full research framework and decision flow: `references/research.md`

### Phase 3: Quantify

- Your estimated probability vs market price — need ≥10% gap
- Calculate EV: `(your_prob × payout) - (1 - your_prob) × cost`
- Position size: max 25% of bankroll per bet, scale down with confidence
- Run pre-flight checklist (7 items) in `references/research.md`

### Phase 4: Execute

1. `poly.py book <token_id>` — check spread and depth
2. `poly.py order <token_id> BUY <price> <size>` — place limit order
3. `poly.py orders` — verify order status

### Phase 5: Monitor

- `poly.py positions` — check current positions
- `poly.py balance` — check remaining USDC
- Set exit plan: hold to expiry or cut at specific loss threshold

## Troubleshooting

| Error                                      | Cause                                 | Fix                                                            |
| ------------------------------------------ | ------------------------------------- | -------------------------------------------------------------- |
| `private key must be exactly 32 bytes`     | Key file has address not private key  | Export actual private key from wallet                          |
| `403 Trading restricted in your region`    | Proxy exit IP in blocked region       | Switch to JP/UK/DE proxy node                                  |
| `allowances all 0`                         | Proxy wallet hasn't approved exchange | Make one trade on polymarket.com                               |
| `NoneType has no attribute signature_type` | Missing BalanceAllowanceParams        | Pass `BalanceAllowanceParams(asset_type=AssetType.COLLATERAL)` |

## API Details

For SDK internals, proxy wallet architecture, and geoblock details: see `references/api.md`.
