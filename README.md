# ARES TradingView Engines

![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-blue)
![Python](https://img.shields.io/badge/Language-Python-blue)
![Platform](https://img.shields.io/badge/Platform-TradingView-black)
![License](https://img.shields.io/badge/License-MPL--2.0-purple)

ARES contains two TradingView setups: the original BBSR/LC confirmation engine and a separate kernel color-change swing strategy. Both use the 09:30–15:00 **America/New_York** entry window, which follows daylight saving time.

## Kernel Swing Strategy

[`ARES_Kernel_Swing_Strategy_JXS.pine`](ARES_Kernel_Swing_Strategy_JXS.pine) trades the rational quadratic kernel line from jdehorty's Lorentzian Classification indicator. The default color changes with the line's slope; enable **Enhance Kernel Smoothing** to use the original Gaussian comparison instead. Lookback, relative weighting, regression level, lag, and source are configurable.

| Kernel changes | Strategy action |
| --- | --- |
| Red to green | Enter long; reverse an open short |
| Green to red | Enter short; reverse an open long |
| Change outside 09:30–15:00 | Close an opposite position, but open no new position |
| Target or stop fills | Stay flat until the next color change |

Orders are placed on the confirmed signal bar's close. The session limits **new entries**; open trades may continue past 15:00 or overnight until the next color change or an enabled stop/target. For precise session boundaries, use an intraday time based chart such as 1 minute or 5 minutes.

**Optional R target:** Disabled by default so trades follow the kernel until its color changes. When enabled, 1R is the ATR reading on the entry bar multiplied by the configurable stop distance (default: 14 period ATR × 1). A fixed stop is placed 1R from entry; the take profit is placed at the selected multiple (default **2R**, adjustable to **3R** or another value). These distances are in the underlying chart's price units, not option premium. A color change can close or reverse a position before either bracket order fills.

The compact LC-style trade box uses `size.normal`, the LC teal/red palette, and TradingView's **actual closed strategy trades** for win rate, trades, net P&L, profit factor, and win/loss ratio. “Early Color Flips” counts an opposite color change less than four bars after an open trade's entry.

## Confirmation Engine

[`ARES_Redline_Engine_JXS.pine`](ARES_Redline_Engine_JXS.pine) is the indicator; [`ARES_Confirmation_Engine_Strategy_JXS.pine`](ARES_Confirmation_Engine_Strategy_JXS.pine) is its Strategy Tester version. The signal path is:

**BBSR arrow → consecutive LC and slope confirmations → BUY/SELL flag**

The BBSR arrow arms the setup. Starting on the following candle, each required confirmation bar must agree with the LC direction and meet an ATR normalized price slope threshold. The default confirmation count is two bars. The confirmation strategy uses a four bar maximum trade duration by default, with optional LC flip and session exits. Its alerts fire on the confirmed entry, not the initial BBSR arrow.

## Use

1. Open the desired `.pine` file and paste its entire contents into TradingView's Pine Editor.
2. Add it to an intraday chart. The strategies report results in **Strategy Tester**.
3. For the kernel strategy, adjust the kernel inputs to match your LC chart. Switch on **Use stop and R target** if you want a fixed 2R/3R target.
4. Configure fees, slippage, and position size in TradingView's strategy properties for the instrument you trade.

The kernel strategy imports `jdehorty/KernelFunctions/2`; the confirmation engines import `jdehorty/MLExtensions/2`. TradingView must have access to these published Pine libraries. Backtests depend on chart bars and the broker emulator; they do not model option contract pricing.

## Files

- `ARES_Kernel_Swing_Strategy_JXS.pine` — kernel color-change strategy and LC-style trade box
- `ARES_Redline_Engine_JXS.pine` — BBSR/LC confirmation indicator
- `ARES_Confirmation_Engine_Strategy_JXS.pine` — confirmation strategy
- `ares_reference.py` and `requirements.txt` — Python research companion
- `THIRD_PARTY_NOTICES.md` and `LICENSE` — attribution and MPL 2.0

## Author

**JXS** · GitHub: [@woi-6ix](https://github.com/woi-6ix)

Based in part on Lorentzian Classification and kernel regression work by **jdehorty**. See [third-party notices](THIRD_PARTY_NOTICES.md). Licensed under [MPL 2.0](LICENSE).
