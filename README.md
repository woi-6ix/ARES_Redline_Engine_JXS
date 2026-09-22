# ARES Redline Engine ⚔️

![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-blue)
![Python](https://img.shields.io/badge/Language-Python-blue)
![Platform](https://img.shields.io/badge/Platform-TradingView-black)
![License](https://img.shields.io/badge/License-MPL--2.0-purple)
![Engine](https://img.shields.io/badge/Engine-BBSR%20%2B%20Lorentzian-red)
![Status](https://img.shields.io/badge/Mode-Backtesting%20%2F%20Research-yellow)

**ARES Redline Engine** is a TradingView strategy that combines Bollinger Band/Stochastic RSI extremes, a red-line mean-reversion trigger, Lorentzian nearest-neighbor classification, and a hard price-slope filter.

The strategy waits for a BBSR extreme, arms a directional setup, watches for price to attack the Bollinger basis, and only enters when Lorentzian state and recent momentum agree.

Repository: [https://github.com/woi-6ix/ARES_Redline_Engine_JXS](https://github.com/woi-6ix/ARES_Redline_Engine_JXS)

> For backtesting, education, and research only. No strategy can guarantee profitable trades.

---

## Overview

ARES is designed to reject weak or contradictory entries. Every trade must pass four gates:

1. A BBSR extreme arms the setup.
2. Price attacks or crosses the red Bollinger basis.
3. Lorentzian Classification agrees with the direction.
4. ATR-normalized slope and recent bars confirm momentum.

The setup expires if price does not reach the red line within the configured waiting window.

---

## Entry Logic

| Gate | Long | Short |
| --- | --- | --- |
| BBSR | Bull extreme armed | Bear extreme armed |
| Red line | Wick or close crosses above | Wick or close crosses below |
| Lorentzian state | Bullish | Bearish |
| Regression slope | At or above positive threshold | At or below negative threshold |
| Recent bars | Enough bullish movement | Enough bearish movement |

All gates are required. A valid BBSR, red-line, and Lorentzian setup is ignored when the slope or directional-bar filter fails.

---

## Core Features

- **BBSR extreme detection:** Combines Bollinger Band re-entry with Stochastic RSI extremes.
- **Red-line trigger:** Uses the Bollinger basis as the central attack or cross level.
- **Lorentzian classification:** Compares normalized RSI, WaveTrend, CCI, and ADX feature states with historical samples.
- **Hard slope filter:** Blocks entries when recent price slope disagrees with the trade.
- **Directional-bar agreement:** Requires enough recent bars to support the intended direction.
- **Post-entry G gauge:** Displays `G+` or `G-` after entry to show immediate slope direction.
- **Strategy testing:** Supports reversals and optional fixed target and stop exits.
- **Stats and alerts:** Provides on-chart performance metrics and TradingView alert conditions.

---

## Methodology

### 1. BBSR setup

The setup begins when price closes back inside a Bollinger Band after being outside it on the previous bar, while smoothed Stochastic RSI is at an extreme.

| Setup | Price condition | Oscillator condition |
| --- | --- | --- |
| Bullish | Re-enters above the lower band | K and D below the lower limit |
| Bearish | Re-enters below the upper band | K and D above the upper limit |

### 2. Red-line trigger

Two entry modes are available:

| Mode | Requirement |
| --- | --- |
| Aggressive Wick Cross | The candle penetrates the Bollinger basis |
| Confirmed Close Cross | The candle closes across the Bollinger basis |

### 3. Lorentzian classification

ARES compares the current feature state with chronologically spaced historical samples using Lorentzian distance:

```text
d(x, y) = Σ log(1 + |xᵢ − yᵢ|)
```

Optional volatility, regime, ADX, EMA, and SMA filters can further restrict the classification state.

### 4. Slope confirmation and G gauge

The entry slope is normalized by ATR:

```text
Normalized slope = regression slope / ATR(14)
```

| Default setting | Value |
| --- | ---: |
| Slope lookback | 5 bars |
| Minimum normalized slope | 0.05 |
| Directional-bar lookback | 5 bars |
| Minimum matching bars | 3 bars |
| G gauge duration | 4 bars after entry |

`G+` means the immediate raw price slope is bullish. `G-` means it is bearish. A long followed by `G-`, or a short followed by `G+`, is an early caution signal rather than a separate exit.

### 5. Exits

By default, the strategy reverses on an opposite valid signal. Optional fixed exits can also be enabled:

| Exit input | Default |
| --- | ---: |
| Fixed TP/SL | Disabled |
| Profit target | $0.50 |
| Stop loss | $0.10 |

The `$0.50` target and `$0.10` stop are distances in the charted instrument's price—not option-premium targets.

---

## Quick Start 🚀

1. Open [`ARES_Redline_Engine_JXS.pine`](./ARES_Redline_Engine_JXS.pine).
2. Copy the complete source code.
3. Open TradingView and select **Pine Editor**.
4. Paste the strategy, save it, and select **Add to chart**.
5. Open **Strategy Tester** to review historical results.

To clone the repository:

```bash
git clone https://github.com/woi-6ix/ARES_Redline_Engine_JXS.git
cd ARES_Redline_Engine_JXS
```

### Requirements

- TradingView with Pine Editor and Strategy Tester access
- Pine Script v6
- Access to the published `jdehorty/MLExtensions/2` Pine library

No Python packages are required to run the TradingView strategy. `requirements.txt` documents the platform dependency for repository consistency.

---

## Main Controls

| Group | Key controls |
| --- | --- |
| BBSR Extreme | Bollinger length, deviation, Stochastic smoothing, extreme thresholds |
| Lorentzian Classification | Neighbors, history, features, prediction strength |
| LC Filters | Volatility, regime, ADX, EMA, and SMA filters |
| ARES Entry Logic | Wick or close crossing, setup delay, maximum setup age |
| Price Slope Filter | Lookback, normalized threshold, directional bars, G gauge |
| Strategy Exits | Opposite-signal reversal, fixed target, fixed stop |

---

## Alerts

The script exposes three TradingView alert conditions:

- `ARES BUY`
- `ARES SELL`
- `ARES ENTRY`

For close-confirmed behavior, select `Confirmed Close Cross` and use **Once Per Bar Close** when creating the alert.

---

## Risk and Limitations ⚠️

- Historical results do not guarantee future performance.
- `Aggressive Wick Cross` and `calc_on_every_tick=true` can behave differently in real time than on historical bars.
- Fixed targets use the underlying chart price, not an option contract's premium.
- Backtests do not automatically model realistic spreads, slippage, liquidity, option Greeks, or brokerage fills.
- Settings optimized for one symbol or timeframe may be overfit.
- The strategy depends on TradingView resolving `jdehorty/MLExtensions/2`.

Always test across unseen periods and different market regimes before relying on any configuration.

---

## Troubleshooting

### End of line without line continuation

Use the repository version of `get_lorentzian_distance()`. Each switch calculation intentionally stays on one line to avoid Pine's line-continuation error.

### Imported library cannot be found

Confirm the import is exactly:

```pine
import jdehorty/MLExtensions/2 as ml
```

### No trades appear

- Confirm enough chart history is loaded.
- Temporarily disable optional LC filters to identify the blocking gate.
- Carefully reduce `Minimum ATR-Normalized Slope`.
- Increase `Maximum Bars To Wait` if red-line attacks occur late.

---

## Author

**JXS**
GitHub: [@woi-6ix](https://github.com/woi-6ix)

## License and Attribution

Licensed under the **Mozilla Public License 2.0**. See [`LICENSE`](./LICENSE) and [`THIRD_PARTY_NOTICES.md`](./THIRD_PARTY_NOTICES.md).

The Lorentzian Classification concept and portions of the ML logic are attributed to **jdehorty**. ARES strategy integration and modifications are identified in the source header.
