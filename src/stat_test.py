"""Statistical test of market efficiency (Section 3.3).

Under the EMH null hypothesis (pi_i^L = 1/2 for every prefix i), the
estimated market information Î^{L+1} follows asymptotically the gamma
distribution Gamma(k, theta) with k = 2^(L-1), theta = 1/(ln(2) n)
(Sec. 3.2.2, equation 11). The p-value of an observed statistic is the
upper tail probability under this null distribution, and a critical value
for a given p-value alpha is the corresponding gamma quantile.

# scipy.stats.gamma implements the gamma distribution's pdf/cdf/ppf/sf used
# below; the estimator and test themselves are specific to this paper.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import gamma

from src.market_information import gamma_params


def market_information_pvalue(I_hat: float, L: int, n: int) -> float:
    """p-value of an observed Î^{L+1} under the EMH null hypothesis
    (Sec. 3.3): p = P(Î^{L+1} >= observed | EMH) = 1 - F_gamma(observed).
    """
    k, theta = gamma_params(L, n)
    return float(gamma.sf(I_hat, a=k, scale=theta))


def market_information_critical_value(L: int, n: int, alpha: float) -> float:
    """Critical value of Î^{L+1} for a p-value threshold alpha (Sec. 3.3,
    Figure 5): q_alpha = F_gamma^{-1}(1 - alpha; k, theta).
    """
    k, theta = gamma_params(L, n)
    return float(gamma.ppf(1.0 - alpha, a=k, scale=theta))


def gamma_pdf(x: np.ndarray, L: int, n: int) -> np.ndarray:
    """Asymptotic gamma density of Î^{L+1} under the EMH (Sec. 3.2.2)."""
    k, theta = gamma_params(L, n)
    return gamma.pdf(x, a=k, scale=theta)


def gamma_cdf(x: np.ndarray, L: int, n: int) -> np.ndarray:
    """Asymptotic gamma CDF of Î^{L+1} under the EMH (Sec. 3.2.2)."""
    k, theta = gamma_params(L, n)
    return gamma.cdf(x, a=k, scale=theta)
