# Polymarket API Reference

## Architecture

Polymarket uses a **proxy wallet** system:

- **EOA address**: Your signing key (from private key)
- **Proxy wallet**: A smart contract that holds your funds (created by Polymarket on first deposit)
- When you deposit via the website, funds go to the proxy wallet, not your EOA

## Authentication

```
signature_type=0  → EOA wallet (MetaMask, direct key)
signature_type=2  → Proxy/browser wallet (SafePal, Coinbase, website deposits)
```

If you deposited via the Polymarket website, you almost certainly need `signature_type=2` + `funder=<proxy_address>`.

## Finding the Proxy Address

The proxy address is visible in Polymarket UI under Settings/Profile. It's a **contract address** (has bytecode on-chain) that holds your USDC.e on Polygon.

To verify: query USDC.e balance of the proxy address on Polygon — it should match your Polymarket balance.

## Geoblock

Polymarket blocks trading from certain regions. The SDK's HTTP layer must route through an allowed proxy exit.

**Blocked regions** (as of 2026-02): US (most states), China, Singapore, France, Cuba, Iran, North Korea, Syria, Crimea, plus others.

**Close-only** (can close but not open): Singapore, Poland, Thailand, Taiwan.

**Allowed**: Japan, UK, Germany, most of EU, South Korea, most of Asia/LATAM.

The `py-clob-client` SDK uses `httpx` internally. Patch the global client:

```python
import py_clob_client.http_helpers.helpers as h
h._http_client = httpx.Client(http2=True, proxy="http://proxy:port")
```

## Allowances

Before placing orders, the proxy wallet must approve Polymarket's exchange contracts to spend USDC. If `allowances` are all `0`, the user needs to make one trade on the website first (triggers automatic approval).

## Market Data (no auth needed)

- `GET https://gamma-api.polymarket.com/markets?closed=false&order=volume24hr&ascending=false&limit=N`
- Response fields: `question`, `outcomePrices` (JSON string `["yes_price","no_price"]`), `clobTokenIds` (JSON string `["yes_token","no_token"]`), `liquidity`, `volume24hr`, `endDate`, `conditionId`

## Order Placement

```python
from py_clob_client.clob_types import OrderArgs, OrderType
order = OrderArgs(price=0.20, size=25.0, side="BUY", token_id=yes_token)
signed = client.create_order(order)
resp = client.post_order(signed, OrderType.GTC)
```

- `price`: 0.01–0.99
- `size`: number of shares (not dollar amount). Cost = price × size
- `side`: BUY or SELL
- `token_id`: the YES or NO token from `clobTokenIds`
- Buying YES at 0.20 means paying $0.20/share, winning $1.00 if YES resolves (5x return)
- Buying NO at 0.80 means paying $0.80/share, winning $1.00 if NO resolves (1.25x return)

## Dependencies

```
pip install py-clob-client httpx
```

Also pulls in: `toolz`, `cytoolz`, `eth-account`, etc.
