---
name: run-empirical-bayes-shrinkage
description: Use when you have many noisy observations of unknown means (hundreds or thousands of short-history units) and need to shrink each one toward a shared prior, or to call which apparent moves are real — e.g. "which of these noisy changes are distinguishable from noise?", "how much should I borrow strength across programs?"
---

# Run an empirical-Bayes shrinkage analysis

For a large set of noisy observations \(x_i = \theta_i + \varepsilon_i\), \(\varepsilon_i \sim N(0, s_i^2)\), estimate a prior \(G\) from the whole set and report the posterior mean and the local false sign rate (lfsr) for each \(i\).

Recommended method: **ebnm** (Willwerscheid, Carbonetto & Stephens 2025), approved 2026-11-13. Teaching page: https://jgridifier.github.io/research-lab/methods-scout/2026-11-13.html#m1. Approval: [`methods/ebnm/APPROVAL.md`](../../methods/ebnm/APPROVAL.md). Evidence: [`methods/ebnm/RESULTS.md`](../../methods/ebnm/RESULTS.md). Transparent; no neural nets.

The three-application reproduction pipeline has not been run on this repo's real panels; the evidence is the 2026-11-13 scout (SYNTHETIC mock budgets) plus the `--synthetic` self-test. Say so when you use this skill.

## 1. Pre-process (mandatory)

- Each unit needs an observation \(x_i\) **and a standard error** \(s_i > 0\). If you do not have \(s_i\), estimate it from repeated measures or a residual spread, and shrink those estimates toward a group median (the scout used four pseudo-observations). Do not plug in a single global \(s\).
- Say what \(x_i\) is (level, log level, change, growth rate). Shrinkage is not invariant to a bad transform.
- Split out units that are not comparable (a different scale, a different data-generating process) before pooling.

## 2. Choose the method

| method | use when | don't use when |
|---|---|---|
| **ebnm, prior `normal_scale_mixture` (ash)** — start here | many noisy means; you want a flexible unimodal-at-mode mixture and lfsr | you have no \(s_i\); or the question is a text-vs-numbers mismatch (the scout showed no gain) |
| ebnm, prior `point_normal` | you expect a spike at the mode (many exact zeros / no-change) plus a normal slab | same limits as ash |
| ebnm, prior `normal` | a quick baseline; one normal prior | tails are heavier than normal (ash or npmle will fit better) |
| Unpooled \(x_i\) (baseline) | always report this | — |
| Complete-pooled group mean (baseline) | always report this | a group that is not exchangeable — complete pooling was *worse* than unpooled on the scout |

## 3. Robustness protocol (report all of it)

- Fit at least ash and point-normal, and both baselines.
- Report RMSE (or a proper scoring rule) against a holdout or a known truth when you have one; otherwise report 90% interval coverage and calibration of lfsr (wrong-sign rate in lfsr bins).
- Thresholding: quote the number of lfsr < 0.05 (and 0.01) calls, the false-sign rate among calls, and the comparison to a BH-adjusted z-test.
- If units come in families, also report within-family vs between-family error. Do not assume a family label is a good complete-pooling group.

## 4. Interpret and report

- Posterior mean = the shrunk estimate. lfsr = the posterior probability that the sign of \(\theta_i\) is wrong (or that \(\theta_i\) is zero, depending on the family). A small lfsr is a call that the move is real and of that sign.
- Complete pooling can over-shrink real differences; unpooled estimates are noisy. The useful answer is usually in between.
- This skill does **not** detect that a text description disagrees with the numeric path. Use it on the numbers.

Template: question; \(n\), what \(x_i\) and \(s_i\) are; prior families fit; unpooled vs complete-pooled vs ebnm error or coverage; lfsr calls vs BH; limitations (including that Stage 2–3 has not been run on the real panels).

## 5. Scripts

`scripts/shrinkage.R`

```bash
Rscript skills/run-empirical-bayes-shrinkage/scripts/shrinkage.R --synthetic
Rscript skills/run-empirical-bayes-shrinkage/scripts/shrinkage.R --csv observations.csv --x x --s s --out results.json
```

`--synthetic` fits ash on a 400-point spike-and-slab problem (seed 20261113) and checks that shrinkage beats both baselines and that lfsr < 0.05 calls have a low false-sign rate. When `methods/ebnm/original/scout_aggregates.json` is present, it also locks the scout's published RMSE and call counts.

## Citations

Willwerscheid, J., Carbonetto, P. & Stephens, M. (2025). "ebnm: An R Package for Solving the Empirical Bayes Normal Means Problem Using a Variety of Prior Families." *Journal of Statistical Software* 114(3):1–33. doi:10.18637/jss.v114.i03. Package [ebnm](https://cran.r-project.org/package=ebnm) 1.1.42.
