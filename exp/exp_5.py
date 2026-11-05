"""Experiment 5: p-value threshold chart for the market efficiency test.

Reproduces Figure 5 of Section 3.3: for L=1 (so Î^2), the critical values
of the gamma-based test at p-value thresholds 5%, 1% and 0.1%, plotted as
a function of the rolling-window sample size n.
"""

from __future__ import annotations

import json

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src import config
from src.stat_test import market_information_critical_value

RESULTS_DIR = "results"


def run() -> pd.DataFrame:
    """Compute the gamma-quantile critical values over src.config.EXP5_N_GRID
    for every alpha in src.config.EXP5_ALPHAS and save the table and plot."""
    L = config.EXP5_L
    rows = []
    for n in config.EXP5_N_GRID:
        row = {"n": n}
        for alpha in config.EXP5_ALPHAS:
            row[f"critical_value_alpha{alpha}"] = market_information_critical_value(L, n, alpha)
        rows.append(row)
    table = pd.DataFrame(rows)
    table.to_csv(f"{RESULTS_DIR}/exp5_critical_values.csv", index=False)

    fig, ax = plt.subplots(figsize=(7, 5))
    styles = {0.05: "-", 0.01: "--", 0.001: ":"}
    for alpha in config.EXP5_ALPHAS:
        ax.plot(table["n"], table[f"critical_value_alpha{alpha}"],
                 linestyle=styles.get(alpha, "-"), label=f"p-value = {alpha:.1%}" if alpha >= 0.01
                 else f"p-value = {alpha:.1%}")
    ax.set_xlabel("n")
    ax.set_ylabel("critical value of $\\hat I^2$")
    ax.set_title("Critical values of the market efficiency test vs. n (L=1)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"{RESULTS_DIR}/exp5_critical_values_plot.png", dpi=150)
    plt.close(fig)

    n100 = table.loc[table["n"] == 100]
    at_n100 = {
        f"alpha{alpha}": float(n100[f"critical_value_alpha{alpha}"].iloc[0])
        for alpha in config.EXP5_ALPHAS
    } if not n100.empty else {}
    summary = {"L": L, "alphas": config.EXP5_ALPHAS, "n_grid": config.EXP5_N_GRID,
               "critical_values_at_n100": at_n100}
    with open(f"{RESULTS_DIR}/exp5_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[exp_5] critical values at n=100: {at_n100}")
    return table


if __name__ == "__main__":
    run()
