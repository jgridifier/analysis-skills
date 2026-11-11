# changeforest — random-forest change-point detection

- **Citation:** Londschien, Bühlmann & Kovács (2023), "Random Forests for Change Point Detection", *JMLR* 24(216):1–45.
- **Package:** `changeforest` 1.2.1 (Rust core, Python and R bindings). Baselines: `change_in_mean` (same package), `ruptures` 1.1.10 Binseg (l2, rbf), scikit-learn k-means.
- **Question type:** where does the joint distribution (variance, correlation, shape — not just the mean) of a multivariate series change?
- **Scout run:** research-lab `docs/methods-scout/runs/2026-11-10/m2_changeforest.py`, `m2b.py`.
- **Applications:** `applications/1` weekly regimes of six rate/stress series, `applications/2` daily volatility/correlation regimes, `applications/3` monthly credit-spread regimes (new in this repo).
- **Status:** see [RESULTS.md](RESULTS.md). Skill: [`run-changepoint-analysis`](../../skills/run-changepoint-analysis/SKILL.md).
