"""Experiment 1: simulation validation of the asymptotic gamma distribution
of the market information estimator under the EMH.

Reproduces Figures 2 (L=1, n=100) and 3 (L=2, n=4000) of Section 3.2.2:
simulated binary sequences under the EMH (all conditional probabilities
pi_i^L = 1/2) give an empirical distribution of Î^{L+1} that is compared,
by histogram and CDF, with the asymptotic Gamma(2^(L-1), 1/(ln(2) n)).
"""

from __future__ import annotations

import json

import matplotlib
import numpy as np
import pandas as pd
from scipy.stats import kstest

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src import config
from src.market_information import gamma_params, market_information, simulate_emh_sequences
from src.stat_test import gamma_cdf, gamma_pdf

RESULTS_DIR = "results"


def simulate_market_information(L: int, n: int, n_trajectories: int, seed: int) -> np.ndarray:
    """Simulate n_trajectories EMH sequences and return their Î^{L+1} values."""
    rng = np.random.default_rng(seed)
    X = simulate_emh_sequences(n, L, n_trajectories, rng)
    I_hat = np.empty(n_trajectories, dtype=float)
    for i in range(n_trajectories):
        I_hat[i] = market_information(X[i], L)["I_hat"]
    return I_hat


def plot_histogram_and_cdf(I_hat: np.ndarray, L: int, n: int, path: str) -> None:
    """Grey histogram + theoretical gamma pdf, and empirical vs theoretical CDF."""
    k, theta = gamma_params(L, n)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    x_max = max(I_hat.max() * 1.15, k * theta * 4)
    grid = np.linspace(1e-9, x_max, 500)

    axes[0].hist(I_hat, bins=40, density=True, color="grey", edgecolor="black", alpha=0.8,
                 label="simulated $\\hat I^{%d}$" % (L + 1))
    axes[0].plot(grid, gamma_pdf(grid, L, n), color="black", lw=2,
                 label=f"Gamma(k={k:g}, θ=1/(ln2·n))")
    axes[0].set_xlabel(f"$\\hat I^{{{L + 1}}}$")
    axes[0].set_ylabel("density")
    axes[0].set_title(f"L={L}, n={n}: histogram vs. asymptotic gamma pdf")
    axes[0].legend()

    sorted_vals = np.sort(I_hat)
    ecdf = np.arange(1, len(sorted_vals) + 1) / len(sorted_vals)
    axes[1].step(sorted_vals, ecdf, color="grey", where="post", label="empirical CDF")
    axes[1].plot(grid, gamma_cdf(grid, L, n), color="black", lw=2, label="theoretical gamma CDF")
    axes[1].set_xlabel(f"$\\hat I^{{{L + 1}}}$")
    axes[1].set_ylabel("CDF")
    axes[1].set_title(f"L={L}, n={n}: empirical vs. asymptotic gamma CDF")
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def run() -> dict:
    """Run exp_1 for every (L, n) pair of src.config.EXP1_N_BY_L and save results."""
    summary = {}
    for L in config.EXP1_L_VALUES:
        n = config.EXP1_N_BY_L[L]
        seed = config.RANDOM_SEED + L
        I_hat = simulate_market_information(L, n, config.EXP1_N_TRAJECTORIES, seed)

        k, theta = gamma_params(L, n)
        theoretical_mean, theoretical_var = k * theta, k * theta**2
        empirical_mean, empirical_var = float(I_hat.mean()), float(I_hat.var(ddof=1))
        ks_stat, ks_pvalue = kstest(I_hat, "gamma", args=(k, 0.0, theta))

        plot_path = f"{RESULTS_DIR}/exp1_L{L}_n{n}_hist_cdf.png"
        plot_histogram_and_cdf(I_hat, L, n, plot_path)
        pd.DataFrame({"I_hat": I_hat}).to_csv(
            f"{RESULTS_DIR}/exp1_L{L}_n{n}_values.csv", index=False
        )

        summary[f"L{L}_n{n}"] = {
            "L": L,
            "n": n,
            "n_trajectories": config.EXP1_N_TRAJECTORIES,
            "gamma_shape_k": k,
            "gamma_scale_theta": theta,
            "theoretical_mean": theoretical_mean,
            "theoretical_var": theoretical_var,
            "empirical_mean": empirical_mean,
            "empirical_var": empirical_var,
            "ks_statistic": float(ks_stat),
            "ks_pvalue": float(ks_pvalue),
            "plot": plot_path,
        }
        print(
            f"[exp_1] L={L} n={n}: empirical mean={empirical_mean:.6f} "
            f"(theory {theoretical_mean:.6f}), KS stat={ks_stat:.4f}, p={ks_pvalue:.4f}"
        )

    with open(f"{RESULTS_DIR}/exp1_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    return summary


if __name__ == "__main__":
    run()
