# AGENTS.md

Guide for coding agents and contributors working on this repository.

## What this repository implements

A replication of selected experiments from *A statistical test of market
efficiency based on information theory* (arXiv:2208.11976): a market-efficiency
test built from the Shannon-entropy-based "market information" estimator
Î^{L+1} of a binary up/down price representation, and its asymptotic gamma
null distribution Γ(2^(L-1), 1/(ln(2)·n)).

Five experiments are implemented:

- `exp_1`: Monte Carlo validation of the asymptotic gamma distribution of
  Î^{L+1} under the EMH (Sec. 3.2.2, Figures 2-3).
- `exp_2`: Kolmogorov-Smirnov test of the gamma approximation as a function of
  sample size n (Sec. 3.2.2, Figure 4).
- `exp_3`: empirical application to CAC 40, Russell 2000, Perficient and
  BTC/USD daily data (Sec. 4, Figure 6).
- `exp_4`: numerical evaluation of the Theorem 2 error bound (Sec. 3.2.1,
  Figure 1).
- `exp_5`: critical-value chart of the market-efficiency test vs. n (Sec. 3.3,
  Figure 5).

## Layout

```
src/            flat library modules: market_information.py, stat_test.py,
                error_bound.py, config.py (all parameters, with their
                paper section/equation or "not specified in the paper")
exp/            one script per experiment, exp_1.py .. exp_5.py
data/           data_loader.py (QuantX Dataloader / Massive OHLCV loader)
tests/          pytest tests for src/ and exp/
results/        every generated table, plot and summary JSON, plus RESULTS.md
```

Parameters live only in `src/config.py` as module-level UPPER_CASE variables.
Market data is loaded only through `data/data_loader.py`; no experiment writes
its own loader or fetches data another way.

## Setup

```
pip install -r requirements.txt
cp .env.example .env   # fill DATALOADER_API_KEY and MASSIVE_API_KEY for exp_3
```

## Tests

```
python -m pytest -m "not market_data"   # no network access needed
python -m pytest                        # also runs exp_3's market-data test
                                         # (needs DATALOADER_API_KEY and
                                         # MASSIVE_API_KEY; skipped otherwise)
```

## Experiments

```
python -m exp.exp_1
python -m exp.exp_2
python -m exp.exp_3   # needs DATALOADER_API_KEY and MASSIVE_API_KEY in .env
python -m exp.exp_4
python -m exp.exp_5
```

All five experiments were run at the paper's full parameters (1,000
trajectories, full n-grids, full 2021 sample, all four assets); there is no
reduced configuration and no `--full` flag.

## Conventions

- Experiment parameters only in `src/config.py`, never hardcoded in `exp/` or
  `src/`.
- Data access only through `data/data_loader.py`; downloaded bars are cached
  under `data/cache/` (git-ignored) and never committed.
- API keys only in an uncommitted `.env` (see `.env.example`); never in code,
  logs, or results.
- Re-running an experiment overwrites its files in `results/`. The numbers and
  verdicts in `results/RESULTS.md` are not regenerated automatically — check
  them against the new files and update by hand after a rerun.
- Run `python -m pytest -m "not market_data"` after any change to `src/` or
  `exp/`; run the full suite (including the market-data test) after a change
  to the data path, and before pushing.
