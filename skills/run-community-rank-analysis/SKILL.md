---
name: run-community-rank-analysis
description: Use when you have a closed group of units observed over time and need to know whether their amounts co-move, and how their ranks rearrange — e.g. "do these series move together?", "who gained or lost rank?", "is the mix walking in one direction or just jittering?"
---

# Run a community rank-clock analysis

For a closed set of units (species, firms, programs) measured at the same times, describe co-movement of *amounts* and rearrangement of *ranks*. Rank clocks are the visual of each unit's rank over time; `rank_shift` summarises how much the rank order changes; `rate_change` asks whether composition walks in one direction; the variance ratio (VR) and synchrony ask whether raw amounts co-move.

Recommended method: **codyn** (Hallett et al. 2016), approved 2026-11-13 for rank clocks, with VR, synchrony and rate-of-change from the same scout kept in this skill. Teaching page: https://jgridifier.github.io/research-lab/methods-scout/2026-11-12-adhoc.html#m1. Approval: [`methods/codyn/APPROVAL.md`](../../methods/codyn/APPROVAL.md). Evidence: [`methods/codyn/RESULTS.md`](../../methods/codyn/RESULTS.md). Transparent; no neural nets.

The three-application reproduction pipeline has not been run on this repo's real panels; the evidence is the 2026-11-12 ad hoc scout (a public FR Y-9C *proxy* panel, descriptive only) plus the `--synthetic` self-test. Say so when you use this skill.

## 1. Pre-process (mandatory)

- Build a balanced tidy panel: time, unit, amount. If the panel is not closed (units appear and disappear), say so; turnover is then meaningful, and rank clocks are harder to compare.
- Split the analysis:
  - **Raw amounts** for variance-ratio and synchrony.
  - **Shares** (amount / time-total) for rank shift, rank clocks, and rate of compositional change.
- **Never** compute VR on shares of a closed composition: \(\mathrm{Var}(\sum \text{shares}) = 0\), so VR is degenerate (~0). The scout recorded this explicitly.

## 2. Choose the method

| method | use when | don't use when |
|---|---|---|
| **codyn `rank_shift` + rank clocks (on shares)** — start here for rearrangement | you want who gained or lost rank | you only have two units (a clock is then a see-saw) |
| **codyn `variance_ratio` (on raw amounts)** | do the amounts co-move? | applied to shares of a closed whole |
| `synchrony` (Loreau or Gross, raw amounts) | a 0–1 companion to VR | as a substitute for a cyclic-shift null |
| `rate_change` (on shares) | is composition walking in one direction? | without a cyclic-shift null (a trend in noise can look directional) |
| Cyclic-shift null (mandatory companion) | every VR, rank-shift, and rate-of-change claim | replacing it with an iid shuffle (that destroys autocorrelation) |

## 3. Robustness protocol (report all of it)

- Cyclic-shift null: independently rotate each unit's series, keeping its own autocorrelation (Hallett et al. 2014). Report the observed value against the null range and a one-sided p.
- Leave-outs: a subset that does *not* co-move can be hidden in the aggregate VR (on the scout, foreign-only VR was 0.73 and inside its null, while the 14-unit VR was 4.45).
- Windows: split the sample (the scout used pre-2020 / 2020-on).
- On a closed balanced panel, appearance and disappearance turnover is identically 0; do not report it as a finding.

## 4. Interpret and report

- VR > 1 (and above the cyclic-shift null) means raw amounts co-move more than independent unit-level paths would. VR inside the null is not co-movement.
- Mean rank shift *below* the null means ranks are unusually stable; *above* means unusually jumpy. The scout's 14-unit panel was unremarkable on rank shift; the four-unit revenue panel was unusually stable.
- A significant rate of change means composition is walking in one direction, not just jittering.

This skill is descriptive. It is not a forecast, and it is not evidence for a pre-registered forecasting study that happens to use a related panel.

Template: question; n units, n times, period; raw-vs-shares split; VR / synchrony vs cyclic-shift null, with leave-outs; rank-shift and clocks vs null; rate of change vs null; limitations (including that Stage 2–3 has not been run on the real panels).

## 5. Scripts

`scripts/rank_clocks.R`

```bash
Rscript skills/run-community-rank-analysis/scripts/rank_clocks.R --synthetic
Rscript skills/run-community-rank-analysis/scripts/rank_clocks.R --csv panel.csv --time t --unit species --value y --out results.json
```

`--synthetic` builds a co-moving community and an independent one (seed 20261113), checks that VR is above a short cyclic-shift null only on the co-moving set, and recovers a designed two-way rank swap with `rank_shift`. When `methods/codyn/original/scout_aggregates.json` is present, it also locks the scout's published VR, null range, foreign-only leave-out, and rate-of-change p-value.

## Citations

Hallett, L. M. et al. (2016). "codyn: An R package of community dynamics metrics." *Methods in Ecology and Evolution* 7(10):1146–1151. doi:10.1111/2041-210X.12611. Package [codyn](https://cran.r-project.org/package=codyn) 2.0.6. Cyclic-shift null: Hallett et al., *Proceedings of the Royal Society B* (2014) and the package documentation. Variance ratio: Schluter, *Ecology* 65(3):743–754 (1984).
