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
| when did the behaviour (mean, volatility, correlation) change? | time series, uni- or multivariate | `run-changepoint-analysis` **DRAFT (pending approval)** | changeforest random_forest on changes | change-in-mean, Binseg-rbf |
| is a claimed regime shift real? | time series | `run-changepoint-analysis` **DRAFT (pending approval)** | changeforest + stationary VAR(1) null | iid shuffle null |
| which conditions mark groups that behave differently? | cross-section | `run-regime-tree-analysis` **DRAFT (pending approval)** | ctree | CART, OLS |
| does a regression's slope depend on the state? | cross-section or time series | `run-regime-tree-analysis` **DRAFT (pending approval)** | MOB `lmtree` | pooled OLS, OLS with interaction |
| which states precede big moves? (descriptive) | time series | `run-regime-tree-analysis` **DRAFT (pending approval)** | ctree + circular-shift null | historical mean (walk-forward) |
| which of many noisy observations should be shrunk, and which moves are real? | many units, each with an estimate and a standard error | `run-empirical-bayes-shrinkage` | ebnm ash (normal scale mixture) | unpooled observation, complete-pooled group mean, BH z-test |
| how do I see the typical shape and unusual branches in hundreds of overlapping short series? | a bundle of aligned short series (panel of paths) | `run-line-density-chart` | DenseLines with `gap_safe=True` | unnormalised overlay |
| do these units' amounts co-move, and how do their ranks rearrange? | closed panel (units × time) | `run-community-rank-analysis` | codyn rank clocks + variance ratio, with a cyclic-shift null | iid shuffle is not a sufficient null |
| forecast the next value | time series | *none yet* — none of the skills is a forecaster | — | historical mean / random walk |
| *(new question type)* | | *(new skill)* | | add one row per skill or method (DRAFT until approved) |

**changeforest and partykit remain DRAFT (pending approval).** ebnm, DenseLines and codyn rank clocks were approved by Jared on 2026-11-13 (see each method's `APPROVAL.md`). Their Stage 2–3 three-application pipeline has not been run; say that when you use those skills. Lovell proportionality was approved in the same message but is not promoted; its direction is still to be decided.

Rules of thumb learned so far:
- Regimes **in time** → change points first; trees on time series need the circular-shift null.
- Groups **across units** → trees.
- Many noisy means → ebnm; do not use it to catch a text-vs-numbers mismatch.
- A spaghetti chart of many short series → DenseLines, with `gap_safe=True` if spans differ, and a brush-sensitivity check.
- Co-movement and rank rearrangement in a closed group → codyn; VR on raw amounts, ranks on shares, always a cyclic-shift null.
- None of these skills is evidence of predictive power; a forecasting claim needs a walk-forward test against the historical mean.
- Skills and methods enter this table only through `promote-method-to-skill` (see `docs/WORKFLOW.md`), plus Jared's dated approval for a non-DRAFT skill.
