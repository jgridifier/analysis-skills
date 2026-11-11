# partykit — Stage 3 results and Stage 4 decision

Original = the 2026-11-10 scout run (`original/m1_results.json`, R 4.4.3, partykit 1.2-29, rpart 4.1.27, conda env `rscout`).
Reproduction = ported scripts in `applications/{1,2,3}/run.R`, run in a **fresh conda prefix built from `env/r-conda-lock.txt`**
(103 pinned conda-forge packages; same versions) on panels rebuilt by `common/prep_panels.py`. All five derived panels
were byte-identical (sha256) to the scout's panels. Comparison: `common/compare.py`, default abs tolerance 1e-4.

| app | question | values compared | strict mismatches | status |
|---|---|---|---|---|
| 1 | credit-spread regimes (ctree + walk-forward + block bootstrap) | 106 | 0 | **PASS (exact)** |
| 2 | MOB: VIX→spread sensitivity by state | 26 | 0 | **PASS (exact)** |
| 3 | county unemployment-shock subgroups | 97 | 13 (all CV RMSE/R²) | **PASS at stated tolerance** (abs 0.03 on CV fields) |

App 3 note: the scout drew its 5-fold CV assignment after other analyses had consumed the RNG stream; the ported script
starts a fresh stream, so fold assignment differs. Every tree, leaf, rule and count is exact; only CV scores move
(largest move 0.018 R²). The original value sits inside the 10-seed range for 5 of 6 scores; the COVID ctree score
(0.2513) is just below that range (0.2547–0.2779).

## Application 1 — credit-spread regimes (monthly, n = 423, 1991-01 → 2026-03)
Response: 6-month-ahead change in the GZ credit spread. Features: VIX, 10y–2y, NFCI, 2y, 12m Δ2y, EBP, 12m Δmortgage, 3m ΔGZ.

| number | original | reproduced |
|---|---|---|
| leaves / root split | 4 / VIX ≤ 31.94 | 4 / VIX ≤ 31.94 |
| leaf VIX > 31.9: n, mean 6m ΔGZ | 24, −1.404 | 24, −1.404 |
| leaf VIX ≤ 31.9 & NFCI > −0.063: n, mean, P(widen > 50bp) | 25, +0.921, 0.56 | 25, +0.921, 0.56 |
| walk-forward OOS R² vs historical mean (n = 267, 2004–2026): ctree / CART / OLS | −0.310 / −0.400 / −0.426 | −0.310 / −0.400 / −0.426 |
| block-bootstrap (300×, 24-month blocks): share with VIX at root | 0.683 | 0.683 |

Robustness (new): VIX-at-root share over 5 more bootstrap seeds 0.653–0.747. Windows: 1990–2007 root is 10y–2y ≤ 2.03,
2008–2026 root is VIX ≤ 27.3. **Null:** iid-permuted response → tree splits in 3% of 100 permutations; **circularly
shifted response (keeps autocorrelation) → splits in 60%.** Baseline: loses to the historical mean out of sample.
**Gates: reproduce ✓ · null ✗ · baseline ✗.**

## Application 2 — MOB: does the VIX→credit-spread sensitivity depend on the state? (monthly, n = 440)
Model `ΔGZ ~ ΔVIX + Δ10y | 10y–2y + NFCI + 2y + time`, `lmtree(minsize = 36, alpha = 0.01, bonferroni)`.

| number | original | reproduced |
|---|---|---|
| split | NFCI ≤ 0.057 | NFCI ≤ 0.057 |
| ΔVIX slope, NFCI ≤ 0.057 (n = 404) / > 0.057 (n = 36) | 0.0293 / 0.0587 | 0.0293 / 0.0587 |
| Δ10y slope, same leaves | −0.125 / −0.444 | −0.125 / −0.444 |
| pooled OLS ΔVIX slope | 0.0432 | 0.0432 |
| BIC pooled / MOB | −350.5 / −513.6 | −350.5 / −513.6 |
| root instability-test p: 10y–2y / NFCI / 2y / time | 0.197 / <1e-5 / 0.024 / 0.829 | same |

Robustness (new): windows — pre-2008 root is 2y ≤ 3.87, post-2008 root is NFCI ≤ −0.18; dropping 2008–09 and Mar–Jun 2020
still splits on NFCI (≤ −0.16). Baseline: OLS with an NFCI > 0.057 interaction has BIC −418.5 (MOB −513.6; part of MOB's
gain is the separate error variance per leaf); OLS with a 2008 break −347.8. **Null: circularly shifting the partitioning
variables (keeps their persistence) still produced a split in 53% of 100 shifts**, so the parameter-instability test is
picking up volatility clustering that any persistent state variable can flag.
**Gates: reproduce ✓ · null ✗ · baseline ✓ (with the variance caveat).**

## Application 3 — county subgroups hit hardest by the 2007–10 and 2019–20 unemployment shocks (n = 3,074 counties)
| number | original | reproduced |
|---|---|---|
| Great Recession tree: root / leaves | unemp 2007 ≤ 4.3 / 7 | same |
| COVID tree: root / leaves | log labor force 2019 ≤ 9.593 (≈14.6k) / 8 | same |
| COVID leaf means (pp rise in unemployment) | 1.10 (labor force ≤ ~2.3k and 2019 unemployment ≤ 5%) … 5.34 (labor force > ~426k) | same |
| 5-fold CV R², Great Recession: ctree / CART / OLS | 0.185 / 0.189 / 0.200 | 0.197 / 0.207 / 0.203 |
| 5-fold CV R², COVID: ctree / CART / OLS | 0.251 / 0.259 / 0.290 | 0.256 / 0.253 / 0.289 |

Robustness (new): 10 CV seeds — ctree 0.173–0.199 (GR), 0.255–0.278 (COVID); OLS 0.201–0.203, 0.287–0.292.
**Null:** iid-permuted response → splits in 0% (GR) and 4% (COVID) of 50 permutations (cross-section, so iid is the right null).
Baseline: ctree ties CART and is within 0.035 R² of OLS while giving 7–8 readable subgroups.
**Gates: reproduce ✓ · null ✓ · baseline ✓ (descriptive use).**

## Stage 4 decision: **PROMOTED (scoped)**
Reproduces in all three applications; application 3 clears all three gates. Scope of the skill:
cross-sectional subgroup discovery, and MOB as a description of state-dependent slopes. Time-series regime use is
allowed only behind a dependence-aware null (circular shift or block permutation), which both time-series applications
failed here; ctree's permutation p-values assume exchangeable rows and are too optimistic on autocorrelated monthly data.
Forecasting with the tree is not supported: it lost to the historical mean.
