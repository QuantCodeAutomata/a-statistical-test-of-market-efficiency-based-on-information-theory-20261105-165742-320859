# A statistical test of market efficiency based on information theory

Replication of selected experiments from *A statistical test of market
efficiency based on information theory* (arXiv:2208.11976).

The paper represents a price series as a sequence of binary up/down
increments and estimates the market information Î^{L+1}, the gain in
predictive power from knowing the last L increments over knowing none. Under
the efficient market hypothesis (EMH), all conditional probabilities
π_i^L equal 1/2 and Î^{L+1} is asymptotically gamma-distributed with shape
k = 2^{L-1} and scale θ = 1/(ln(2)·n). This gives a statistical test of
market efficiency usable on any price series.

## Repository layout

```
src/    market-information estimator, gamma-based test, Theorem 2 error bound, config
exp/    one script per experiment, run as `python -m exp.<name>`
data/   data/data_loader.py: OHLCV bars via the QuantX Dataloader REST API
tests/  pytest unit tests of src/ and a market-data smoke test
results/ figures, tables and RESULTS.md with the paper comparison
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill DATALOADER_API_KEY and MASSIVE_API_KEY for exp_3
```

## Tests

```bash
python -m pytest -m "not market_data"   # unit tests, no network access
python -m pytest                        # also runs the market-data smoke test
```

## Experiments

```bash
python -m exp.exp_1   # Figures 2-3: simulated distribution of Î^{L+1} vs. the gamma law
python -m exp.exp_2   # Figure 4: Kolmogorov-Smirnov statistic vs. sample size n
python -m exp.exp_3   # Figure 6: rolling-window test on CAC 40, Russell 2000, Perficient, BTC/USD
python -m exp.exp_4   # Figure 1: Theorem 2 error-bound comparison across q
python -m exp.exp_5   # Figure 5: critical-value chart of the market-efficiency test
```

`reproduce.sh` runs the test suite and every experiment in this order.

Every experiment writes its figures and tables to `results/`; see
`results/RESULTS.md` for the comparison with the paper's reported values,
deviations and items not reproduced.
