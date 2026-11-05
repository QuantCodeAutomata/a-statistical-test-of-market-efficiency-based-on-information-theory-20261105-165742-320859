"""Error bound of the approximation of E[g_j(t, X/n_j)] (Theorem 2, Sec. 3.2.1).

Theorem 2 states, for g_j defined in equation (4) and X ~ Binomial(n_j, 1/2):

    E[g_j(t, X/n_j)] = 1 + i t p_j^L / (2 ln(2) n_j) + R(t, n_j)

with, for q in N \\ {0, 1} and any epsilon > 1, an n_j large enough that

    |R(t, n_j)| <= (epsilon/96) (q-1)^(1-1/q) (4q-1)^3
                   * sum_{l=1}^{4} |2^5 t p_j^L / (15 ln 2)|^l L(4,l) / (5ql-1)^(1/q)
                   * n_j^(-2 + 1/(2q))                                   (equation 10)

where L(k, l) = C(k-1, l-1) k! / l! is a Lah number. Letting epsilon -> 1
gives the asymptotic upper bound evaluated here (Sec. 3.2.1, Figure 1).

# Custom implementation (paper Theorem 2, equation 10): this closed-form
# combinatorial bound is specific to the paper and has no library equivalent.
"""

from __future__ import annotations

from math import comb, factorial, log

import numpy as np


def lah_number(k: int, l: int) -> float:
    """Lah number L(k, l) = C(k-1, l-1) * k! / l! (Theorem 2, equation 10)."""
    if l < 1 or l > k:
        raise ValueError("l must satisfy 1 <= l <= k")
    return comb(k - 1, l - 1) * factorial(k) / factorial(l)


def theorem2_bound(
    q: int,
    n_j: np.ndarray | float,
    t: float = 1.0,
    p_j_l: float = 0.5,
    epsilon: float = 1.0,
) -> np.ndarray:
    """Asymptotic upper bound of |R(t, n_j)| from Theorem 2 (equation 10),
    evaluated with epsilon -> 1 (the tightest constant admitted by the
    theorem for n_j large enough, Sec. 3.2.1 text following Theorem 2).

    n_j = 0 is excluded from the valid domain of the bound (it contains a
    negative power of n_j) and is returned as +inf, matching the fact that
    the theorem only holds for n_j at or above some threshold nu.
    """
    if q < 2:
        raise ValueError("q must be an integer >= 2 (Theorem 2 requires q in N \\ {0,1})")
    n_j = np.asarray(n_j, dtype=float)

    ln2 = log(2.0)
    inner_sum = np.zeros_like(n_j)
    for l in range(1, 5):
        term_const = abs((2**5) * t * p_j_l / (15.0 * ln2)) ** l
        inner_sum = inner_sum + term_const * lah_number(4, l) / (5 * q * l - 1) ** (1.0 / q)

    prefactor = (epsilon / 96.0) * (q - 1) ** (1.0 - 1.0 / q) * (4 * q - 1) ** 3
    with np.errstate(divide="ignore"):
        power_term = np.where(n_j > 0, n_j ** (-2.0 + 1.0 / (2.0 * q)), np.inf)
    return prefactor * inner_sum * power_term
