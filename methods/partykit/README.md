# partykit — conditional inference trees (ctree) and model-based trees (MOB)

- **Citations:** Hothorn, Hornik & Zeileis (2006), "Unbiased Recursive Partitioning: A Conditional Inference Framework", *JCGS* 15(3):651–674.
  Zeileis, Hothorn & Hornik (2008), "Model-Based Recursive Partitioning", *JCGS* 17(2):492–514.
  Hothorn & Zeileis (2015), "partykit: A Modular Toolkit for Recursive Partytioning in R", *JMLR* 16:3905–3909.
- **Package:** R `partykit` 1.2-29 (CRAN), C core via `libcoin`. Baseline: `rpart` 4.1.27 (CART).
- **Question type:** regime / subgroup discovery with a readable tree; MOB for "does a regression's slope depend on the state?".
- **Scout run:** research-lab `docs/methods-scout/runs/2026-11-10/m1_partykit.R` (analyses A1–A4).
- **Applications:** `applications/1` credit-spread regimes (A1+A2), `applications/2` MOB VIX sensitivity (A3), `applications/3` county shock subgroups (A4).
- **Status:** see [RESULTS.md](RESULTS.md). Skill: [`run-regime-tree-analysis`](../../skills/run-regime-tree-analysis/SKILL.md).
