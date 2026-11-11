# changeforest — Stage 3 results and Stage 4 decision

Original = the 2026-11-10 scout run (`original/m2_results.json`; Python 3.13.5, changeforest 1.2.1, ruptures 1.1.10,
scikit-learn 1.9.1) for applications 1–2. Application 3 is new in this repo: its "original" is the first run in the
scout venv (`applications/3/out_original_scoutenv/`). Reproduction = a **fresh venv built from `env/requirements.lock.txt`**
(identical `pip freeze`), on panels rebuilt by `common/prep_panels.py` (byte-identical to the scout's). Timings are never compared.

| app | question | values compared | mismatches | status |
|---|---|---|---|---|
| 1 | weekly regimes in six rate/stress series (changes; levels as pre-processing check) | 585 | 0 | **PASS (exact)** |
| 2 | daily volatility/correlation regimes (n = 9,174) + scaling | 275 | 0 | **PASS (exact)** |
| 3 | monthly credit-spread regimes (GZ, EBP, log VIX, 10y) | 73 | 0 | **PASS (exact)** — same package versions, so this is a determinism check, not a cross-version one |

## Application 1 — weekly changes of log VIX, 10y–2y, 2y, mortgage rate, NFCI, STLFSI4 (n = 1,709, 1994-01 → 2026-10)
| number | original | reproduced |
|---|---|---|
| breaks on LEVELS (pre-processing check) | 63, median gap 27 weeks | 63, median gap 27 weeks |
| breaks on weekly CHANGES (default seed) | 35 | 35 (same dates) |
| change-in-mean breaks | 0 | 0 |
| breaks across 10 seeds | 32–47 | 32–47 |
| iid-shuffled data, 5 shuffles | 0 each | 0 each |
| first-70% refit: share of breaks recovered | 0.76 | 0.76 |
| overlap with Binseg-rbf / Binseg-l2 (same K, ±13 weeks) | 0.57 / 0.29 | 0.57 / 0.29 |

Robustness (new): 28 of 35 breaks recur in ≥ 8 of 10 seeds. **Stationary VAR(1) null** (fitted to the data, constant
Gaussian innovations, no breaks by construction; spectral radius 0.957): **20–37 breaks in 5 simulations — as many as
the real data.** On levels the same null gives 64–71 (radius 0.997), which explains the 63-break artifact. So weekly changes
are still too persistent for changeforest's independence assumption (weekly averages of daily data and the smoothed stress
indices are autocorrelated). Remedy tested: prewhiten with a VAR(1) and rerun on residuals → 22 breaks, 17–22 across seeds,
**12 recur in ≥ 8/10 seeds** (incl. 2007-07, 2008-10, 2019-12, 2020-06, 2022-01), VAR(1) null on residuals 0–2 breaks.
**Gates (raw changes): reproduce ✓ · null ✗ · baseline ✓. With prewhitening: null ✓ (0–2 vs 22).**

## Application 2 — daily changes of log VIX, 10y–2y, 2y, 10y (n = 9,174, 1990 → 2026)
| number | original | reproduced |
|---|---|---|
| breaks (default seed) | 28 | 28 (same dates) |
| change-in-mean breaks | 0 | 0 |
| iid-shuffled, 3 shuffles | 0 each | 0 each |
| synthetic one-variance-break scaling: break found at n/2 for n = 1k…16k | yes (500, 1000, 2006, 4003, 8009) | same |

Robustness (new): 28–36 breaks across 10 seeds; 23 of 28 recur in ≥ 8/10 (±63 trading days). VAR(1) null (radius 0.50):
0 breaks in 3 simulations. Segments separate high-vol episodes (10y daily sd 0.10 in Oct 2008–Mar 2009 vs 0.036–0.04 in
2016–19) and flips in the VIX–10y correlation (−0.56 in Aug 2011–Feb 2012; +0.13 to +0.26 in 2022-05 → 2024-07).
16k rows in 0.72 s here (timings depend on the machine). **Gates: reproduce ✓ · null ✓ · baseline ✓.**

## Application 3 — monthly changes of GZ spread, EBP, log VIX, 10y (n = 440, 1990-02 → 2026-09; new)
| number | original (scout venv) | reproduced (clean venv) |
|---|---|---|
| breaks | 1998-08, 2012-07 | same |
| sd of ΔGZ by segment | 0.069 / 0.331 / 0.205 | same |
| corr(ΔGZ, Δlog VIX) by segment | −0.02 / 0.70 / 0.68 | same |
| seeds: break count; recurrence of each break | 2–4; 0.9 and 0.8 | same |
| change-in-mean / kNN breaks | 0 / 5 (2000–2004) | same |
| iid-shuffled (10) and VAR(1) null (10, radius 0.42) | 0 every time | same |

Limitation: binary segmentation with these settings does not isolate the 2008–09 or 2020 spikes as their own segments.
**Gates: reproduce ✓ · null ✓ · baseline ✓.**

## Status: **RECOMMENDED, AWAITING APPROVAL**
Not promoted. Under Stage 4b, promotion needs Jared's own dated approval recorded in `methods/changeforest/APPROVAL.md`, and that file does not exist.

## Stage 4 decision: **recommend promotion**
Reproduces exactly in all three applications; applications 2 and 3 clear every gate, and application 1 clears them after
prewhitening. Lessons the skill makes mandatory: never run it on levels; check persistence (VAR(1) spectral radius) of
the transformed input and prewhiten if it is high; always run the stationary VAR(1) null, because the iid shuffle passed
even where the VAR null failed; report only breaks that recur in ≥ 8 of 10 seeds.
