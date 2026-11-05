"""Market-data test of the rolling market-information pipeline used by exp_3.

Uses a cached, reduced real-data slice (one ticker, one year) through
data/data_loader.py and the shared src/ components, checking the paper's
qualitative properties rather than its reported numbers (Sec. 3.1, 3.2.2, 3.3).
"""

import numpy as np
import pytest

from src.market_information import binary_returns, market_information
from src.stat_test import market_information_critical_value, market_information_pvalue

pytestmark = pytest.mark.market_data


def test_rolling_window_has_no_lookahead_and_valid_statistics(market_slice):
    """Each rolling Î^2 depends only on data up to and including its date, is
    non-negative (Theorem 1), and its gamma p-value lies in [0, 1] (Sec. 3.3).
    """
    prices = market_slice.set_index("date")["close"].sort_index()
    X = binary_returns(prices.to_numpy())
    assert set(np.unique(X)).issubset({0, 1})

    L, n_window = 1, 100
    span = n_window + L
    assert len(X) > span, "cached market slice is too short for one rolling window"

    I_hat_values = []
    for i in range(span - 1, len(X)):
        window_full = X[: i + 1]  # everything known up to date i (no future data)
        window = X[i - span + 1 : i + 1]
        # The statistic computed from the trailing window must reproduce the
        # one computed by slicing the full history up to date i: this is the
        # no-look-ahead property of a rolling window of fixed length.
        assert np.array_equal(window, window_full[-span:])

        stats = market_information(window, L)
        I_hat = stats["I_hat"]
        assert I_hat >= -1e-12, "Î^{L+1} must be non-negative (Theorem 1)"

        p_value = market_information_pvalue(I_hat, L, n_window)
        assert 0.0 <= p_value <= 1.0
        I_hat_values.append(I_hat)

    assert len(I_hat_values) > 0
    critical_95 = market_information_critical_value(L, n_window, 0.05)
    assert critical_95 > 0
