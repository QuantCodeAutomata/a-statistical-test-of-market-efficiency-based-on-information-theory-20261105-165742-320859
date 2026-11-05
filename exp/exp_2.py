"""Experiment 2: Kolmogorov-Smirnov test of the asymptotic gamma
approximation as a function of the sample size n.

Reproduces Figure 4 of Section 3.2.2: for L=1, simulate the distribution
of Î^{L+1} under the EMH for a grid of n, compare it with the theoretical
Gamma(1, 1/(ln(2) n)) by a one-sample KS test, and locate the minimum n
above which the approximation holds at the 5%, 1% and 0.1% levels.
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

RESULTS_DIR = "results"


def ks_statistic_for_n(L: int, n: int, n_trajectories: int, seed: int) -> tuple[float, float]:
    """Simulate n_trajectories EMH sequences for sample size n and return the
    KS statistic and p-value against the theoretical Gamma(2^(L-1), 1/(ln2 n))."""
    rng = np.random.default_rng(seed)
    X = simulate_emh_sequences(n, L, n_trajectories, rng)
    I_hat = np.array([market_information(X[i], L)["I_hat"] for i in range(n_trajectories)])
    k, theta = gamma_params(L, n)
    ks_stat, ks_pvalue = kstest(I_hat, "gamma", args=(k, 0.0, theta))
    return float(ks_stat), float(ks_pvalue)


def run() -> pd.DataFrame:
    """Run exp_2 over src.config.EXP2_N_GRID and save the KS-statistic table and plot."""
    L = config.EXP2_L
    m = config.EXP2_N_TRAJECTORIES
    rows = []
    for i, n in enumerate(config.EXP2_N_GRID):
        seed = config.RANDOM_SEED + 1000 + i
        ks_stat, ks_pvalue = ks_statistic_for_n(L, n, m, seed)
        rows.append({"n": n, "ks_statistic": ks_stat, "ks_pvalue": ks_pvalue})
        print(f"[exp_2] n={n}: KS stat={ks_stat:.4f}, p={ks_pvalue:.4f}")

    table = pd.DataFrame(rows)
    table.to_csv(f"{RESULTS_DIR}/exp2_ks_results.csv", index=False)

    # Asymptotic Kolmogorov critical constants c(alpha): D_crit = c(alpha)/sqrt(m)
    critical_values = {
        alpha: c / np.sqrt(m) for alpha, c in config.EXP2_KS_CRITICAL_CONSTANTS.items()
    }
    min_n_above = {}
    for alpha, d_crit in critical_values.items():
        valid = table.loc[table["ks_statistic"] < d_crit, "n"]
        min_n_above[str(alpha)] = int(valid.min()) if not valid.empty else None

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(table["n"], table["ks_statistic"], marker="o", color="black",
            label="simulated KS statistic")
    styles = {0.05: "--", 0.01: "-.", 0.001: ":"}
    for alpha, d_crit in critical_values.items():
        ax.axhline(d_crit, linestyle=styles.get(alpha, "--"),
                   label=f"critical value, p={alpha:.3%}" if alpha >= 0.001 else f"p={alpha}")
    ax.set_xlabel("n")
    ax.set_ylabel("KS statistic")
    ax.set_title(f"KS statistic vs. n for the Gamma(1, 1/(ln2·n)) approximation (L={L})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"{RESULTS_DIR}/exp2_ks_plot.png", dpi=150)
    plt.close(fig)

    summary = {
        "L": L,
        "n_trajectories": m,
        "critical_values": critical_values,
        "min_n_below_critical_value": min_n_above,
    }
    with open(f"{RESULTS_DIR}/exp2_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[exp_2] minimum n below critical value: {min_n_above}")
    return table


if __name__ == "__main__":
    run()
