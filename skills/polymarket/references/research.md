# Research Framework

## Decision Flow

```
SCAN → FILTER → RESEARCH → QUANTIFY → BET or PASS
                                ↑
                          PASS if no edge
```

**核心原则：没有明确 edge 就不下注。"感觉会赢"不是 edge。**

## Step 1: Filter (from scan results)

Only consider markets that meet ALL criteria:

- Liquidity > $5,000 (otherwise slippage kills you)
- Odds between 10-90% (extremes have no edge for small players)
- End date > 24h away (too close = pure noise)
- You can form an independent opinion (skip sports you don't follow, politics you don't understand)

## Step 2: Research (per candidate market)

### 2a. Read Resolution Criteria

Go to `https://polymarket.com/event/<slug>` or check the market description.
Misunderstanding resolution = guaranteed loss.

### 2b. Gather Intel (minimum 3 sources, 2 categories)

Use `scripts/research.py` to automate:

```bash
python research.py "US strikes Iran" --category geopolitical
python research.py "bitcoin 60000"   --category crypto
```

**Geopolitical events — required sources:**

1. Wire services (Reuters, AP) — factual status, not opinion
2. Domain tracker (ISW, IAEA, CriticalThreats) — expert analysis
3. Official statements — what decision-makers actually said
4. Timeline: deadlines, scheduled meetings, ultimatums

**Crypto/financial — required sources:**

1. Current price + 24h/7d trend (CoinGecko API)
2. Macro calendar this week (FOMC, PCE, CPI, NFP)
3. ETF flows (institutional sentiment)
4. Recent catalyst (tariffs, regulation, hacks)

**Sports — required sources:**

1. Recent form (last 5-10 games)
2. Injury reports
3. Bookmaker odds (compare with Polymarket)
4. Head-to-head history

### 2c. Identify What the Market Might Be Missing

The market is usually right. You need a specific reason it's wrong:

- **Stale pricing**: News broke in last 1-2 hours, market hasn't adjusted
- **Structural bias**: Fear premium on dramatic events (war, crashes)
- **Information asymmetry**: You know something most bettors don't
- **Miscalibrated tail risk**: Market underprices compound catalysts

If you can't articulate a specific reason, **PASS**.

## Step 3: Quantify

### Your Estimate vs Market Price

| Your estimate | Market price | Edge | Action                   |
| ------------- | ------------ | ---- | ------------------------ |
| 35%           | 20%          | +15% | Consider YES             |
| 22%           | 20%          | +2%  | **PASS** (edge too thin) |
| 15%           | 20%          | -5%  | Consider NO              |

**Minimum edge threshold: 10 percentage points** for small bankrolls.
Below that, transaction costs + estimation error eat your edge.

### Expected Value Check

```
EV = (your_prob × payout) - (1 - your_prob) × cost
```

Example: YES @ $0.20, you think 35% chance:

- EV = 0.35 × $0.80 - 0.65 × $0.20 = $0.28 - $0.13 = +$0.15 per share ✅

Example: YES @ $0.20, you think 22% chance:

- EV = 0.22 × $0.80 - 0.78 × $0.20 = $0.176 - $0.156 = +$0.02 per share ❌ (noise)

### Position Sizing

For bankroll B:

- **High confidence edge (>15%)**: up to 25% of B
- **Medium confidence (10-15%)**: up to 15% of B
- **Speculative (<10% edge but compelling thesis)**: up to 5% of B
- **Never** go all-in on a single market

## Step 4: Pre-Flight Checklist

Before placing the order, answer these:

1. ☐ I can state the resolution criteria from memory
2. ☐ I have 3+ sources supporting my view
3. ☐ I can articulate why the market is wrong (not just "I think so")
4. ☐ My estimated probability differs from market by ≥10%
5. ☐ EV is positive after accounting for estimation uncertainty
6. ☐ Position size ≤ 25% of bankroll
7. ☐ I have a plan for if I'm wrong (hold to expiry? cut loss at X?)

If any box is unchecked → **PASS** or go back to research.

## Common Traps

- **"It's only $10"** — Bad process stays bad at any bankroll size. Build good habits.
- **Revenge trading** — Lost a bet? Don't immediately chase with another.
- **Overconfidence after a win** — One win doesn't validate your process.
- **Correlated bets** — "Iran strike by Feb 28" + "Iran strike by Mar 31" = same thesis, not diversification.
