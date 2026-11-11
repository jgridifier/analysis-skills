---
name: choose-analysis-method
description: Use first when asked to analyse a dataset and it is not yet clear which analysis fits — e.g. "find regimes", "when did this change", "which groups behave differently", "does the effect depend on conditions", "what drives this". Maps the question type and data shape to the right analysis skill and starting method in this repo, and says when none applies.
---

# Choose the analysis method

1. Write the question in one sentence and name the **data shape**: time series (ordered, dependent rows),
   cross-section (exchangeable rows), or panel (units × time).
2. Find the matching row below and load that skill. Use its method chooser for the exact method.
3. If no row matches, say so and do not force a method; propose the question for the methods scout.

| question type | data shape | skill | start with | baselines to always run |
|---|---|---|---|---|
| when did the behaviour (mean, volatility, correlation) change? | time series, uni- or multivariate | `run-changepoint-analysis` | changeforest random_forest on changes | change-in-mean, Binseg-rbf |
| is a claimed regime shift real? | time series | `run-changepoint-analysis` | changeforest + stationary VAR(1) null | iid shuffle null |
| which conditions mark groups that behave differently? | cross-section | `run-regime-tree-analysis` | ctree | CART, OLS |
| does a regression's slope depend on the state? | cross-section or time series | `run-regime-tree-analysis` | MOB `lmtree` | pooled OLS, OLS with interaction |
| which states precede big moves? (descriptive) | time series | `run-regime-tree-analysis` | ctree + circular-shift null | historical mean (walk-forward) |
| forecast the next value | time series | *none yet* — neither skill is a forecaster | — | historical mean / random walk |
| *(new question type)* | | *(new skill)* | | add one row per promoted skill or method |

Rules of thumb learned so far:
- Regimes **in time** → change points first; trees on time series need the circular-shift null.
- Groups **across units** → trees.
- Neither skill is evidence of predictive power; a forecasting claim needs a walk-forward test against the historical mean.
- Skills and methods enter this table only through `promote-method-to-skill` (see `docs/WORKFLOW.md`).
