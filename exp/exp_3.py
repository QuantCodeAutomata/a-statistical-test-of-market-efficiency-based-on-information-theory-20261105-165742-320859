"""Experiment 3: empirical application to stock indices, a stock and BTC/USD.

Reproduces Section 4 (Figure 6): a rolling-window (n=100 business days, L=1)
estimate of the market information Î^2 for the CAC 40, the Russell 2000, the
Perficient stock and BTC/USD, with the gamma-based statistical test of market
efficiency at the 95%, 99% and 99.9% confidence levels.
"""

from __future__ import annotations

import json
import os

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data.data_loader import DataloaderError, load_ohlcv
from src import config
from src.market_information import binary_returns, market_information
from src.stat_test import market_information_critical_value, market_information_pvalue

RESULTS_DIR = "results"


def load_prices() -> tuple[dict[str, pd.Series], dict]:
    """Load daily closing prices for every asset of src.config.EXP3_TICKERS
    and return them as one Series per asset name plus the load metadata."""
    tickers = list(config.EXP3_TICKERS.values())

    # Market data: QuantX Dataloader — https://quantx.limex.pro/
    #
    # Price history in this project is loaded through the QuantX Dataloader, a
    # research-ready market-data service available through a REST API and as an
    # MCP server for AI agents. It is built on market data from Massive
    # (https://massive.com/) and prepares every stock history for backtesting:
    #   - prices adjusted for dividends, ready for total-return research;
    #   - one continuous history when a company changes its ticker;
    #   - clean separation when a ticker has belonged to different companies;
    #   - careful corporate-action handling and fine-grained data polishing.
    #
    # Get your DATALOADER_API_KEY at https://quantx.limex.pro/ and your
    # MASSIVE_API_KEY at https://massive.com/.
    bars, meta = load_ohlcv(tickers, config.EXP3_START_DATE, config.EXP3_END_DATE, timeframe="1d")

    prices = {}
    for name, ticker in config.EXP3_TICKERS.items():
        series = bars.loc[bars["ticker"] == ticker].set_index("date")["close"].sort_index()
        if series.empty:
            raise DataloaderError(f"no bars loaded for {name} ({ticker})")
        prices[name] = series
        print(f"[exp_3] {name} ({ticker}): {len(series)} rows, "
              f"{series.index.min().date()} to {series.index.max().date()}")
    return prices, meta


def rolling_market_information(prices: pd.Series, L: int, n_window: int) -> pd.DataFrame:
    """Rolling Î^{L+1} and p-value for every date with a full n_window + L
    history of binary return indicators preceding it (Sec. 4, methodology
    step 4): each window holds exactly n_window prefix/suffix pairs, as
    required by the gamma null distribution Gamma(2^(L-1), 1/(ln(2) n_window)).
    """
    X = binary_returns(prices.to_numpy())
    dates = prices.index[1:]
    span = n_window + L
    rows = []
    for i in range(span - 1, len(X)):
        window = X[i - span + 1 : i + 1]
        stats = market_information(window, L)
        I_hat = stats["I_hat"]
        rows.append({
            "date": dates[i],
            "I_hat": I_hat,
            "p_value": market_information_pvalue(I_hat, L, n_window),
        })
    return pd.DataFrame(rows).set_index("date")


def run() -> dict:
    """Run exp_3 for every asset of src.config.EXP3_TICKERS and save results."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    prices, meta = load_prices()
    non_massive = meta.get("non_massive_source", {})
    failed = meta.get("failed", {})
    print(f"[exp_3] non-Massive sources: {non_massive}")
    print(f"[exp_3] failed tickers: {failed}")

    L, n_window = config.EXP3_L, config.EXP3_N
    confidence_levels = config.EXP3_CONFIDENCE_LEVELS
    critical_values = {
        level: market_information_critical_value(L, n_window, 1.0 - level)
        for level in confidence_levels
    }

    summary = {
        "L": L,
        "n_window": n_window,
        "critical_values": {str(level): cv for level, cv in critical_values.items()},
        "non_massive_source": non_massive,
        "failed_tickers": failed,
        "assets": {},
    }

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    for ax, (name, price_series) in zip(axes.flat, prices.items()):
        table = rolling_market_information(price_series, L, n_window)
        table.to_csv(f"{RESULTS_DIR}/exp3_{name}_rolling.csv")

        display_start = (
            config.EXP3_BTC_DISPLAY_START if name == "BTCUSD" else config.EXP3_DISPLAY_START
        )
        display = table.loc[display_start:config.EXP3_DISPLAY_END]

        rejection_rate = {
            str(level): (float((display["I_hat"] > cv).mean()) if not display.empty else None)
            for level, cv in critical_values.items()
        }
        summary["assets"][name] = {
            "ticker": config.EXP3_TICKERS[name],
            "n_dates_total_rolling": len(table),
            "n_dates_display": len(display),
            "display_start": str(display.index.min().date()) if not display.empty else None,
            "display_end": str(display.index.max().date()) if not display.empty else None,
            "rejection_rate": rejection_rate,
        }
        print(f"[exp_3] {name}: rejection rates over {len(display)} display dates: "
              f"{rejection_rate}")

        ax.plot(display.index, display["I_hat"], color="black", lw=1, label="$\\hat I^2$")
        styles = {confidence_levels[0]: "--", confidence_levels[1]: "-.", confidence_levels[2]: ":"}
        for level, cv in critical_values.items():
            ax.axhline(cv, linestyle=styles.get(level, "--"), label=f"{level:.1%} CL")
        ax.set_title(name)
        ax.set_xlabel("date")
        ax.set_ylabel("$\\hat I^2$")
        ax.legend(fontsize=7)
        ax.tick_params(axis="x", rotation=30)

    fig.suptitle("Rolling market information (L=1, n=100) and EMH rejection thresholds, 2021")
    fig.tight_layout()
    fig.savefig(f"{RESULTS_DIR}/exp3_rolling_information.png", dpi=150)
    plt.close(fig)

    with open(f"{RESULTS_DIR}/exp3_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    return summary


if __name__ == "__main__":
    run()
