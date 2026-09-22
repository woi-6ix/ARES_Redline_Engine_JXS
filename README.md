# ARES Confirmation Engine

![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-blue)
![Python](https://img.shields.io/badge/Language-Python-blue)
![Platform](https://img.shields.io/badge/Platform-TradingView-black)
![License](https://img.shields.io/badge/License-MPL--2.0-purple)
![Engine](https://img.shields.io/badge/Engine-BBSR%20%2B%20Lorentzian-red)

**ARES** is a TradingView confirmation engine built around a simple sequence:

**BBSR arrow → LC confirmation bars → slope confirmation → entry flag**

The previous red-line-cross requirement has been removed. A BBSR Bull or Bear arrow now starts the setup directly.

Repository: https://github.com/woi-6ix/ARES_Redline_Engine_JXS

> For research, calibration, and backtesting only.

---

## Signal Logic

### Bullish

1. BBSR prints a **Bull** arrow during the active session.
2. ARES begins counting confirmation bars starting from the **next candle**.
3. Every confirmation bar must have:
   - bullish Lorentzian Classification state;
   - positive ATR-normalized price slope above the configured threshold.
4. Once the selected number of consecutive bars is reached, ARES prints a **BUY flag**.
5. The entry alert fires only at this point.

### Bearish

1. BBSR prints a **Bear** arrow during the active session.
2. Confirmation begins on the next candle.
3. Every confirmation bar must have:
   - bearish Lorentzian Classification state;
   - negative ATR-normalized price slope below the configured threshold.
4. Once the selected number of consecutive bars is reached, ARES prints a **SELL flag**.
5. The entry alert fires only after confirmation is complete.

The confirmation count is configurable. The default is **2 bars**, but it can be changed to 1 or any larger value supported by the input.

---

## Trading Window

ARES uses:

**09:30–15:00 America/New_York**

BBSR arrows outside the trading window do not arm a setup.

Pending setups are cleared outside the active session. Active trades can optionally receive an exit at 3:00 PM.

---

## Lorentzian Confirmation

ARES embeds the Lorentzian Classification feature engine and Approximate Nearest Neighbor logic used by the LC indicator.

Default features:

| Feature | Parameters |
| --- | --- |
| RSI | 14 / 1 |
| WaveTrend | 10 / 11 |
| CCI | 20 / 1 |
| ADX | 20 / 2 |
| RSI | 9 / 1 |

Optional LC filters include volatility, regime, ADX, EMA, and SMA confirmation.

ARES does not enter simply because LC is bullish or bearish. LC must match the original BBSR direction on **each required confirmation candle**.

---

## Slope Confirmation

Price slope is calculated from linear regression and normalized by ATR.

For a bullish confirmation bar:

```text
Normalized slope >= minimum slope threshold
```

For a bearish confirmation bar:

```text
Normalized slope <= -minimum slope threshold
```

The default slope threshold is **0.05 ATR**.

If either LC state or slope fails on a candle, the consecutive confirmation count resets while the BBSR setup remains armed until the maximum confirmation window expires.

---

## Chart Theme

ARES follows the simplified LC visual language:

- Teal: bullish
- Red: bearish
- Gray: neutral
- Small triangle: original BBSR arrow
- Flag: confirmed ARES entry
- X: trade exit
- Subtle candle tint: a bar that currently passes both LC and slope confirmation

TradingView's standard chart/table typography is used to stay visually consistent with LC.

---

## Entries and Exits

The entry flag is the point where the full ARES confirmation sequence has completed.

Exits use a simplified LC-style lifecycle:

- maximum trade-bar duration;
- optional early exit when LC flips to the opposite state;
- optional session-end exit.

The default maximum trade duration is **4 bars**, matching the four-bar horizon used by the LC model.

---

## Alert

ARES uses a single functional entry alert.

After adding either the indicator or strategy to TradingView:

1. Select **Create Alert**.
2. Choose **ARES Confirmation Engine v3** or **ARES Confirmation Engine Strategy v3**.
3. Select **Any alert() function call**.
4. Use **Once Per Bar Close**.

The alert only fires after the requested confirmation bars have passed both LC and slope checks.

Messages identify either:

- `ARES BUY`
- `ARES SELL`

Raw BBSR arrows do not trigger the ARES entry alert.

---

## LC-Style Trade Stats

The compact stats panel uses the LC backtest helper and displays:

- Win rate
- Trades
- Wins / losses
- Win/loss ratio
- Early LC flips
- Current LC state
- Current confirmation progress

These LC-style statistics are intended for calibration. The separate strategy file also exposes the same confirmed entries and LC-style exits directly to TradingView Strategy Tester.

---

## Main Controls

| Group | Controls |
| --- | --- |
| BBSR | Bollinger settings, Stochastic RSI settings, extremes |
| Trading Hours | Session window |
| Lorentzian Classification | Neighbors, history, prediction threshold |
| LC Filters | Volatility, regime, ADX, EMA, SMA |
| LC Feature Engineering | RSI, WT, CCI, ADX parameters |
| Confirmation Slope | Lookback, minimum normalized slope |
| ARES Confirmation | Confirmation bars, maximum wait |
| LC-Style Exits | Maximum bars, LC flip, session exit |
| LC Trade Stats | Table and worst-case estimate |

---

## Files

- `ARES_Redline_Engine_JXS.pine` — TradingView indicator
- `ARES_Confirmation_Engine_Strategy_JXS.pine` — TradingView strategy / Strategy Tester version
- `ares_reference.py` — Python research companion
- `THIRD_PARTY_NOTICES.md` — third-party attribution
- `LICENSE` — MPL 2.0 license

---

## Author

**JXS**  
GitHub: [@woi-6ix](https://github.com/woi-6ix)

## License and Attribution

Licensed under the **Mozilla Public License 2.0**.

Lorentzian Classification concepts and portions of the ML logic are attributed to **jdehorty**. ARES integration and sequencing changes are identified in the source header.
