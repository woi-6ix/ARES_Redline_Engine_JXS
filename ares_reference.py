"""Python companion utilities for ARES Redline Engine.

This module mirrors a small, testable subset of the TradingView strategy's
price-slope logic. The production trading indicator remains the Pine Script
file; this Python module is intended for offline research and validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class AresSlopeConfig:
    """Default slope settings used by the ARES research helper."""

    slope_lookback: int = 5
    atr_length: int = 14
    min_normalized_slope: float = 0.05
    directional_lookback: int = 5
    min_matching_bars: int = 3


def true_range(high: float, low: float, previous_close: float) -> float:
    """Return Wilder true range for one bar."""

    return max(
        high - low,
        abs(high - previous_close),
        abs(low - previous_close),
    )


def simple_atr(
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    length: int = 14,
) -> float:
    """Return a simple ATR estimate over the latest *length* completed bars.

    This helper intentionally uses a simple mean so the calculation is easy
    to inspect during research. TradingView's ta.atr() uses Wilder smoothing.
    """

    if length < 1:
        raise ValueError("length must be >= 1")
    if not (len(highs) == len(lows) == len(closes)):
        raise ValueError("highs, lows, and closes must have equal length")
    if len(closes) < length + 1:
        raise ValueError("need at least length + 1 bars")

    start = len(closes) - length
    ranges = [
        true_range(highs[i], lows[i], closes[i - 1])
        for i in range(start, len(closes))
    ]
    return sum(ranges) / length


def atr_normalized_slope(
    closes: Sequence[float],
    atr_value: float,
    lookback: int = 5,
) -> float:
    """Return average price slope per bar divided by ATR."""

    if lookback < 1:
        raise ValueError("lookback must be >= 1")
    if len(closes) <= lookback:
        raise ValueError("not enough closing prices for lookback")
    if atr_value <= 0:
        raise ValueError("atr_value must be positive")

    slope_per_bar = (closes[-1] - closes[-1 - lookback]) / lookback
    return slope_per_bar / atr_value


def matching_directional_bars(
    closes: Sequence[float],
    lookback: int = 5,
) -> tuple[int, int]:
    """Count up-closes and down-closes across the latest lookback bars."""

    if lookback < 1:
        raise ValueError("lookback must be >= 1")
    if len(closes) <= lookback:
        raise ValueError("not enough closing prices for lookback")

    recent = closes[-(lookback + 1) :]
    up = sum(curr > prev for prev, curr in zip(recent, recent[1:]))
    down = sum(curr < prev for prev, curr in zip(recent, recent[1:]))
    return up, down


def slope_state(
    normalized_slope: float,
    threshold: float = 0.05,
) -> str:
    """Classify the ARES slope state as G+, G-, or neutral."""

    if normalized_slope >= threshold:
        return "G+"
    if normalized_slope <= -threshold:
        return "G-"
    return "NEUTRAL"


if __name__ == "__main__":
    defaults = AresSlopeConfig()
    print("ARES Redline Engine — Python research companion")
    print(defaults)
