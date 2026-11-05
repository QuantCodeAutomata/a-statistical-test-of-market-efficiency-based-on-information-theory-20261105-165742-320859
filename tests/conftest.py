"""Shared pytest fixtures and marker registration."""

import os

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "market_data: tests that load real market data through data/data_loader.py"
    )


@pytest.fixture(scope="session")
def market_slice(request: pytest.FixtureRequest):
    """A short, cached slice of real daily bars for the four exp_3 tickers.

    Loads about one year of data for a subset of the exp_3 universe through
    data/data_loader.py and caches it across test sessions. Skips with a
    clear reason when DATALOADER_API_KEY or MASSIVE_API_KEY is absent.
    """
    if not (os.environ.get("DATALOADER_API_KEY") and os.environ.get("MASSIVE_API_KEY")):
        pytest.skip("DATALOADER_API_KEY / MASSIVE_API_KEY not set: skipping market_data test")

    cache_dir = request.config.cache.mkdir("market_slice")
    cache_file = cache_dir / "prft_2021.csv"
    import pandas as pd

    if cache_file.exists():
        return pd.read_csv(cache_file, parse_dates=["date"])

    from data.data_loader import load_ohlcv

    bars, _ = load_ohlcv(["PRFT"], "2021-01-01", "2021-12-31", timeframe="1d")
    bars.to_csv(cache_file, index=False)
    return bars
