# ARES LC Strategy [JXS] - QuantConnect LEAN Python
# LC feature engine adapted from jdehorty (MPL-2.0).
# Original Pine: https://mozilla.org/MPL/2.0/
from AlgorithmImports import *
from collections import deque
from datetime import timedelta, time
from math import exp, log, sqrt
import numpy as np

class PineEMA:
    """Streaming EMA. Pine's recursive form is seeded from the first valid value."""

    def __init__(self, length):
        self.length = int(length)
        self.alpha = 2.0 / (self.length + 1.0)
        self.value = None

    def update(self, x):
        if x is None or np.isnan(x):
            return self.value
        x = float(x)
        if self.value is None:
            self.value = x
        else:
            self.value = self.alpha * x + (1.0 - self.alpha) * self.value
        return self.value

class PineSMA:
    def __init__(self, length):
        self.length = int(length)
        self.window = deque(maxlen=self.length)
        self.total = 0.0

    def update(self, x):
        if x is None or np.isnan(x):
            return None
        x = float(x)
        if len(self.window) == self.length:
            self.total -= self.window[0]
        self.window.append(x)
        self.total += x
        if len(self.window) < self.length:
            return None
        return self.total / self.length

class PineRMA:
    """Wilder RMA: SMA seed, then (prev*(n-1)+x)/n."""

    def __init__(self, length):
        self.length = int(length)
        self.seed = deque(maxlen=self.length)
        self.value = None

    def update(self, x):
        if x is None or np.isnan(x):
            return self.value
        x = float(x)
        if self.value is None:
            self.seed.append(x)
            if len(self.seed) < self.length:
                return None
            self.value = sum(self.seed) / self.length
        else:
            self.value = ((self.length - 1.0) * self.value + x) / self.length
        return self.value

class RunningNormalizer:
    """MLExtensions normalize(): causal running historic min/max -> 0..1."""

    def __init__(self):
        self.historic_min = 1e11
        self.historic_max = -1e11

    def update(self, x):
        if x is None or np.isnan(x):
            return None
        x = float(x)
        self.historic_min = min(self.historic_min, x)
        self.historic_max = max(self.historic_max, x)
        den = max(self.historic_max - self.historic_min, 1e-10)
        return (x - self.historic_min) / den

class RSIState:
    def __init__(self, length):
        self.prev = None
        self.avg_gain = PineRMA(length)
        self.avg_loss = PineRMA(length)

    def update(self, close):
        close = float(close)
        if self.prev is None:
            self.prev = close
            return None
        change = close - self.prev
        self.prev = close
        gain = max(change, 0.0)
        loss = max(-change, 0.0)
        ag = self.avg_gain.update(gain)
        al = self.avg_loss.update(loss)
        if ag is None or al is None:
            return None
        if al == 0:
            return 100.0
        if ag == 0:
            return 0.0
        rs = ag / al
        return 100.0 - 100.0 / (1.0 + rs)

class NormalizedRSI:
    def __init__(self, n1, n2):
        self.rsi = RSIState(n1)
        self.ema = PineEMA(n2)

    def update(self, close):
        value = self.rsi.update(close)
        value = self.ema.update(value)
        if value is None:
            return None
        return value / 100.0

class NormalizedCCI:
    def __init__(self, n1, n2):
        self.length = int(n1)
        self.window = deque(maxlen=self.length)
        self.ema = PineEMA(n2)
        self.norm = RunningNormalizer()

    def update(self, src):
        src = float(src)
        self.window.append(src)
        if len(self.window) < self.length:
            return None
        vals = list(self.window)
        sma = sum(vals) / self.length
        dev = sum(abs(v - sma) for v in vals) / self.length
        if dev == 0:
            cci = 0.0
        else:
            cci = (src - sma) / (0.015 * dev)
        smoothed = self.ema.update(cci)
        return self.norm.update(smoothed)

class NormalizedWaveTrend:
    def __init__(self, n1, n2):
        self.ema1 = PineEMA(n1)
        self.ema2 = PineEMA(n1)
        self.wt1_ema = PineEMA(n2)
        self.wt1_sma = PineSMA(4)
        self.norm = RunningNormalizer()

    def update(self, src):
        src = float(src)
        ema1 = self.ema1.update(src)
        if ema1 is None:
            return None
        ema2 = self.ema2.update(abs(src - ema1))
        if ema2 is None or ema2 == 0:
            return None
        ci = (src - ema1) / (0.015 * ema2)
        wt1 = self.wt1_ema.update(ci)
        if wt1 is None:
            return None
        wt2 = self.wt1_sma.update(wt1)
        if wt2 is None:
            return None
        return self.norm.update(wt1 - wt2)

class ADXState:
    """jdehorty MLExtensions directional-movement recursion + Wilder RMA DX."""

    def __init__(self, length):
        self.length = int(length)
        self.prev_high = None
        self.prev_low = None
        self.prev_close = None
        self.tr_smooth = 0.0
        self.dm_plus_smooth = 0.0
        self.dm_minus_smooth = 0.0
        self.dx_rma = PineRMA(length)

    def update(self, high, low, close):
        high = float(high)
        low = float(low)
        close = float(close)

        if self.prev_close is None:
            tr = high - low
            up_move = 0.0
            down_move = 0.0
        else:
            tr = max(
                high - low,
                abs(high - self.prev_close),
                abs(low - self.prev_close),
            )
            up = high - self.prev_high
            down = self.prev_low - low
            up_move = max(up, 0.0) if up > down else 0.0
            down_move = max(down, 0.0) if down > up else 0.0

        self.tr_smooth = self.tr_smooth - self.tr_smooth / self.length + tr
        self.dm_plus_smooth = (
            self.dm_plus_smooth - self.dm_plus_smooth / self.length + up_move
        )
        self.dm_minus_smooth = (
            self.dm_minus_smooth - self.dm_minus_smooth / self.length + down_move
        )

        self.prev_high = high
        self.prev_low = low
        self.prev_close = close

        if self.tr_smooth == 0:
            return None

        di_plus = self.dm_plus_smooth / self.tr_smooth * 100.0
        di_minus = self.dm_minus_smooth / self.tr_smooth * 100.0
        di_sum = di_plus + di_minus
        dx = 0.0 if di_sum == 0 else abs(di_plus - di_minus) / di_sum * 100.0
        return self.dx_rma.update(dx)

class ATRState:
    def __init__(self, length):
        self.prev_close = None
        self.rma = PineRMA(length)

    def update(self, high, low, close):
        high = float(high)
        low = float(low)
        close = float(close)
        if self.prev_close is None:
            tr = high - low
        else:
            tr = max(
                high - low,
                abs(high - self.prev_close),
                abs(low - self.prev_close),
            )
        self.prev_close = close
        return self.rma.update(tr)

class RegimeFilterState:
    """MLExtensions KLMF regime filter used by the LC indicator."""

    def __init__(self, threshold=-0.1):
        self.threshold = float(threshold)
        self.prev_src = None
        self.value1 = 0.0
        self.value2 = 0.0
        self.klmf = 0.0
        self.prev_klmf = None
        self.slope_ema = PineEMA(200)

    def update(self, src, high, low):
        src = float(src)
        high = float(high)
        low = float(low)

        ds = 0.0 if self.prev_src is None else src - self.prev_src
        self.value1 = 0.2 * ds + 0.8 * self.value1
        self.value2 = 0.1 * (high - low) + 0.8 * self.value2
        omega = abs(self.value1 / self.value2) if self.value2 != 0 else 0.0
        alpha = (-(omega ** 2) + sqrt(omega ** 4 + 16.0 * omega ** 2)) / 8.0

        old_klmf = self.klmf
        self.klmf = alpha * src + (1.0 - alpha) * self.klmf
        self.prev_src = src

        if self.prev_klmf is None:
            self.prev_klmf = old_klmf
        abs_curve_slope = abs(self.klmf - self.prev_klmf)
        self.prev_klmf = self.klmf

        exp_avg = self.slope_ema.update(abs_curve_slope)
        if exp_avg is None or exp_avg == 0:
            return False
        normalized_slope_decline = (abs_curve_slope - exp_avg) / exp_avg
        return normalized_slope_decline >= self.threshold

class AresLCSpyQuantConnect(QCAlgorithm):

    START_YEAR = 2024
    START_MONTH = 1
    START_DAY = 1

    END_YEAR = 2026
    END_MONTH = 9
    END_DAY = 25

    INITIAL_CASH = 10000

    NEIGHBORS_COUNT = 3
    MAX_BARS_BACK = 2000
    INCLUDE_FULL_HISTORY = True

    USE_VOLATILITY_FILTER = True
    USE_REGIME_FILTER = True
    REGIME_THRESHOLD = -0.1
    USE_ADX_FILTER = False
    ADX_FILTER_THRESHOLD = 20

    USE_EMA_FILTER = True
    EMA_PERIOD = 200
    USE_SMA_FILTER = True
    SMA_PERIOD = 200

    USE_KERNEL_FILTER = True
    USE_KERNEL_SMOOTHING = False
    KERNEL_H = 8
    KERNEL_R = 8.0
    KERNEL_X = 25
    KERNEL_LAG = 1

    USE_COLOR_CONFIRMATION = False
    CONFIRMATION_BARS = 2

    USE_SLOPE_FILTER = False

    USE_R_TARGET = True
    ATR_LENGTH = 14
    STOP_ATR_MULTIPLIER = 1.0
    REWARD_MULTIPLE = 2.0

    USE_CANDLE_COLOR_EXIT = True
    OPPOSING_CANDLES_REQUIRED = 2

    USE_DYNAMIC_EXITS = True
    FORCE_DYNAMIC_EXITS_WITH_TREND_FILTERS = False

    ENTRY_START = time(9, 30)
    ENTRY_END = time(12, 49)

    FLATTEN_AT_1249 = False

    def initialize(self):
        self.set_start_date(self.START_YEAR, self.START_MONTH, self.START_DAY)
        self.set_end_date(self.END_YEAR, self.END_MONTH, self.END_DAY)
        self.set_cash(self.INITIAL_CASH)
        self.set_time_zone("America/New_York")

        security = self.add_equity(
            "SPY",
            Resolution.MINUTE,
            extended_market_hours=False,
            data_normalization_mode=DataNormalizationMode.RAW,
        )
        self.spy = security.symbol

        security.set_fee_model(ConstantFeeModel(0, "USD"))
        security.set_slippage_model(NullSlippageModel.INSTANCE)

        self.consolidate(self.spy, timedelta(minutes=2), self._on_two_minute_bar)

        self.set_warm_up(timedelta(days=30), Resolution.MINUTE)

        if self.FLATTEN_AT_1249:
            self.schedule.on(
                self.date_rules.every_day(self.spy),
                self.time_rules.at(12, 49),
                self._flatten_at_session_end,
            )

        self._reset_model_state()

    def _reset_model_state(self):
        self.bar_index = -1
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []

        self.f1_state = NormalizedRSI(14, 1)
        self.f2_state = NormalizedWaveTrend(10, 11)
        self.f3_state = NormalizedCCI(20, 1)
        self.f4_state = ADXState(20)
        self.f5_state = NormalizedRSI(9, 1)

        self.feature_rows = []
        self.training_labels = []
        self._feature_matrix_cache = None

        self.ann_distances = []
        self.ann_predictions = []
        self.prediction = 0.0

        self.atr1_state = ATRState(1)
        self.atr10_state = ATRState(10)
        self.atr14_state = ATRState(self.ATR_LENGTH)
        self.regime_state = RegimeFilterState(self.REGIME_THRESHOLD)
        self.adx_filter_state = ADXState(14)

        self.ema200 = PineEMA(self.EMA_PERIOD)
        self.sma200 = PineSMA(self.SMA_PERIOD)

        self.signal = 0
        self.bars_held = 0

        self.signal_history = []
        self.ema_up_history = []
        self.ema_down_history = []
        self.sma_up_history = []
        self.sma_down_history = []
        self.lc_long_history = []
        self.lc_short_history = []
        self.yhat1_history = []

        self.bars_since_lc_long = None
        self.bars_since_lc_short = None
        self.bars_since_bullish_change = None
        self.bars_since_bearish_change = None
        self.prev_valid_long_exit = False
        self.prev_valid_short_exit = False

        self.last_entry_bar = None
        self.opposing_candle_count = 0
        self.stop_ticket = None
        self.target_ticket = None
        self.pending_entry = None
        self.current_direction = 0

    def _on_two_minute_bar(self, bar: TradeBar):
        self.bar_index += 1

        o = float(bar.open)
        h = float(bar.high)
        l = float(bar.low)
        c = float(bar.close)

        self.opens.append(o)
        self.highs.append(h)
        self.lows.append(l)
        self.closes.append(c)

        hlc3 = (h + l + c) / 3.0
        ohlc4 = (o + h + l + c) / 4.0

        f1 = self.f1_state.update(c)
        f2 = self.f2_state.update(hlc3)
        f3 = self.f3_state.update(c)
        adx20 = self.f4_state.update(h, l, c)
        f4 = None if adx20 is None else adx20 / 100.0
        f5 = self.f5_state.update(c)

        row = [f1, f2, f3, f4, f5]
        self.feature_rows.append(row)

        if len(self.closes) >= 5:
            c4 = self.closes[-5]
            label = -1 if c4 < c else (1 if c4 > c else 0)
        else:
            label = 0
        self.training_labels.append(label)

        atr1 = self.atr1_state.update(h, l, c)
        atr10 = self.atr10_state.update(h, l, c)
        atr14 = self.atr14_state.update(h, l, c)

        volatility_ok = True
        if self.USE_VOLATILITY_FILTER:
            volatility_ok = (
                atr1 is not None and atr10 is not None and atr1 > atr10
            )

        regime_ok = True
        if self.USE_REGIME_FILTER:
            regime_ok = self.regime_state.update(ohlc4, h, l)

        adx_filter_value = self.adx_filter_state.update(h, l, c)
        adx_ok = True
        if self.USE_ADX_FILTER:
            adx_ok = (
                adx_filter_value is not None
                and adx_filter_value > self.ADX_FILTER_THRESHOLD
            )

        filter_all = volatility_ok and regime_ok and adx_ok

        ema_value = self.ema200.update(c)
        sma_value = self.sma200.update(c)

        ema_up = (not self.USE_EMA_FILTER) or (
            ema_value is not None and c > ema_value
        )
        ema_down = (not self.USE_EMA_FILTER) or (
            ema_value is not None and c < ema_value
        )
        sma_up = (not self.USE_SMA_FILTER) or (
            sma_value is not None and c > sma_value
        )
        sma_down = (not self.USE_SMA_FILTER) or (
            sma_value is not None and c < sma_value
        )

        yhat1 = self._kernel_rational_quadratic(
            self.KERNEL_H, self.KERNEL_R, self.KERNEL_X
        )
        yhat2 = self._kernel_gaussian(
            self.KERNEL_H - self.KERNEL_LAG, self.KERNEL_X
        )

        prev_yhat1 = self.yhat1_history[-1] if self.yhat1_history else None
        two_back_yhat1 = (
            self.yhat1_history[-2] if len(self.yhat1_history) >= 2 else None
        )

        bullish_rate = (
            yhat1 is not None and prev_yhat1 is not None and yhat1 > prev_yhat1
        )
        bearish_rate = (
            yhat1 is not None and prev_yhat1 is not None and yhat1 < prev_yhat1
        )
        bullish_change = (
            bullish_rate
            and two_back_yhat1 is not None
            and two_back_yhat1 > prev_yhat1
        )
        bearish_change = (
            bearish_rate
            and two_back_yhat1 is not None
            and two_back_yhat1 < prev_yhat1
        )

        bullish_smooth = (
            yhat1 is not None and yhat2 is not None and yhat2 >= yhat1
        )
        bearish_smooth = (
            yhat1 is not None and yhat2 is not None and yhat2 <= yhat1
        )

        if not self.USE_KERNEL_FILTER:
            kernel_bull = True
            kernel_bear = True
        elif self.USE_KERNEL_SMOOTHING:
            kernel_bull = bullish_smooth
            kernel_bear = bearish_smooth
        else:
            kernel_bull = bullish_rate
            kernel_bear = bearish_rate

        self.prediction = self._lc_prediction(row)

        previous_signal = self.signal
        if self.prediction > 0 and filter_all:
            self.signal = 1
        elif self.prediction < 0 and filter_all:
            self.signal = -1

        signal_changed = self.signal != previous_signal
        self.bars_held = 0 if signal_changed else self.bars_held + 1

        is_held_four_bars = self.bars_held == 4
        is_held_less_than_four = 0 < self.bars_held < 4

        new_buy_signal = self.signal == 1 and ema_up and sma_up and signal_changed
        new_sell_signal = self.signal == -1 and ema_down and sma_down and signal_changed

        lc_long = new_buy_signal and kernel_bull and ema_up and sma_up
        lc_short = new_sell_signal and kernel_bear and ema_down and sma_down

        if len(self.signal_history) >= 4:
            last_signal_buy = (
                self.signal_history[-4] == 1
                and self.ema_up_history[-4]
                and self.sma_up_history[-4]
            )
            last_signal_sell = (
                self.signal_history[-4] == -1
                and self.ema_down_history[-4]
                and self.sma_down_history[-4]
            )
            lc_long_4 = self.lc_long_history[-4]
            lc_short_4 = self.lc_short_history[-4]
        else:
            last_signal_buy = False
            last_signal_sell = False
            lc_long_4 = False
            lc_short_4 = False

        strict_long_exit = (
            (
                (is_held_four_bars and last_signal_buy)
                or (
                    is_held_less_than_four
                    and new_sell_signal
                    and last_signal_buy
                )
            )
            and lc_long_4
        )

        strict_short_exit = (
            (
                (is_held_four_bars and last_signal_sell)
                or (
                    is_held_less_than_four
                    and new_buy_signal
                    and last_signal_sell
                )
            )
            and lc_short_4
        )

        self.bars_since_lc_long = self._update_barssince(
            self.bars_since_lc_long, lc_long
        )
        self.bars_since_lc_short = self._update_barssince(
            self.bars_since_lc_short, lc_short
        )
        self.bars_since_bullish_change = self._update_barssince(
            self.bars_since_bullish_change, bullish_change
        )
        self.bars_since_bearish_change = self._update_barssince(
            self.bars_since_bearish_change, bearish_change
        )

        valid_long_exit = self._bars_since_gt(
            self.bars_since_bearish_change, self.bars_since_lc_long
        )
        valid_short_exit = self._bars_since_gt(
            self.bars_since_bullish_change, self.bars_since_lc_short
        )

        dynamic_long_exit = bearish_change and self.prev_valid_long_exit
        dynamic_short_exit = bullish_change and self.prev_valid_short_exit

        dynamic_allowed = (
            self.USE_DYNAMIC_EXITS
            and not self.USE_KERNEL_SMOOTHING
            and (
                self.FORCE_DYNAMIC_EXITS_WITH_TREND_FILTERS
                or (not self.USE_EMA_FILTER and not self.USE_SMA_FILTER)
            )
        )

        long_lc_exit = dynamic_long_exit if dynamic_allowed else strict_long_exit
        short_lc_exit = dynamic_short_exit if dynamic_allowed else strict_short_exit

        self.prev_valid_long_exit = valid_long_exit
        self.prev_valid_short_exit = valid_short_exit

        bar_time = bar.end_time.time()
        entry_window = self.ENTRY_START <= bar_time <= self.ENTRY_END

        enter_long = (
            entry_window
            and atr14 is not None
            and lc_long
            and (not self.USE_SLOPE_FILTER)
        )
        enter_short = (
            entry_window
            and atr14 is not None
            and lc_short
            and (not self.USE_SLOPE_FILTER)
        )

        invested = self.portfolio[self.spy].invested
        is_long_position = self.portfolio[self.spy].is_long
        is_short_position = self.portfolio[self.spy].is_short

        if (
            not invested
            or enter_long
            or enter_short
            or self.last_entry_bar is None
            or self.bar_index <= self.last_entry_bar
        ):
            self.opposing_candle_count = 0
        elif is_long_position:
            self.opposing_candle_count = (
                self.opposing_candle_count + 1 if c < o else 0
            )
        elif is_short_position:
            self.opposing_candle_count = (
                self.opposing_candle_count + 1 if c > o else 0
            )

        opposing_long_exit = (
            self.USE_CANDLE_COLOR_EXIT
            and is_long_position
            and self.opposing_candle_count >= self.OPPOSING_CANDLES_REQUIRED
        )
        opposing_short_exit = (
            self.USE_CANDLE_COLOR_EXIT
            and is_short_position
            and self.opposing_candle_count >= self.OPPOSING_CANDLES_REQUIRED
        )

        self.signal_history.append(self.signal)
        self.ema_up_history.append(bool(ema_up))
        self.ema_down_history.append(bool(ema_down))
        self.sma_up_history.append(bool(sma_up))
        self.sma_down_history.append(bool(sma_down))
        self.lc_long_history.append(bool(lc_long))
        self.lc_short_history.append(bool(lc_short))
        self.yhat1_history.append(yhat1)

        for arr in [
            self.signal_history,
            self.ema_up_history,
            self.ema_down_history,
            self.sma_up_history,
            self.sma_down_history,
            self.lc_long_history,
            self.lc_short_history,
            self.yhat1_history,
        ]:
            if len(arr) > 20:
                del arr[0]

        if self.is_warming_up:
            return

        if self.portfolio[self.spy].is_long and not enter_short:
            if long_lc_exit or opposing_long_exit:
                reason = "2 opposing red candles" if opposing_long_exit else "LC exit"
                self._exit_position(reason)

        if self.portfolio[self.spy].is_short and not enter_long:
            if short_lc_exit or opposing_short_exit:
                reason = "2 opposing green candles" if opposing_short_exit else "LC exit"
                self._exit_position(reason)

        if enter_long:
            self._enter_position(1, atr14, "ARES LC LONG")
        elif enter_short:
            self._enter_position(-1, atr14, "ARES LC SHORT")

    def _lc_prediction(self, current_features):
        if any(v is None or np.isnan(v) for v in current_features):
            return self.prediction

        current_index = len(self.feature_rows) - 1

        if self.INCLUDE_FULL_HISTORY:
            start = 0
            end = min(self.MAX_BARS_BACK - 1, current_index)
        else:
            start = max(0, current_index - self.MAX_BARS_BACK + 1)
            end = current_index

        if end < start:
            return self.prediction

        if (
            self.INCLUDE_FULL_HISTORY
            and end == self.MAX_BARS_BACK - 1
            and self._feature_matrix_cache is None
        ):
            matrix = np.array(self.feature_rows[: self.MAX_BARS_BACK], dtype=float)
            self._feature_matrix_cache = matrix

        if (
            self.INCLUDE_FULL_HISTORY
            and self._feature_matrix_cache is not None
            and end == self.MAX_BARS_BACK - 1
        ):
            matrix = self._feature_matrix_cache
            base_index = 0
        else:
            matrix = np.array(self.feature_rows[start : end + 1], dtype=float)
            base_index = start

        cur = np.array(current_features, dtype=float)
        valid_rows = ~np.isnan(matrix).any(axis=1)
        dists = np.full(matrix.shape[0], np.nan)
        if valid_rows.any():
            dists[valid_rows] = np.log1p(np.abs(matrix[valid_rows] - cur)).sum(axis=1)

        last_distance = -1.0
        quart_index = int(round(self.NEIGHBORS_COUNT * 3.0 / 4.0))

        for local_i, d in enumerate(dists):
            i = base_index + local_i
            if np.isnan(d) or i % 4 == 0:
                continue
            if d >= last_distance:
                last_distance = float(d)
                self.ann_distances.append(float(d))
                self.ann_predictions.append(int(self.training_labels[i]))

                if len(self.ann_predictions) > self.NEIGHBORS_COUNT:
                    if quart_index < len(self.ann_distances):
                        last_distance = self.ann_distances[quart_index]
                    self.ann_distances.pop(0)
                    self.ann_predictions.pop(0)

        return float(sum(self.ann_predictions)) if self.ann_predictions else 0.0

    def _kernel_rational_quadratic(self, lookback, relative_weight, start_at_bar):
        count = start_at_bar + 2
        if len(self.closes) < count:
            return None
        num = 0.0
        den = 0.0
        for i in range(count):
            y = self.closes[-1 - i]
            w = (1.0 + (i * i) / (lookback * lookback * 2.0 * relative_weight)) ** (
                -relative_weight
            )
            num += y * w
            den += w
        return None if den == 0 else num / den

    def _kernel_gaussian(self, lookback, start_at_bar):
        if lookback <= 0:
            return None
        count = start_at_bar + 2
        if len(self.closes) < count:
            return None
        num = 0.0
        den = 0.0
        for i in range(count):
            y = self.closes[-1 - i]
            w = exp(-(i * i) / (2.0 * lookback * lookback))
            num += y * w
            den += w
        return None if den == 0 else num / den

    def _enter_position(self, direction, atr_value, tag):
        if atr_value is None or atr_value <= 0:
            return

        if direction == 1 and self.portfolio[self.spy].is_long:
            return
        if direction == -1 and self.portfolio[self.spy].is_short:
            return

        self._cancel_protection("New LC reversal/entry")

        if self.portfolio[self.spy].invested:
            self.liquidate(self.spy, tag="ARES reversal close")

        target_weight = 1.0 if direction == 1 else -1.0
        qty = self.calculate_order_quantity(self.spy, target_weight)
        if qty == 0:
            return

        risk_distance = max(
            float(atr_value) * self.STOP_ATR_MULTIPLIER,
            float(self.securities[self.spy].symbol_properties.minimum_price_variation),
        )

        ticket = self.market_order(self.spy, qty, tag=tag)
        self.pending_entry = {
            "order_id": ticket.order_id,
            "direction": direction,
            "risk_distance": risk_distance,
        }

        if ticket.status == OrderStatus.FILLED:
            self._arm_bracket(direction, float(ticket.average_fill_price), risk_distance)
            self.pending_entry = None

    def _arm_bracket(self, direction, entry_price, risk_distance):
        if not self.USE_R_TARGET:
            self.last_entry_bar = self.bar_index
            self.opposing_candle_count = 0
            self.current_direction = direction
            return

        quantity = int(self.portfolio[self.spy].quantity)
        if quantity == 0:
            return

        if direction == 1:
            stop_price = entry_price - risk_distance
            target_price = entry_price + risk_distance * self.REWARD_MULTIPLE
        else:
            stop_price = entry_price + risk_distance
            target_price = entry_price - risk_distance * self.REWARD_MULTIPLE

        exit_qty = -quantity
        self.stop_ticket = self.stop_market_order(
            self.spy,
            exit_qty,
            stop_price,
            tag="ARES 1R ATR stop",
        )
        self.target_ticket = self.limit_order(
            self.spy,
            exit_qty,
            target_price,
            tag=f"ARES {self.REWARD_MULTIPLE:.2f}R target",
        )

        self.last_entry_bar = self.bar_index
        self.opposing_candle_count = 0
        self.current_direction = direction

    def _exit_position(self, reason):
        if not self.portfolio[self.spy].invested:
            return
        self._cancel_protection(reason)
        self.liquidate(self.spy, tag=reason)
        self.opposing_candle_count = 0
        self.current_direction = 0

    def _cancel_protection(self, reason):
        for ticket in [self.stop_ticket, self.target_ticket]:
            if ticket is not None and ticket.status in [
                OrderStatus.NEW,
                OrderStatus.SUBMITTED,
                OrderStatus.PARTIALLY_FILLED,
            ]:
                ticket.cancel(reason)
        self.stop_ticket = None
        self.target_ticket = None

    def on_order_event(self, order_event: OrderEvent):
        if order_event.status != OrderStatus.FILLED:
            return

        if (
            self.pending_entry is not None
            and order_event.order_id == self.pending_entry["order_id"]
        ):
            direction = self.pending_entry["direction"]
            risk_distance = self.pending_entry["risk_distance"]
            self._arm_bracket(direction, float(order_event.fill_price), risk_distance)
            self.pending_entry = None
            return

        stop_id = self.stop_ticket.order_id if self.stop_ticket is not None else None
        target_id = self.target_ticket.order_id if self.target_ticket is not None else None

        if order_event.order_id == stop_id:
            if self.target_ticket is not None and self.target_ticket.status in [
                OrderStatus.NEW,
                OrderStatus.SUBMITTED,
                OrderStatus.PARTIALLY_FILLED,
            ]:
                self.target_ticket.cancel("Stop filled - cancel target")
            self.stop_ticket = None
            self.target_ticket = None
            self.current_direction = 0
            self.opposing_candle_count = 0

        elif order_event.order_id == target_id:
            if self.stop_ticket is not None and self.stop_ticket.status in [
                OrderStatus.NEW,
                OrderStatus.SUBMITTED,
                OrderStatus.PARTIALLY_FILLED,
            ]:
                self.stop_ticket.cancel("Target filled - cancel stop")
            self.stop_ticket = None
            self.target_ticket = None
            self.current_direction = 0
            self.opposing_candle_count = 0

    @staticmethod
    def _update_barssince(previous_count, condition):
        if condition:
            return 0
        if previous_count is None:
            return None
        return previous_count + 1

    @staticmethod
    def _bars_since_gt(a, b):
        if a is None or b is None:
            return False
        return a > b

    def _flatten_at_session_end(self):
        if self.is_warming_up:
            return
        if self.portfolio[self.spy].invested:
            self._exit_position("12:49 session flatten")
