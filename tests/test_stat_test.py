"""Unit tests of the gamma-based statistical test (src/stat_test.py)."""

import numpy as np
from scipy.stats import gamma

from src.stat_test import (
    gamma_cdf,
    gamma_pdf,
    market_information_critical_value,
    market_information_pvalue,
)


def test_pvalue_at_zero_is_one():
    assert np.isclose(market_information_pvalue(0.0, 1, 100), 1.0)


def test_pvalue_decreases_with_statistic():
    p_small = market_information_pvalue(0.01, 1, 100)
    p_large = market_information_pvalue(0.05, 1, 100)
    assert p_large < p_small


def test_pvalue_in_unit_interval():
    for I_hat in [0.0, 0.001, 0.01, 0.1, 1.0, 10.0]:
        p = market_information_pvalue(I_hat, 1, 100)
        assert 0.0 <= p <= 1.0


def test_critical_value_ordering():
    """Critical values must increase as the p-value threshold shrinks
    (Sec. 3.3, Figure 5: 5% line below 1% below 0.1%)."""
    q95 = market_information_critical_value(1, 100, 0.05)
    q99 = market_information_critical_value(1, 100, 0.01)
    q999 = market_information_critical_value(1, 100, 0.001)
    assert q95 < q99 < q999


def test_critical_value_matches_exponential_closed_form_L1():
    """For L=1 the gamma distribution is exponential with rate ln(2) n, so
    q_alpha = -ln(alpha) / (ln(2) n) exactly (implementation_notes)."""
    n = 250
    for alpha in [0.05, 0.01, 0.001]:
        q = market_information_critical_value(1, n, alpha)
        closed_form = -np.log(alpha) / (np.log(2.0) * n)
        assert np.isclose(q, closed_form, rtol=1e-9)


def test_critical_value_decreases_with_n():
    q_100 = market_information_critical_value(1, 100, 0.05)
    q_1000 = market_information_critical_value(1, 1000, 0.05)
    assert q_1000 < q_100


def test_gamma_pdf_cdf_consistency_with_scipy():
    x = np.linspace(0.0001, 0.2, 50)
    pdf = gamma_pdf(x, 1, 100)
    cdf = gamma_cdf(x, 1, 100)
    k, theta = 1.0, 1.0 / (np.log(2.0) * 100)
    assert np.allclose(pdf, gamma.pdf(x, a=k, scale=theta))
    assert np.allclose(cdf, gamma.cdf(x, a=k, scale=theta))


def test_pvalue_is_survival_function():
    I_hat = 0.03
    p = market_information_pvalue(I_hat, 1, 100)
    k, theta = 1.0, 1.0 / (np.log(2.0) * 100)
    assert np.isclose(p, gamma.sf(I_hat, a=k, scale=theta))
