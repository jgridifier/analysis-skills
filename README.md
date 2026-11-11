# analysis-skills

General agent skills for data analysis (Claude Code format), built by running lesser-known, fast, interpretable methods
through a reproduce-then-promote workflow on our own data. No neural nets. No raw data in the repo: only scripts,
lockfiles, aggregates, fitted structure and figures.

- **Newsroom (Pages):** https://jgridifier.github.io/analysis-skills/ — a method article per method, an article per application.
- **Workflow:** [docs/WORKFLOW.md](docs/WORKFLOW.md) (agent version: [skills/promote-method-to-skill](skills/promote-method-to-skill/SKILL.md)).
- **Skills:** [skills/README.md](skills/README.md) — `choose-analysis-method`, `run-changepoint-analysis`, `run-regime-tree-analysis`, `promote-method-to-skill`.

| method | applications | reproduction | decision | skill |
|---|---|---|---|---|
| [changeforest](methods/changeforest/RESULTS.md) (Londschien, Bühlmann & Kovács 2023, JMLR 24(216)) | 3 | 3/3 exact | **promoted** | run-changepoint-analysis |
| [partykit ctree/MOB](methods/partykit/RESULTS.md) (Hothorn, Hornik & Zeileis 2006; Zeileis, Hothorn & Hornik 2008; Hothorn & Zeileis 2015) | 3 | 2/3 exact, 1/3 at stated tolerance (CV folds) | **promoted (scoped)** | run-regime-tree-analysis |

## Layout
```
common/        prep_panels.py (raw Drive files -> panels + data/MANIFEST.json), compare.py (Stage 3), app_manifest.py, check_repo.py (CI)
env/           requirements.lock.txt (pip freeze), r-conda-lock.txt (explicit conda lock, R 4.4.3), r-packages.csv
methods/<m>/   README.md, RESULTS.md, original/ (first-run results), applications/{1,2,3}/{run.*, manifest.json, out/results.json, reproduction.json}
skills/<s>/    SKILL.md (+ scripts/, reference/, examples/)
docs/          Pages newsroom: index.html, articles/, content/ (article bodies), articles.json (manifest), build.py, assets/brief.css, fig/
reproduce.sh   Stage 3 end to end (needs the raw files in $AS_DATA_DIR)
```

## Reproduce
```bash
export AS_DATA_DIR=/path/to/raw/drive/files   # see data/MANIFEST.json for names, Drive ids and sha256
./reproduce.sh
```
CI (`.github/workflows/smoke.yml`) checks skill frontmatter, the article manifest and that the site is rebuilt, and runs each skill
script's `--synthetic` example (Python job for changeforest, R job for partykit). CI does not touch real data.

MIT licensed.
