# ARES Redline Engine

![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-blue)
![Platform](https://img.shields.io/badge/Platform-TradingView-black)
![License](https://img.shields.io/badge/License-MPL--2.0-purple)
![Engine](https://img.shields.io/badge/Engine-BBSR%20%2B%20Lorentzian-red)
![Filter](https://img.shields.io/badge/Filter-ATR--Normalized%20Slope-orange)
![Status](https://img.shields.io/badge/Mode-Backtesting%20%2F%20Research-yellow)

**ARES Redline Engine**, named after Ares, the Greek god of war, is a TradingView strategy that combines Bollinger Band/Stochastic RSI extremes, a red-line mean-reversion trigger, Lorentzian nearest-neighbor classification, and a hard price-slope filter.

The engine waits for a BBSR extreme, arms a directional setup, watches for price to attack or cross the Bollinger basis, verifies the Lorentzian state, and rejects the entry unless recent price momentum is strong and aligned with the proposed trade.

> This strategy is for **backtesting, education, and research only**. It does not guarantee profitable trades and should not be treated as financial advice.

---

## Project Overview

ARES is designed to reduce weak or contradictory entries. A setup is not enough on its own: the engine requires agreement between the BBSR sequence, the red-line trigger, Lorentzian classification, linear-regression slope, and recent directional bars.

The default slope configuration uses a five-bar linear regression, normalizes its slope by ATR, and requires at least three of the last five bars to move in the intended direction.

---

## What the Strategy Does

### Long sequence

1. Detects a bullish BBSR extreme below the lower Bollinger Band.
2. Arms a bullish setup for a configurable number of bars.
3. Waits for price to wick through or close above the red Bollinger basis.
4. Requires the Lorentzian Classification state to be bullish.
5. Requires ATR-normalized regression slope to be sufficiently positive.
6. Requires enough recent bars to move upward.
7. Places an `ARES LONG` strategy order.

### Short sequence

1. Detects a bearish BBSR extreme above the upper Bollinger Band.
2. Arms a bearish setup for a configurable number of bars.
3. Waits for price to wick through or close below the red Bollinger basis.
4. Requires the Lorentzian Classification state to be bearish.
5. Requires ATR-normalized regression slope to be sufficiently negative.
6. Requires enough recent bars to move downward.
7. Places an `ARES SHORT` strategy order.

---

## Key Features

- **Red-Line Entry Trigger**
  Uses the Bollinger basis as the central attack/cross level.

- **BBSR Extreme Detection**
  Combines Bollinger Band re-entry with Stochastic RSI extremes.

- **Lorentzian Classification State**
  Uses RSI, WaveTrend, CCI, and ADX feature combinations with Lorentzian distance.

- **Hard Slope Filter**
  Blocks longs unless the normalized slope is positive and blocks shorts unless it is negative.

- **Post-Entry G Gauge**
  Shows a simple `G+` or `G-` on the first bars after entry so adverse short-term direction is immediately visible.

- **Directional-Bar Agreement**
  Requires a configurable number of recent bars to support the intended direction.

- **Strategy Backtesting**
  Includes TradingView strategy entries, reversal controls, optional fixed profit target, and optional fixed stop loss.

- **On-Chart Statistics**
  Displays position, armed setup, LC state, slope, directional bars, win rate, profit factor, P/L, and drawdown.

- **TradingView Alerts**
  Provides individual BUY/SELL conditions and a combined ARES entry condition.

---

## Strategy Methodology

### 1. BBSR extreme

The setup begins when price closes back inside a Bollinger Band after being outside it on the previous bar, while smoothed Stochastic RSI is at an extreme.

| Setup | Price condition | Oscillator condition |
| --- | --- | --- |
| Bullish | Previous close below lower band; current close above lower band | K and D below lower limit |
| Bearish | Previous close above upper band; current close below upper band | K and D above upper limit |

### 2. Armed setup window

A BBSR event arms one direction. The engine waits at least `Minimum Bars After BBSR Signal` and invalidates the setup after `Maximum Bars To Wait`.

### 3. Red-line trigger

Two modes are available:

| Mode | Requirement |
| --- | --- |
| Aggressive Wick Cross | The candle penetrates the Bollinger basis |
| Confirmed Close Cross | The close crosses the Bollinger basis |

### 4. Lorentzian classification

The classifier builds normalized technical feature series and compares the current feature state with chronologically spaced historical samples using Lorentzian distance:

```text
d(x, y) = Σ log(1 + |xᵢ − yᵢ|)
```

This distance reduces the influence of extreme feature differences relative to a simple Euclidean metric. Optional volatility, regime, ADX, EMA, and SMA filters can further restrict the classification state.

### 5. Price-slope filter

ARES calculates a linear-regression slope and normalizes it by ATR:

```text
Normalized slope = regression slope / ATR(14)
```

Default requirements:

| Parameter | Default |
| --- | ---: |
| Slope lookback | 5 bars |
| Minimum normalized slope | 0.05 |
| Directional-bar lookback | 5 bars |
| Minimum matching bars | 3 bars |

The optional post-entry G gauge uses the same raw regression slope without the minimum-strength threshold. By default, it marks the first four bars after each entry: `G+` means the immediate price slope is bullish and `G-` means it is bearish. A long followed by `G-`, or a short followed by `G+`, is an early caution signal rather than a separate strategy exit.

A bullish setup with flat or negative slope is rejected. A bearish setup with flat or positive slope is also rejected.

### 6. Exits

By default, an open position reverses only when an opposite valid ARES signal occurs. Optional fixed price-distance exits can be enabled.

| Exit input | Default |
| --- | ---: |
| Fixed TP/SL enabled | No |
| Profit target | $0.50 |
| Stop loss | $0.10 |

These are underlying price distances—not option-premium targets—and must be adjusted for the symbol being tested.

---

## Entry Requirements

| Gate | Long | Short |
| --- | --- | --- |
| BBSR | Bull extreme armed | Bear extreme armed |
| Red line | Wick/close crosses above | Wick/close crosses below |
| LC state | Bullish | Bearish |
| Regression slope | At or above positive threshold | At or below negative threshold |
| Recent bars | Enough bullish movement | Enough bearish movement |

All gates are required. A valid BBSR + red-line + Lorentzian setup is ignored if the slope or directional-bar filter fails.

---

## Project Structure

```text
ARES_Redline_Engine_JXS/
├── ARES_Redline_Engine_JXS.pine
├── LICENSE
├── README.md
├── THIRD_PARTY_NOTICES.md
├── requirements.txt
└── .gitignore
```

---

## Tech Stack

- TradingView
- Pine Script v6
- `jdehorty/MLExtensions/2`
- Bollinger Bands
- Stochastic RSI
- Approximate nearest-neighbor classification
- Lorentzian distance
- Linear regression
- Average True Range

---

## Requirements

- A TradingView account with access to the Pine Editor and Strategy Tester
- Pine Script v6
- Internet access so TradingView can resolve `jdehorty/MLExtensions/2`

No Python installation or pip packages are required. `requirements.txt` is included for repository consistency and documents the platform-level dependency.

---

## Installation

1. Open `ARES_Redline_Engine_JXS.pine`.
2. Copy the complete source code.
3. Open TradingView and select **Pine Editor**.
4. Create a new blank strategy.
5. Paste the code and select **Save**.
6. Select **Add to chart**.
7. Open **Strategy Tester** to review historical results.

To clone the repository locally:

```bash
git clone https://github.com/woi-6ix/ARES_Redline_Engine_JXS.git
cd ARES_Redline_Engine_JXS
```

---

## Main Controls

### BBSR Extreme

- Bollinger length and standard deviation
- Stochastic K and D smoothing
- RSI and Stochastic lengths
- Upper and lower extreme thresholds

### Lorentzian Classification

- Neighbor count
- Historical lookback
- Feature count
- Minimum prediction strength
- Volatility, regime, and ADX filters
- Optional EMA and SMA direction filters

### ARES Entry Logic

- Aggressive wick or confirmed close crossing
- Minimum delay after BBSR
- Maximum armed-setup age

### Price Slope Filter

- Slope lookback
- Minimum ATR-normalized slope
- Directional-bar lookback
- Minimum matching bars

### Strategy Exits

- Reverse on opposite signal
- Optional fixed target and stop

---

## Alerts

The script exposes three alert conditions:

- `ARES BUY`
- `ARES SELL`
- `ARES ENTRY`

Create an alert in TradingView and select the required ARES condition. For close-confirmed behavior, use **Once Per Bar Close** and select `Confirmed Close Cross` in the strategy settings.

---

## Known Limitations

### No strategy can be 100% accurate

Market behavior changes. Historical performance does not guarantee future performance, and classification or slope filters can fail.

### Intrabar behavior

`Aggressive Wick Cross` and `calc_on_every_tick=true` may behave differently in real time than on historical bars. Use confirmed-close mode for more conservative signal confirmation.

### Imported Pine dependency

The script depends on the published `jdehorty/MLExtensions/2` Pine library. Availability and behavior depend on TradingView resolving that import.

### Fixed targets are symbol-price distances

The `$0.50` target and `$0.10` stop apply to the charted instrument's price, not directly to an option contract's premium.

### Execution assumptions

Backtests do not automatically model realistic spreads, slippage, liquidity, option Greeks, or brokerage fills. Configure Strategy Tester properties for the market being evaluated.

### Parameter overfitting

Optimizing settings on one symbol or timeframe can produce fragile results. Validate parameters across unseen periods and multiple market regimes.

---

## Troubleshooting

### End of line without line continuation

Use the repository version of `get_lorentzian_distance()`. Each switch calculation intentionally stays on one line to avoid Pine's line-continuation parser error.

### Imported library cannot be found

Confirm the import is exactly:

```pine
import jdehorty/MLExtensions/2 as ml
```

### No trades appear

- Confirm enough chart history is loaded.
- Temporarily disable optional LC filters to identify which gate is blocking signals.
- Reduce `Minimum ATR-Normalized Slope` carefully.
- Confirm `Minimum Matching Bars` does not exceed the directional lookback.
- Increase `Maximum Bars To Wait` if red-line attacks occur late.

### Too many weak entries

- Increase the normalized slope threshold.
- Increase the number of required directional bars.
- Use confirmed close crossing.
- Enable EMA or SMA filtering.

---

## Learning Objectives

This project demonstrates:

- Multi-stage strategy state management in Pine Script
- Feature-based historical pattern comparison
- Lorentzian distance for robust similarity scoring
- ATR-normalized momentum filters
- Strategy entries, exits, reversals, and alerts
- On-chart performance diagnostics
- The difference between signal generation and realistic execution

---

## Future Improvements

- Trading-session controls
- Configurable commission and slippage presets
- ATR- or R-multiple exits
- Out-of-sample validation helpers
- Walk-forward parameter testing notes
- Additional setup-rejection diagnostics
- Optional cooldown after exits

---

## Financial Disclaimer

This repository is provided solely for educational, research, and backtesting purposes. It is not financial, investment, legal, or tax advice. Trading stocks, options, futures, forex, and digital assets involves substantial risk, including the possible loss of all capital. Always conduct independent research and use appropriate risk management.

---

## Author

**JXS**
GitHub: [@woi-6ix](https://github.com/woi-6ix)

---

## License and Attribution

This project is licensed under the **Mozilla Public License 2.0**. See `LICENSE` for the complete terms and `THIRD_PARTY_NOTICES.md` for upstream attribution.

The Lorentzian Classification concept and portions of the ML logic are attributed to **jdehorty** and remain subject to MPL-2.0. Modifications and the ARES strategy integration are identified in the source header.
