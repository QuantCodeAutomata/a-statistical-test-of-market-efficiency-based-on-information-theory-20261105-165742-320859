"""Parameters for the replication of
'A statistical test of market efficiency based on information theory'.

Every module-level variable is used by exactly one experiment (see the
comment headers) and carries the paper section or equation it comes from.
No value here is a free modelling choice: when the paper does not state a
number, the comment says so explicitly.
"""

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------
RANDOM_SEED = 12345  # not specified in the paper; fixed for reproducibility

# ---------------------------------------------------------------------------
# exp_1: simulation validation of the asymptotic gamma distribution (Sec. 3.2.2,
# Figures 2 and 3)
# ---------------------------------------------------------------------------
EXP1_N_TRAJECTORIES = 1000  # number of simulated trajectories, Figures 2-3 captions
EXP1_L_VALUES = [1, 2]  # prefix lengths used in Figures 2 (L=1) and 3 (L=2)
EXP1_N_BY_L = {1: 100, 2: 4000}  # sample size n used with each L, Figures 2 and 3 captions

# ---------------------------------------------------------------------------
# exp_2: Kolmogorov-Smirnov test of the gamma approximation vs. n (Sec. 3.2.2,
# Figure 4)
# ---------------------------------------------------------------------------
EXP2_L = 1  # prefix length used in Figure 4 (shape k = 2^(L-1) = 1)
EXP2_N_GRID = [25, 50, 75, 100, 125, 150, 200, 300, 400, 600, 800, 1000]  # implementation_notes
EXP2_N_TRAJECTORIES = 1000  # sample size of the simulated distribution, consistent with Figures 2-4
# KS critical values for a one-sample test against a fully specified CDF, sample size m:
# D_crit(alpha) = c(alpha) / sqrt(m), with c(0.05)=1.36, c(0.01)=1.63, c(0.001)=1.95
# (standard asymptotic Kolmogorov critical constants; not given numerically in the paper)
EXP2_KS_CRITICAL_CONSTANTS = {0.05: 1.36, 0.01: 1.63, 0.001: 1.95}

# ---------------------------------------------------------------------------
# exp_3: empirical application to CAC 40, Russell 2000, Perficient and BTC/USD
# (Sec. 4, Figure 6)
# ---------------------------------------------------------------------------
EXP3_L = 1  # prefix length used in the empirical study, Sec. 4
EXP3_N = 100  # rolling-window length in business days, Sec. 4
EXP3_CONFIDENCE_LEVELS = [0.95, 0.99, 0.999]  # Sec. 4 test confidence levels
EXP3_START_DATE = "2020-01-01"  # history needed before 2021 to fill the first rolling window
EXP3_END_DATE = "2021-12-31"  # sample period is the year 2021, Sec. 4
EXP3_DISPLAY_START = "2021-05-31"  # "end May 2021" for the three slower-trading series, Sec. 4
EXP3_DISPLAY_END = "2021-12-31"  # "end December 2021", Sec. 4
EXP3_BTC_DISPLAY_START = "2021-04-11"  # BTC/USD starts earlier because it trades every day, Sec. 4
# Tickers: CAC 40 and Russell 2000 are index levels. The Dataloader/Massive route serves
# equities and ETFs, not raw index levels without an index entitlement; the closest
# investable proxies are used instead (see "Deviations from the paper" in results/RESULTS.md).
EXP3_TICKERS = {
    "CAC40": "EWQ",       # iShares MSCI France ETF, proxy for the CAC 40 index
    "RUSSELL2000": "IWM",  # iShares Russell 2000 ETF, proxy for the Russell 2000 index
    "PERFICIENT": "PRFT",  # Perficient Inc. common stock
    "BTCUSD": "X:BTCUSD",  # BTC/USD spot pair, Massive crypto notation
}

# ---------------------------------------------------------------------------
# exp_4: numerical evaluation of the error bound of Theorem 2 (Sec. 3.2.1,
# Figure 1)
# ---------------------------------------------------------------------------
EXP4_Q_VALUES = [2, 3, 4, 5]  # free parameter q in the bound, Figure 1 caption
EXP4_T = 1.0  # value of t used in Figure 1, Figure 1 caption
EXP4_P_J_L = 0.5  # value of p_j^L used in Figure 1, Figure 1 caption
EXP4_EPSILON = 1.0  # asymptotic bound uses epsilon -> 1, Sec. 3.2.1 text after Theorem 2
EXP4_NJ_GRID = list(range(0, 1001, 50))  # n_j range inferred from the Figure 1 table, 0 to 1000 step 50

# ---------------------------------------------------------------------------
# exp_5: p-value threshold chart for the market efficiency test (Sec. 3.3,
# Figure 5)
# ---------------------------------------------------------------------------
EXP5_L = 1  # Figure 5 uses I^2, i.e. L = 1
EXP5_ALPHAS = [0.05, 0.01, 0.001]  # p-value thresholds shown in Figure 5
EXP5_N_GRID = list(range(10, 1001, 10))  # n range inferred from the Figure 5 table, 0 to 1000
