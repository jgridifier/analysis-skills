# Analysis skills

General, method-agnostic agent skills (Claude Code format: `skills/<name>/SKILL.md` + optional `scripts/`, `reference/`, `examples/`).

| skill | use it when | methods inside |
|---|---|---|
| [`choose-analysis-method`](choose-analysis-method/SKILL.md) | you have a dataset and a question but no method yet | router to the skills below |
| [`run-changepoint-analysis`](run-changepoint-analysis/SKILL.md) **DRAFT (pending approval)** | "when did the behaviour of this series change?" | changeforest (recommended, awaiting approval); change-in-mean, ruptures (baselines); fastcpd (watchlist) |
| [`run-regime-tree-analysis`](run-regime-tree-analysis/SKILL.md) **DRAFT (pending approval)** | "which conditions mark groups that behave differently?" / "does the slope depend on the state?" | partykit ctree + MOB (recommended (scoped), awaiting approval; well-known); CART (baseline); evtree, glmertree, stablelearner (watchlist) |
| [`promote-method-to-skill`](promote-method-to-skill/SKILL.md) | a scouted method is picked and must go through the workflow | meta skill for `docs/WORKFLOW.md` |

To use in Claude Code, copy or symlink a skill folder into `.claude/skills/` (project) or `~/.claude/skills/` (user).
DRAFT skills may be used only as drafts, and the agent must say so. A skill loses DRAFT only when its method has an `APPROVAL.md` (see `docs/WORKFLOW.md`, Stage 4b).
New methods are added as rows in a task skill's method chooser, not as new package skills.
