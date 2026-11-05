"""Experiment 4: numerical evaluation of the error bound of Theorem 2.

Reproduces Figure 1 of Section 3.2.1: the asymptotic upper bound of the
remainder |R(t, n_j)| in the approximation of E[g_j(t, X/n_j)], evaluated
at p_j^L = 1/2, t = 1, for q in {2, 3, 4, 5} over a grid of n_j.
"""

from __future__ import annotations

import json

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src import config
from src.error_bound import theorem2_bound

RESULTS_DIR = "results"


def run() -> pd.DataFrame:
    """Evaluate the Theorem 2 bound for every q in src.config.EXP4_Q_VALUES
    over src.config.EXP4_NJ_GRID, save the table and plot, and check that
    lower q gives a tighter (lower) bound for every n_j > 0."""
    n_j_grid = np.array(config.EXP4_NJ_GRID, dtype=float)
    table = pd.DataFrame({"n_j": n_j_grid})
    for q in config.EXP4_Q_VALUES:
        bound = theorem2_bound(
            q, n_j_grid, t=config.EXP4_T, p_j_l=config.EXP4_P_J_L, epsilon=config.EXP4_EPSILON
        )
        table[f"bound_q{q}"] = bound

    table.to_csv(f"{RESULTS_DIR}/exp4_error_bound.csv", index=False)

    positive = table[table["n_j"] > 0]
    q_cols = [f"bound_q{q}" for q in config.EXP4_Q_VALUES]
    # Theorem 2 (eq. 10): the bound is monotone increasing in q for fixed n_j,
    # since lower q gives a smaller prefactor and power exponent in the formula.
    ordered = np.all(np.diff(positive[q_cols].to_numpy(), axis=1) >= 0)

    fig, ax = plt.subplots(figsize=(7, 5))
    for q in config.EXP4_Q_VALUES:
        ax.plot(positive["n_j"], positive[f"bound_q{q}"], marker="o", label=f"q={q}")
    ax.set_yscale("log")
    ax.set_xlabel("$n_j$")
    ax.set_ylabel("asymptotic upper bound of $|R(t, n_j)|$ (log scale)")
    ax.set_title("Theorem 2 error bound vs. $n_j$, $t=1$, $p_j^L=1/2$")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"{RESULTS_DIR}/exp4_error_bound_plot.png", dpi=150)
    plt.close(fig)

    summary = {
        "q_values": config.EXP4_Q_VALUES,
        "t": config.EXP4_T,
        "p_j_L": config.EXP4_P_J_L,
        "epsilon": config.EXP4_EPSILON,
        "n_j_grid": config.EXP4_NJ_GRID,
        "bound_increasing_in_q": bool(ordered),
        "bound_at_n_j_1000": {
            f"q{q}": float(table.loc[table["n_j"] == 1000, f"bound_q{q}"].iloc[0])
            for q in config.EXP4_Q_VALUES
        },
    }
    with open(f"{RESULTS_DIR}/exp4_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[exp_4] bound increasing in q for every n_j>0: {ordered}")
    print(table.to_string(index=False))
    return table


if __name__ == "__main__":
    run()
