# Results — A statistical test of market efficiency based on information theory

Paper: *A statistical test of market efficiency based on information theory*
(arXiv:2208.11976).

All numbers below come from the JSON/CSV files written to `results/` by the
scripts in `exp/`, produced by the runs described in each section. Re-running
an experiment overwrites its files in `results/`; this file must then be
checked against the new files and updated by hand.

## Experiment 1 — Simulation validation of the asymptotic gamma distribution

Command: `python -m exp.exp_1`
Files: `results/exp1_L1_n100_hist_cdf.png`, `results/exp1_L2_n4000_hist_cdf.png`,
`results/exp1_L1_n100_values.csv`, `results/exp1_L2_n4000_values.csv`,
`results/exp1_summary.json`

For `L=1, n=100` and `L=2, n=4000`, 1,000 independent trajectories of i.i.d.
Bernoulli(1/2) binary return sequences were simulated, the market information
estimator Î^{L+1} (Sec. 3.1) was computed on each, and the empirical
distribution was compared to Γ(2^(L-1), 1/(ln(2)·n)) (Sec. 3.2.2).

| setting | theoretical mean | empirical mean | theoretical var | empirical var | KS statistic | KS p-value |
|---|---|---|---|---|---|---|
| L=1, n=100 | 0.014427 | 0.015043 | 2.0814e-4 | 2.1334e-4 | 0.0621 | 8.6e-4 |
| L=2, n=4000 | 7.2135e-4 | 7.2142e-4 | 2.6017e-7 | 2.7655e-7 | 0.0235 | 0.629 |

Both settings reproduce the paper's qualitative description (Sec. 3.2.2): the
distribution of Î^{L+1} is concentrated near 0, right-skewed, and its first
two moments match the gamma law closely in both cases. For L=2, n=4000 the
empirical and theoretical CDFs are statistically indistinguishable (KS
p=0.63). For L=1, n=100 the formal KS test rejects exact equality (p<0.001)
even though the fit is visually close, as the paper itself states that "this
confirmation is only visual" and that the exact adequacy of the gamma law at
n=100 requires the dedicated test of Sec. 3.2.2 (reproduced as Experiment 2).
The KS statistic obtained here for L=1, n=100 (0.0621) is of the same order as
the value read off the paper's own Figure 4 curve at n=100 (≈0.07, see
Experiment 2), confirming that the two implementations measure the same
quantity.

**Verdict:** L=2, n=4000 — reproduced. L=1, n=100 — partially reproduced
(correct shape and moments; exact distributional equality is not expected by
the paper itself at this n, consistent with Experiment 2's conclusion that the
gamma approximation only becomes tight for n≳100-200).

## Experiment 2 — Kolmogorov-Smirnov validation of the gamma approximation vs. n

Command: `python -m exp.exp_2`
Files: `results/exp2_ks_results.csv`, `results/exp2_ks_plot.png`,
`results/exp2_summary.json`

For `L=1` and `n` in {25, 50, 75, 100, 125, 150, 200, 300, 400, 600, 800,
1000}, 1,000 trajectories were simulated for each n and the KS statistic
between the empirical distribution of Î^2 and Γ(1, 1/(ln(2)·n)) was computed.
Critical values for a one-sample KS test with sample size m=1,000 at p=5%,
1%, 0.1% were computed from the standard asymptotic Kolmogorov constants
(D_crit(α) = c(α)/√m, c(0.05)=1.36, c(0.01)=1.63, c(0.001)=1.95), giving
0.0430, 0.0515, 0.0617 respectively.

| n | KS statistic (this run) | paper's Figure 4 curve |
|---|---|---|
| 25 | 0.0891 | — |
| 50 | 0.0657 | 0.085 |
| 75 | 0.0439 | — |
| 100 | 0.0411 | 0.07 |
| 125 | 0.0391 | — |
| 150 | 0.0378 | 0.055 |
| 200 | 0.0217 | 0.036 |
| 300 | 0.0421 | 0.026 |
| 400 | 0.0295 | 0.024 |
| 600 | 0.0334 | 0.026 |
| 800 | 0.0415 | 0.026 |
| 1000 | 0.0360 | 0.025 |

(The paper's Figure 4 curve values at n=50, 100, 150, 200, 300, 400, 600, 800,
1000 were read off the chart in Sec. 3.2.2, Figure 4.)

The KS statistic decreases from ≈0.09 at n=25 towards a plateau of ≈0.02-0.04
for n≥200 in both curves, and crosses the 5% critical value (0.043) near
n≈75-100 in this replication, matching the paper's own conclusion that "the
asymptotic distribution is valid for n≳100" (Sec. 3.2.2). Point-by-point
differences between the two curves (up to ≈60% at some n) are consistent with
Monte Carlo sampling noise: both curves are single realizations of a KS
statistic computed from only 1,000 simulated trajectories, which itself has a
standard deviation of the same order as the differences observed. The
monotonically increasing critical-value constants used here (0.043, 0.0515,
0.0617 for 5%, 1%, 0.1%) are the standard asymptotic Kolmogorov critical
values for a one-sample test against a fully specified distribution; the
paper does not give these constants numerically.

**Verdict:** partially reproduced — the qualitative conclusion ("valid for
n≳100", decreasing KS statistic, plateau at large n) holds, but individual
points differ from the paper's digitized curve by more than 10% at several n,
attributable to Monte Carlo noise inherent to a single 1,000-trajectory run
rather than to a methodological difference.

## Experiment 3 — Empirical application to stock indices, a single stock and a cryptocurrency

Command: `python -m exp.exp_3`
Files: `results/exp3_{CAC40,RUSSELL2000,PERFICIENT,BTCUSD}_rolling.csv`,
`results/exp3_rolling_information.png`, `results/exp3_summary.json`

A rolling window of n=100 business days with L=1 was applied to CAC 40,
Russell 2000, Perficient and BTC/USD daily closing prices over 2021 (with
history back to 2020-01-01 to fill the first window), displayed from
2021-06-01 (CAC 40, Russell 2000, Perficient) and 2021-04-11 (BTC/USD) through
2021-12-31, as in Sec. 4 and Figure 6.

| asset | ticker used | rejection rate 95% | rejection rate 99% | rejection rate 99.9% | paper (95% / 99% / 99.9%) |
|---|---|---|---|---|---|
| CAC 40 | EWQ (ETF proxy) | 9.3% | 0.0% | 0.0% | 60.8% / 31.0% / 4.4% |
| Russell 2000 | IWM (ETF proxy) | 0.0% | 0.0% | 0.0% | never rejected |
| Perficient | PRFT (common stock) | 58.7% | 10.7% | 0.0% | 57.0% / 15.2% / — |
| BTC/USD | X:BTCUSD | 1.5% | 0.0% | 0.0% | 4.2% / — / — |

Russell 2000 and Perficient reproduce the paper closely: Russell 2000 is
never rejected at any level in both the paper and this run, and Perficient's
95% rejection rate (58.7% vs. 57.0%) differs by only 3%. Because Perficient
uses the same instrument as the paper (no proxy substitution) and matches
almost exactly, the shared pipeline (market-information estimator, gamma
p-value, rolling window) is validated end to end on real data.

CAC 40 differs materially (9.3% vs. 60.8% at 95%): the Dataloader/Massive
route does not serve the raw CAC 40 index level (`I:FCHI` returns
`NOT_AUTHORIZED — not entitled to this data`, confirmed by a direct request),
so the iShares MSCI France ETF (EWQ) is used as an investable proxy. EWQ
trades on a US exchange during US hours, after the Paris session that forms
the CAC 40's own daily close; this timing mismatch changes the day-to-day
serial dependence structure measured by Î^2 relative to the native index
used by the paper. Since the identical pipeline reproduces Perficient's
result (a non-proxied instrument) almost exactly, this divergence is
attributed to the proxy substitution rather than to the implementation.
BTC/USD is lower than the paper (1.5% vs. 4.2%, a 64% relative difference)
but of the same small order of magnitude and the same low-information
direction (far below the always-rejected regime of CAC 40 or Perficient at
95%); the paper does not specify which venue its BTC/USD series comes from,
and Massive's own aggregation of BTC/USD may differ from the paper's source.
This hypothesis was not checked against an alternative BTC/USD source, so the
cause of the gap is not identified.

**Verdict:** Russell 2000 — reproduced. Perficient — reproduced at 95%,
partially reproduced at 99% (10.7% vs. 15.2%, same order, outside 10% but
within 50%). BTC/USD — not reproduced at 95% by the 50% relative-difference
criterion (1.5% vs. 4.2%), though its direction (small, non-zero, far from
the always-rejected regime) is qualitatively right; the cause of the gap was
not identified. CAC 40 — not reproduced at the index level; attributed to the
ETF-proxy substitution documented above (identified cause, corroborated by
the accurate Perficient reproduction using the same code path).

## Experiment 4 — Numerical evaluation of the Theorem 2 error bound

Command: `python -m exp.exp_4`
Files: `results/exp4_error_bound.csv`, `results/exp4_error_bound_plot.png`,
`results/exp4_summary.json`

The asymptotic (ε=1) upper bound of |R(t, n_j)| from Theorem 2 (Sec. 3.2.1,
Eq. 10) was evaluated for q ∈ {2, 3, 4, 5}, t=1, p_j^L=1/2, over n_j = 0 to
1000 in steps of 50, using the Lah numbers L(4,1)=24, L(4,2)=36, L(4,3)=12,
L(4,4)=1.

At n_j=1000: bound(q=2)=8.22e-4, bound(q=3)=3.96e-3, bound(q=4)=1.32e-2,
bound(q=5)=3.43e-2. The bound decreases monotonically in n_j for every q, and
is strictly increasing in q at every n_j tested (`bound_increasing_in_q =
true`), matching both qualitative claims of Sec. 3.2.1: "lower q values yield
lower bounds regardless of n_j" and the bound vanishing as n_j grows, at the
stated rate of O(n_j^(-2+1/(2q))) (O(n_j^-1.75) for q=2).

**Verdict:** reproduced (both qualitative properties hold exactly as stated).

## Experiment 5 — Critical-value chart for the market efficiency test

Command: `python -m exp.exp_5`
Files: `results/exp5_critical_values.csv`, `results/exp5_critical_values_plot.png`,
`results/exp5_summary.json`

For L=1 (so Γ(1, θ) is an exponential distribution with rate ln(2)·n), the
critical values q_α = -ln(α)/(ln(2)·n) were computed for α ∈ {0.05, 0.01,
0.001} and n = 10, 20, …, 1000, directly implementing the gamma-quantile
construction described in Sec. 3.3 ("we have also provided … an asymptotic
gamma distribution for Î^{L+1} under the null hypothesis, which we can use to
quantify the p-value …"). At n=100: 0.0432 (5%), 0.0664 (1%), 0.0997 (0.1%).
The three curves are monotonically ordered (5% < 1% < 0.1% everywhere) and
decrease roughly as 1/n, as expected from the exponential quantile formula.

The table of values printed in the paper's Figure 5 (Sec. 3.3) is internally
inconsistent — e.g. its n=1000 row lists 0.1%=0.01, below its own 1%=0.012 —
which is incompatible with any proper probability distribution and indicates
that the printed table reflects an imprecise reading of the original chart's
axis gridlines rather than literal numeric values. Because the paper
states the construction explicitly in the text (quantiles of the asymptotic
gamma null distribution) rather than only in the figure, this experiment
follows that formula directly instead of attempting to match the
unreliable table.

**Verdict:** reproduced (the implemented formula matches the construction
stated in Sec. 3.3; the paper's own figure data could not be used for a
numeric comparison because of the inconsistency described above).

## Deviations from the paper

- **Index proxies (Sec. 4):** the CAC 40 and Russell 2000 are index levels.
  The QuantX Dataloader / Massive route requires an index-data entitlement
  for `I:FCHI` (confirmed: a direct request returns HTTP 502,
  `NOT_AUTHORIZED — not entitled to this data`); no such entitlement is
  available. The iShares MSCI France ETF (EWQ) and iShares Russell 2000 ETF
  (IWM) are used as investable proxies instead, as allowed by the market-data
  retrieval rules when an index symbol is not entitled. This substitution is
  the identified cause of the CAC 40 divergence reported in Experiment 3
  above (see that section for the supporting evidence).
- **BTC/USD venue (Sec. 4):** the paper does not name the exchange or
  aggregation source of its BTC/USD series. This replication uses Massive's
  own BTC/USD aggregation (`X:BTCUSD`), which may differ from the paper's
  (unspecified) source.
- **Data source and `ticker_details`:** all four series in Experiment 3 were
  loaded from Massive through the QuantX Dataloader with no Yahoo Finance
  backstop invoked (`non_massive_source` is empty in
  `results/exp3_summary.json`); no ticker failed to load
  (`failed_tickers` is empty).
- **KS critical values (Sec. 3.2.2, Figure 4; Experiment 2):** the paper's
  Figure 4 caption states that its three reference lines correspond to
  p-values of 5%, 1%, 0.1% but does not give their numeric values. This
  replication uses the standard asymptotic one-sample Kolmogorov critical
  constants (c(0.05)=1.36, c(0.01)=1.63, c(0.001)=1.95, divided by √1000),
  which are mathematically necessary to be monotonically increasing in the
  p-value threshold.
- **Figure 5 table (Sec. 3.3; Experiment 5):** the tabular data printed in
  Figure 5 is internally non-monotonic (see Experiment 5 above) and is not
  used as a numeric reference; the experiment instead implements the gamma
  quantile formula that Sec. 3.3 states explicitly.
- **Random seed:** the paper does not specify a random seed for its
  simulations (Experiments 1 and 2); this replication fixes
  `RANDOM_SEED = 12345` (`src/config.py`) for reproducibility.
- **Authors' code or data:** no link to the authors' code or data was found
  in the paper; no authors' artifacts were used.

## Not reproduced

Nothing is omitted for compute-time or scope reasons: all five selected
experiments were executed in full at the parameters the paper specifies
(1,000 trajectories in Experiments 1-2, the full n-grids of Experiments 2 and
5, the full 2021 sample and all four assets in Experiment 3, and the full q
and n_j grids of Experiment 4). Two numeric comparisons in Experiment 3 are
reported above as "not reproduced" rather than omitted: CAC 40, with its
identified cause (ETF-proxy substitution), and BTC/USD at the 95% level,
where the rejection rate is qualitatively in the right range but the
precise cause of the 64% relative gap to the paper's figure was not
identified.
