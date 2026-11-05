"""Market information estimator of Risso's binary-symbolic approach.

Implements Section 2 and Section 3.1 of "A statistical test of market
efficiency based on information theory": the binary-increment symbolic
representation of a price series, the Shannon entropies H^L and H^{L+1}
(equations 1-2), the market information I^{L+1} = H*^{L+1} - H^{L+1}
(equation 3), and its empirical estimator Î^{L+1}.

Custom implementation (paper Eqs. 1, 2, 3): no general-purpose entropy or
information-theory library implements this specific conditional two-state
construction, so the estimator is coded directly from the equations.
"""

from __future__ import annotations

import numpy as np


def gray_code_sequences(length: int) -> list[tuple[int, ...]]:
    """Return the 2^length binary sequences of a given length ordered by
    the reflected binary (Gray) code, as used to index the prefixes G_i^L
    in Section 2. Order is for display only: the entropy sums below are
    taken over all prefixes and do not depend on their ordering.
    """
    if length == 0:
        return [()]
    previous = gray_code_sequences(length - 1)
    return [(0,) + p for p in previous] + [(1,) + p for p in reversed(previous)]


def binary_returns(prices: np.ndarray) -> np.ndarray:
    """Binary increase/decrease indicators X_i = 1{P_i - P_{i-1} > 0} (Sec. 2)."""
    prices = np.asarray(prices, dtype=float)
    if prices.ndim != 1 or len(prices) < 2:
        raise ValueError("prices must be a 1-D array of at least 2 values")
    return (np.diff(prices) > 0).astype(np.int64)


def simulate_emh_sequences(
    n: int, L: int, n_trajectories: int, rng: np.random.Generator
) -> np.ndarray:
    """Simulate binary sequences of length n + L under the EMH.

    Each X_i is an i.i.d. Bernoulli(1/2) draw, so that every conditional
    probability pi_i^L equals 1/2 exactly, as required by the null
    hypothesis of Theorem 1 (Sec. 3, "methodology" of exp_1).
    """
    if n <= 0 or L <= 0 or n_trajectories <= 0:
        raise ValueError("n, L and n_trajectories must be positive")
    return rng.integers(0, 2, size=(n_trajectories, n + L))


def prefix_counts(X: np.ndarray, L: int) -> tuple[int, np.ndarray, np.ndarray]:
    """Count prefix occurrences and suffix=1 occurrences via a sliding window
    of length L+1 over a single binary sequence X (Sec. 2 and 3.1).

    Returns (n, counts_n, counts_suffix1) where counts_n[i] = n_i (number of
    times prefix i occurs among the n = len(X) - L windows) and
    counts_suffix1[i] = number of times the suffix equals 1 given prefix i.
    Prefixes are indexed by their value read as a binary integer (X_1 is the
    most significant bit); this indexing does not affect the entropy sums.
    """
    X = np.asarray(X, dtype=np.int64)
    n_total = len(X)
    n = n_total - L
    if n <= 0:
        raise ValueError("sequence too short for the requested prefix length L")
    windows = np.lib.stride_tricks.sliding_window_view(X, L + 1)
    prefixes = windows[:, :L]
    suffixes = windows[:, L]
    weights = (1 << np.arange(L - 1, -1, -1))
    idx = prefixes @ weights
    n_prefixes = 1 << L
    counts_n = np.bincount(idx, minlength=n_prefixes).astype(np.int64)
    counts_suffix1 = np.bincount(idx, weights=suffixes, minlength=n_prefixes)
    return n, counts_n, counts_suffix1


def _xlog2x(x: np.ndarray) -> np.ndarray:
    """x * log2(x) with the convention 0 * log2(0) = 0 (Sec. 2, below eq. 1)."""
    x = np.asarray(x, dtype=float)
    out = np.zeros_like(x)
    mask = x > 0
    out[mask] = x[mask] * np.log2(x[mask])
    return out


def market_information_from_counts(
    n: int, counts_n: np.ndarray, counts_suffix1: np.ndarray
) -> dict:
    """Compute the estimated market information Î^{L+1} and its components
    from prefix/suffix counts (Sec. 3.1, equations 1-3).

    Returns a dict with p_hat, pi_hat, H_L, H_L1, H_star, I_hat.
    """
    counts_n = np.asarray(counts_n, dtype=float)
    counts_suffix1 = np.asarray(counts_suffix1, dtype=float)
    p_hat = counts_n / n
    a_hat = counts_suffix1 / n  # p_i^L * pi_i^L = P(prefix i, suffix=1)
    b_hat = (counts_n - counts_suffix1) / n  # p_i^L * (1 - pi_i^L)
    with np.errstate(divide="ignore", invalid="ignore"):
        pi_hat = np.where(counts_n > 0, counts_suffix1 / counts_n, 0.0)

    H_L = -np.sum(_xlog2x(p_hat))  # equation: H^L = -sum p_i^L log2 p_i^L
    H_L1 = -np.sum(_xlog2x(a_hat) + _xlog2x(b_hat))  # equation (1)
    H_star = 1.0 + H_L  # equation (2)
    I_hat = H_star - H_L1  # equation (3)

    # Cross-check with the single-pass "key formula" (implementation_notes):
    # Î^{L+1} = sum_i p_i [-log2(p_i/2) + pi_i log2(p_i pi_i) + (1-pi_i) log2(p_i(1-pi_i))]
    mask = p_hat > 0
    direct = np.zeros_like(p_hat)
    direct[mask] = p_hat[mask] * (1.0 - np.log2(p_hat[mask]))
    direct += _xlog2x(a_hat) + _xlog2x(b_hat)
    I_hat_direct = np.sum(direct)
    assert np.isclose(I_hat, I_hat_direct, atol=1e-9), "formula mismatch in Î^{L+1}"

    return {
        "p_hat": p_hat,
        "pi_hat": pi_hat,
        "H_L": H_L,
        "H_L1": H_L1,
        "H_star": H_star,
        "I_hat": I_hat,
    }


def market_information(X: np.ndarray, L: int) -> dict:
    """Estimate Î^{L+1} directly from one binary sequence X (Sec. 3.1)."""
    n, counts_n, counts_suffix1 = prefix_counts(X, L)
    return market_information_from_counts(n, counts_n, counts_suffix1)


def gamma_params(L: int, n: int) -> tuple[float, float]:
    """Asymptotic gamma distribution parameters of Î^{L+1} under the EMH
    (Sec. 3.2.2, equation 11): shape k = 2^(L-1), scale theta = 1/(ln(2) n).
    """
    k = 2.0 ** (L - 1)
    theta = 1.0 / (np.log(2.0) * n)
    return k, theta
