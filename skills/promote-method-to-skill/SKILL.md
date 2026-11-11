---
name: promote-method-to-skill
description: Use when a method from the methods scout (or any new analytical package) has been picked for adoption and needs to go through the repo's promotion workflow — three applications on real data, a clean-environment reproduction with robustness checks, a promote/reject decision, folding it into a general task skill, and publishing the method and application articles to the newsroom site.
---

# Promote a method to a skill

Follow `docs/WORKFLOW.md`; this is the checklist form. Never commit raw or row-level private data
(aggregates, fitted structure, figures and scripts only). No neural nets. Never invent or round away a number;
report mismatches as mismatches.

## Stage 1 — Candidate
- [ ] `methods/<method>/README.md`: citation(s), package + version, core language, question type, source scout run.
- [ ] Data: put raw files in `$AS_DATA_DIR` (not in git); extend `common/prep_panels.py` (Drive id, retrieval date) and rerun it
      so `data/MANIFEST.json` records rows and sha256.

## Stage 2 — Three applications (`methods/<method>/applications/{1,2,3}/`)
- [ ] Three **distinct** uses (different question or data shape). Each: `run.R`/`run.py` with a fixed seed, reading only
      `$AS_WORK_DIR` panels; writes `out/results.json` (aggregates only) and figures to `$AS_FIG_DIR`.
- [ ] `manifest.json` per application (extend `common/app_manifest.py`): raw file, Drive id, retrieval date, rows, sha256, panels, env, seed, command.
- [ ] Pin the environment in `env/` (pip freeze; conda explicit lock for R; package version list).
- [ ] Keep a copy of the first ("original") results: `methods/<method>/original/` or `applications/<n>/out_original_*`.

## Stage 3 — Reproduce and stress
- [ ] Build fresh environments from the lockfiles; rebuild panels; rerun (`reproduce.sh`).
- [ ] `python common/compare.py ORIGINAL REPRO applications/<n>/reproduction.json` — default abs 1e-4. Any looser tolerance
      only for RNG streams that cannot be replayed; state it and the strict mismatch count.
- [ ] Robustness in each `results.json`: 10 seeds (report what recurs ≥ 8/10), windows, a **dependence-aware null**
      (iid shuffle is not enough for time series: circular shift or stationary VAR(1)), and the plain baseline.
- [ ] `methods/<method>/RESULTS.md`: per application — question, original vs reproduced key numbers, match status, robustness, gates.

## Stage 4 — Decide
- [ ] Gates per application: reproduces · clears the null · clears the baseline.
- [ ] **Promote** if all three reproduce and at least one application clears all gates; scope the skill to the uses that cleared,
      and turn every failed gate into a mandatory check or anti-pattern. Otherwise **reject** with the reason in RESULTS.md.

## Stage 5 — Skill
- [ ] If a task skill for the question type exists (`run-changepoint-analysis`, `run-regime-tree-analysis`, …), add a row to its
      method chooser and its `reference/evidence.md`. Otherwise create `skills/run-<task>/SKILL.md`: YAML frontmatter `name`, and
      `description` that says **when** to use it; sections pre-process → method chooser table → robustness protocol → interpret
      and report (with template) → scripts → citations. Add runnable `scripts/` with a `--synthetic` self-test.
- [ ] Add a row to `skills/choose-analysis-method/SKILL.md` and `skills/README.md`.
- [ ] CI (`.github/workflows/smoke.yml`) must pass: frontmatter check + each script's `--synthetic` run.

## Publish — newsroom articles (`docs/`, theme `docs/assets/brief.css`)
- [ ] Append to `docs/articles.json` one **method** entry and one **application** entry per application:
      `{slug, title, type: "method"|"application", method, date, tags, dek, verdict, links: {self, parent, children, code, results, skill}}`.
- [ ] Method article (`docs/articles/<method>.html`), in order: citation first → plain math → why it is unusual or fast →
      verdict → reproduction status per application → links to each application article → skill.
- [ ] Application article (`docs/articles/<method>-app<n>.html`), in order: question → data used (sources, n, period;
      aggregates only) → what we ran → figures and tables → original vs reproduced → robustness → limitations → takeaway →
      link back to the method article.
- [ ] Article bodies live in `docs/content/<slug>.html` (fragment); run `python docs/build.py` to render the pages and the
      front page (lead story = newest method article, then a card grid of all articles, newest first, tagged by method and skill).
- [ ] Check the Pages URL returns 200 after merge.
