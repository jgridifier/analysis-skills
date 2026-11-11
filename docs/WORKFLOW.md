# Workflow: from scouted method to general skill

This is the pipeline every candidate method goes through before an agent is allowed to use it.
It runs in five stages. Each stage leaves files in the repo, so anyone can check what was done.
The same steps are packaged for agents as [`skills/promote-method-to-skill`](../skills/promote-method-to-skill/SKILL.md).

Rules that apply at every stage: no raw or row-level private data is committed (aggregates, fitted
structure, figures and scripts only); no neural nets; never invent a number, and report mismatches as mismatches.

## Stage 1 — Candidate
A method from the daily methods scout (research-lab `docs/methods-scout/`) is picked.
Create `methods/<method>/README.md` with: citation(s), package and version, language of the core,
what question type it answers, and the scout run it came from.

## Stage 2 — Three applications
Three **distinct** uses on our real data, each in `methods/<method>/applications/{1,2,3}/`:

| file | what it holds |
|---|---|
| `run.R` / `run.py` | one script, fixed seed, reads only the panels built by `common/prep_panels.py` |
| `manifest.json` | data manifest: raw source file, Drive file id, retrieval date, row counts, sha256 of the fetched bytes (the data itself is not committed), derived panels with their hashes, environment, seed, command |
| `out/results.json` | aggregates only: fitted structure, segment/leaf summaries, scores |

Environments are pinned in `env/`: `requirements.lock.txt` (pip freeze), `r-conda-lock.txt`
(explicit conda-forge lock for R 4.4.3) and `r-packages.csv` (R package versions).
"Distinct" means a different question or a different data shape (time series vs cross-section, daily vs monthly),
not the same fit with a different parameter.

## Stage 3 — Reproduce and stress
1. Rebuild the environment **from the lockfiles** in a fresh prefix (`reproduce.sh`), rebuild the panels,
   rerun every application.
2. `common/compare.py ORIGINAL REPRO OUT` compares every shared value. Default tolerance: abs 1e-4 on floats
   (results are stored to 5 significant digits), exact on strings and integers. Wall-clock timings and versions
   are never compared. A looser tolerance is allowed **only** for RNG-dependent quantities whose RNG stream
   could not be replayed, and it must be stated in `RESULTS.md` along with the strict-mode mismatch count.
3. Robustness, each written into `out/results.json`:
   - **seeds**: 10 seeds; report what recurs in at least 8 of 10;
   - **windows**: split sample or leave-crisis-out refits;
   - **null**: a null that keeps the dependence structure of the data. An iid shuffle is necessary but **not
     sufficient** for time series: use a circular shift (trees) or a stationary VAR(1) simulation (change points);
   - **baseline**: the plain alternative (historical mean, OLS, CART, change-in-mean, k-means).
4. Record PASS / MISMATCH per application in `reproduction.json` and in `methods/<method>/RESULTS.md`.

## Stage 4 — Decide
For each application, three gates: **reproduces** (Stage 3.2), **clears the null**, **clears the baseline**
(for a forecasting use: beats the baseline out of sample; for a descriptive use: finds structure the baseline does not,
without being materially worse than it on held-out fit).

- **Recommend for promotion** a method when it reproduces in all three applications and at least one application clears all three gates.
  The skill's scope is limited to the uses that cleared; every failed gate becomes a mandatory check or an
  anti-pattern in the skill.
- **Reject** otherwise, with the reason, in `RESULTS.md` (`Decision: REJECTED — <reason>`). Rejected methods stay in
  the repo so the scout doesn't propose them again.

Note on provenance: these gates were written during the first run (partykit and changeforest, 2026-11-10),
after their results were visible. The next method through the pipeline is the first one judged by rules fixed in advance.

## Stage 4b — Jared's approval (required for every promotion)
A Stage 4 "promote" is only a **recommendation**. The method's status is
**`recommended, awaiting approval`** until Jared approves it himself.

- It becomes **`promoted`** only when Jared's own words, with the date, are recorded in `methods/<method>/APPROVAL.md`:
  his verbatim text, the date, the channel it came from, and the commit or PR it approves.
- An agent relaying that "he agreed", a summary, or an inferred yes does **not** count.
- **No agent may create or edit `APPROVAL.md` on its own.** It is added only on Jared's explicit instruction, and it quotes him word for word.
- Until then, the skill built in Stage 5 is marked **DRAFT (pending approval)** in `skills/README.md` and in the
  `choose-analysis-method` router. Its files stay in the repo, and agents may use it only as a draft, saying so.
- Every status shown on the site (`articles.json`, the method and application articles, the front page) must match
  this status.
- Rejections don't need approval. They are recorded as rejected, with the reason.

## Stage 5 — Skill
Fold what was learned into a **general task skill** (`run-changepoint-analysis`, not `use-changeforest`).
A task skill has: when to use it (frontmatter `description`), pre-processing, a method chooser table with one row
per method (new methods slot in by adding a row), the robustness protocol, interpretation and a reporting template,
runnable `scripts/`, and citations. Then add a row to `skills/choose-analysis-method/SKILL.md` and to `skills/README.md`.
If the skill for the question type already exists, add a method row instead of a new skill.

## Publishing: the newsroom
Every recommended, promoted or rejected method is published on the Pages site (`docs/`) as news articles in the shared
`brief.css` theme:

- **Front page** `docs/index.html`: lead story (newest method article) plus a card grid of every article,
  newest first, each tagged by method and skill. Built from the manifest.
- **One method article** per method, `docs/articles/<method>.html`, in this order:
  1. citation(s) first; 2. the math in plain notation; 3. why it is unusual or fast; 4. verdict (Stage 4 decision), approval status (Stage 4b) and novelty, with one line on why;
  5. reproduction status per application; 6. links to the application articles; 7. the skill it feeds.
- **One application article** per application, `docs/articles/<method>-app<n>.html`, in this order:
  1. question; 2. data used (named sources, sample size and period; aggregates only, never rows);
  3. what we ran (script path, settings); 4. figures and tables; 5. original vs reproduced numbers;
  6. robustness (seeds, windows, null, baseline); 7. limitations; 8. takeaway; 9. link back to the method article.
- **Manifest** `docs/articles.json`: one entry per article with
  `slug, title, type (method|application), method, date, status, novelty, tags, links {self, parent, children, code, results}`.
  `status`: `recommended, awaiting approval` | `promoted` (only with APPROVAL.md) | `rejected`.
  `novelty`: `well-known` | `niche` | `obscure`. The scout's goal is diamonds in the rough, so on the front page the lead story is
  the most novel method article, and well-known methods sort after the niche and obscure ones.
  Article bodies are HTML fragments in `docs/content/<slug>.html`; the daily scout and future methods add articles by
  appending manifest entries, writing the fragments and running `python docs/build.py` (CI fails if the built pages are stale).
- **Daily scout cards** (`type: scout`): a short card per scouted method that links out to its research-lab scout page
  (`links.self` = `https://jgridifier.github.io/research-lab/methods-scout/<date>.html#m<n>`, no fragment, no children).
  Status is always `scouted, not in workflow`; the verdict is the scout's recommendation only. A scout card never enters the
  promote workflow or changes any skill. That happens only when Jared picks the method (Stage 1) and later approves it (APPROVAL.md).
