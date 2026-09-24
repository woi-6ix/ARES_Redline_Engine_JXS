# ARES TradingView Engines

![Pine Script](https://img.shields.io/badge/Pine%20Script-v6-blue)
![Python](https://img.shields.io/badge/Language-Python-blue)
![Platform](https://img.shields.io/badge/Platform-TradingView-black)
![License](https://img.shields.io/badge/License-MPL--2.0-purple)

ARES contains the original BBSR/LC confirmation engine and two separate strategies: one follows Lorentzian Classification's own trade signals; the other follows kernel color changes. New entries use the 09:30–15:00 **America/New_York** window, which follows daylight saving time.

## LC Trade Strategy

[`ARES_LC_Trade_Strategy_JXS.pine`](ARES_LC_Trade_Strategy_JXS.pine) rebuilds the attached Lorentzian Classification indicator's feature engine, neighbor search, filters, kernel check, and original buy/sell conditions. **With both new filters unchecked, it enters on each LC buy/sell signal within trading hours**, on the signal bar's close. It follows LC's default four-bar exit or its dynamic kernel exit option. Exits may happen after 15:00; this strategy does not automatically flatten at session end.

Two independent switches modify entries:

| Setting | When checked |
| --- | --- |
| Require consecutive LC color bars | Wait for the chosen number of consecutive LC prediction bars in the signal direction, counting the LC signal bar as bar 1 (default 4). If color or session breaks, discard the pending entry. |
| Require price slope in trade direction | Require linear-regression price slope normalized by ATR to meet the minimum threshold on the signal and, when color confirmation is on, each confirmation bar. |

The **Use stop and profit target** switch is off by default. When checked, entry-bar ATR × the selected multiplier defines **1R**. The stop is 1R away and the profit order is placed at the selected multiple (default 2R, adjustable to 3R). LC exit signals can still close the trade earlier. When unchecked, no R stop or target is placed. The LC-style trade box uses actual closed Strategy Tester trades and shows confirmation progress.

**Optional regular candle color exit:** Turn on **Exit after consecutive opposing candles** and set **Opposing candles to exit** (default 3). A red price candle counts against a long; a green price candle counts against a short. The counter starts at **0 on entry** and increments on each subsequent completed opposing candle. A candle in the trade direction or a doji resets it to 0. The trade closes when the count reaches the threshold. The trade box shows the current count. This uses regular `close` versus `open` candle colors, separate from LC prediction-bar colors; LC exits and an enabled R stop or target can still close a trade first.

## Kernel Swing Strategy

[`ARES_Kernel_Swing_Strategy_JXS.pine`](ARES_Kernel_Swing_Strategy_JXS.pine) trades the rational quadratic kernel line from jdehorty's Lorentzian Classification indicator. The default color changes with the line's slope; enable **Enhance Kernel Smoothing** to use the original Gaussian comparison instead. Lookback, relative weighting, regression level, lag, and source are configurable.

| Kernel changes | Strategy action |
| --- | --- |
| Red to green | Close an open short; start bullish entry confirmation |
| Green to red | Close an open long; start bearish entry confirmation |
| New color persists for the selected bar count | Enter in that direction if the confirmation bar closes within 09:30–15:00 |
| Change outside 09:30–15:00 | Close an opposite position, but start no new setup |
| Target or stop fills | Stay flat until the next color change |

**Bar confirmation:** The default is **4 consecutive completed bars** in the new kernel color (more than 3). The color-change bar counts as bar 1. Change **Consecutive color bars** to require a different number. A return to the opposite color or the end of the entry window cancels the pending setup. An existing trade still exits as soon as the color changes; it does not wait for the next entry to confirm.

Orders are placed on the final confirmation bar's close. The session limits **new entries**; open trades may continue past 15:00 or overnight until the next color change or an enabled stop/target. For precise session boundaries, use an intraday time based chart such as 1 minute or 5 minutes.

**Optional R target:** Disabled by default so trades follow the kernel until its color changes. When enabled, 1R is the ATR reading on the entry bar multiplied by the configurable stop distance (default: 14 period ATR × 1). A fixed stop is placed 1R from entry; the take profit is placed at the selected multiple (default **2R**, adjustable to **3R** or another value). These distances are in the underlying chart's price units, not option premium. A color change can close or reverse a position before either bracket order fills.

The compact LC-style trade box uses `size.normal`, the LC teal/red palette, and TradingView's **actual closed strategy trades** for win rate, trades, net P&L, profit factor, and win/loss ratio. “Early Color Flips” counts an opposite color change less than four bars after an open trade's entry. “Confirm” shows progress toward the next entry.

## Confirmation Engine

[`ARES_Redline_Engine_JXS.pine`](ARES_Redline_Engine_JXS.pine) is the indicator; [`ARES_Confirmation_Engine_Strategy_JXS.pine`](ARES_Confirmation_Engine_Strategy_JXS.pine) is its Strategy Tester version. The signal path is:

**BBSR arrow → consecutive LC and slope confirmations → BUY/SELL flag**

The BBSR arrow arms the setup. Starting on the following candle, each required confirmation bar must agree with the LC direction and meet an ATR normalized price slope threshold. The default confirmation count is two bars. The confirmation strategy uses a four bar maximum trade duration by default, with optional LC flip and session exits. Its alerts fire on the confirmed entry, not the initial BBSR arrow.

## Use

1. Open the desired `.pine` file and paste its entire contents into TradingView's Pine Editor.
2. Add it to an intraday chart. The strategies report results in **Strategy Tester**.
3. For LC trade signals, use the new LC Trade Strategy and leave its optional confirmation, slope, and R switches off to start with the original LC behavior. For the earlier kernel-only approach, use Kernel Swing Strategy.
4. Configure fees, slippage, and position size in TradingView's strategy properties for the instrument you trade.

The LC trade strategy imports `jdehorty/MLExtensions/2` and `jdehorty/KernelFunctions/2`; the other engines use the relevant published libraries. TradingView must have access to them. Backtests depend on chart bars and the broker emulator; they do not model option contract pricing. The optional R distances use the chart's underlying price.

## Files

- `ARES_LC_Trade_Strategy_JXS.pine` — LC signal strategy with optional color, slope, and R settings
- `ARES_Kernel_Swing_Strategy_JXS.pine` — kernel color-change strategy and LC-style trade box
- `ARES_Redline_Engine_JXS.pine` — BBSR/LC confirmation indicator
- `ARES_Confirmation_Engine_Strategy_JXS.pine` — confirmation strategy
- `ares_reference.py` and `requirements.txt` — Python research companion
- `THIRD_PARTY_NOTICES.md` and `LICENSE` — attribution and MPL 2.0

## Author

**JXS** · GitHub: [@woi-6ix](https://github.com/woi-6ix)

Based in part on Lorentzian Classification and kernel regression work by **jdehorty**. See [third-party notices](THIRD_PARTY_NOTICES.md). Licensed under [MPL 2.0](LICENSE).
