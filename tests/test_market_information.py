"""Unit tests of the market information estimator (src/market_information.py)."""

import numpy as np
import pytest

from src.market_information import (
    binary_returns,
    gamma_params,
    gray_code_sequences,
    market_information,
    market_information_from_counts,
    prefix_counts,
    simulate_emh_sequences,
)


def test_gray_code_sequences_L1():
    assert gray_code_sequences(1) == [(0,), (1,)]


def test_gray_code_sequences_L2():
    assert gray_code_sequences(2) == [(0, 0), (0, 1), (1, 1), (1, 0)]


def test_binary_returns_signs():
    prices = np.array([100.0, 101.0, 99.0, 99.0, 102.0])
    X = binary_returns(prices)
    # increases: 100->101 (1), 101->99 (0), 99->99 (0, not strictly >), 99->102 (1)
    assert list(X) == [1, 0, 0, 1]


def test_binary_returns_rejects_short_series():
    with pytest.raises(ValueError):
        binary_returns(np.array([100.0]))


def test_simulate_emh_sequences_shape_and_range():
    rng = np.random.default_rng(1)
    X = simulate_emh_sequences(50, 1, 20, rng)
    assert X.shape == (20, 51)
    assert set(np.unique(X)).issubset({0, 1})


def test_simulate_emh_sequences_mean_near_half():
    rng = np.random.default_rng(1)
    X = simulate_emh_sequences(5000, 1, 1, rng)
    assert abs(X.mean() - 0.5) < 0.03


def test_prefix_counts_L1_exact():
    # X = 0,1,1,0,1 -> windows of length 2: (0,1),(1,1),(1,0),(0,1)
    X = np.array([0, 1, 1, 0, 1])
    n, counts_n, counts_suffix1 = prefix_counts(X, 1)
    assert n == 4
    # prefix 0 occurs twice (positions giving (0,1) and (0,1)); prefix 1 occurs twice
    assert counts_n[0] == 2
    assert counts_n[1] == 2
    # suffix=1 given prefix 0: both occurrences have suffix 1 -> 2
    assert counts_suffix1[0] == 2
    # suffix=1 given prefix 1: (1,1) suffix 1, (1,0) suffix 0 -> 1
    assert counts_suffix1[1] == 1


def test_market_information_nonnegative_and_zero_for_constant_alternation():
    """I_hat >= 0 always (Sec. 3.1): H*^{L+1} >= H^{L+1} since conditioning
    on one more past value cannot increase entropy in this construction."""
    rng = np.random.default_rng(2)
    for _ in range(20):
        X = rng.integers(0, 2, size=200)
        res = market_information(X, 1)
        assert res["I_hat"] >= -1e-10


def test_market_information_perfectly_predictable_sequence():
    """A perfectly alternating sequence (0,1,0,1,...) has pi_hat in {0,1}
    for every prefix, which should yield a much larger I_hat than a random
    sequence of the same length."""
    X_alt = np.tile([0, 1], 100)
    X_rand = np.random.default_rng(3).integers(0, 2, size=200)
    res_alt = market_information(X_alt, 1)
    res_rand = market_information(X_rand, 1)
    assert res_alt["I_hat"] > res_rand["I_hat"]


def test_market_information_from_counts_matches_direct_path():
    rng = np.random.default_rng(4)
    X = rng.integers(0, 2, size=300)
    n, counts_n, counts_suffix1 = prefix_counts(X, 2)
    res1 = market_information_from_counts(n, counts_n, counts_suffix1)
    res2 = market_information(X, 2)
    assert np.isclose(res1["I_hat"], res2["I_hat"])


def test_gamma_params_L1():
    k, theta = gamma_params(1, 100)
    assert k == 1.0
    assert np.isclose(theta, 1.0 / (np.log(2) * 100))


def test_gamma_params_L2():
    k, theta = gamma_params(2, 4000)
    assert k == 2.0
    assert np.isclose(theta, 1.0 / (np.log(2) * 4000))


def test_prefix_counts_rejects_too_short_sequence():
    with pytest.raises(ValueError):
        prefix_counts(np.array([0, 1]), 5)
