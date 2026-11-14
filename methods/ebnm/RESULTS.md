# ebnm — results and decision

**Status: PROMOTED** (Jared, 2026-11-13, 11:51 PM ET; see [APPROVAL.md](APPROVAL.md)).

The formal Stage 2–3 pipeline (three distinct applications on the analysis-skills real panels, clean-environment reproduction, seed/window/null/baseline gates) has **not** been run. Promotion in this repo is from the 2026-11-13 methods-scout run that Jared approved from, plus a `--synthetic` self-test in the skill script. That limitation is in force until a later Stage 2–3 pass is added.

Original aggregates: `original/scout_aggregates.json` (no per-program rows). Scout data were SYNTHETIC mock ZBB budgets, not real firm budgets. Package versions: ebnm 1.1.42, ashr 2.2.63, mixsqp 0.3.54, R 4.5.3. Seed 20261113.

## Scout evidence (2026-11-13, two mock firms)

Rounded the way the teaching page reports them; full tables are in the aggregate file.

### A1 — pooling 2025 levels (log RMSE vs true level)

| estimator | Corning mock (n = 998) | Morgan Stanley mock (n = 1,702) |
|---|---:|---:|
| Own 2025 actual (no pooling) | 0.146 | 0.138 |
| Group mean (complete pooling) | 0.267 | 0.261 |
| ebnm: normal | 0.119 | 0.114 |
| ebnm: point_normal | 0.109 | 0.110 |
| ebnm: ash (normal scale mixture) | 0.108 | 0.109 |
| ebnm: unimodal | 0.108 | 0.110 |
| ebnm: npmle | 0.108 | 0.110 |

Pooling cuts 2025-level log RMSE 0.146 → 0.108 (Corning mock) and 0.138 → 0.109 (Morgan Stanley mock). Complete pooling is worse than using each program's own actual. 90% interval coverage for ash is 0.895 and 0.895.

### A2 — which year-on-year moves are real (lfsr)

| rule | Corning mock n_calls / false-sign / true pos | Morgan Stanley mock n_calls / false-sign / true pos |
|---|---|---|
| Naive z, \|z\| > 1.96 | 141 / 0.043 / 135 | 292 / 0.027 / 284 |
| Naive + BH q < 0.05 | 14 / 0 / 14 | 28 / 0 / 28 |
| ebnm ash, lfsr < 0.05 | 91 / 0 / 91 | 200 / 0.015 / 197 |
| ebnm point-normal, lfsr < 0.05 | 104 / 0 / 104 | 199 / 0.015 / 196 |

On the Corning mock, lfsr < 0.05 calls 91 real year-on-year moves with 0 wrong signs, versus BH's 14. Growth-rate RMSE also falls (raw 0.201 → ash 0.079 on that mock; raw 0.196 → ash 0.098 on the other).

### A3 — text vs numbers (stated growth, planted decline)

No material gain. On the Corning mock, posterior-mean AUC is 0.741 vs 0.731 for the raw slope; on the Morgan Stanley mock, 0.624 vs 0.620. Precision at the planted set stays low. A follow-up on *relative* (description-implied) residuals (`m1c_relative.R`) likewise shows no reliable lift.

## Validation this turn

- **Stored aggregates** match the published teaching-page figures (the rounded RMSE and call counts above).
- **`--synthetic` self-test** (skill script): a spike-and-slab normal-means problem, fixed seed, checks that ash shrinks RMSE below the raw observations and that lfsr < 0.05 calls have a low false-sign rate. This does not re-fit the mock budgets.
- **Not re-run this turn:** the original scout scripts on the mock datasets (would need those inputs and is outside the "no heavy installs or builds" cap). The Rust-free skill script uses the ebnm package already present in the lab's R environment when run locally; CI installs ebnm from CRAN.

## Mandatory checks the skill carries

- Always compare against the unpooled observation and against the complete-pooled group mean; complete pooling can be worse than doing nothing.
- Report lfsr (or a stated posterior-probability threshold), not only a point estimate.
- Do not expect the method, by itself, to catch a mismatch between a text label and a numeric path.
- Needs a standard error for each observation; garbage `s` in, garbage shrinkage out.

## Stage 4 decision

Recommend promotion of ebnm for **shrinkage and calling real moves among many noisy observations**, on the scout evidence above. Scope does **not** include text-vs-numbers mismatch detection. A later three-application pass on the analysis-skills panels is still worth doing; it was not a condition of this approval.
