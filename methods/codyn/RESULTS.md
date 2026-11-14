# codyn — results and decision

**Status: PROMOTED** (Jared, 2026-11-13, 11:51 PM ET; see [APPROVAL.md](APPROVAL.md)). The approval names rank clocks; variance-ratio, synchrony and rate-of-change from the same scout are kept in the skill.

The formal Stage 2–3 pipeline (three distinct applications on the analysis-skills real panels, clean-environment reproduction) has **not** been run. Promotion is from the 2026-11-12 ad hoc methods-scout run that Jared approved from, plus a `--synthetic` self-test in the skill script. That limitation is in force until a later Stage 2–3 pass is added.

Original aggregates: `original/scout_aggregates.json` (no raw amounts and no period-by-period share series). Scout data were a public FR Y-9C *proxy* panel, used descriptively. Package: codyn 2.0.6, R 4.5.3, seed 20261112, 999 cyclic-shift draws.

## Scout evidence (2026-11-12 ad hoc)

Panel A: trading assets of 14 dealer holding companies, 2016Q3–2026Q2 (40 quarters). Panel E4: trailing-four-quarter equity trading revenue of four dealers, 2011Q1–2026Q2 (62 quarters).

| quantity | Panel A (14 dealers, raw amounts unless noted) | Panel E4 (4 dealers, raw amounts unless noted) |
|---|---|---|
| Variance ratio (VR) | 4.45; cyclic-shift null 0.44–2.00 | 2.36; null 0.57–1.66 |
| VR on shares | ~0 (degenerate: shares sum to 1) | ~0 (same degeneracy) |
| Loreau / Gross synchrony | 0.76 / 0.50 | 0.78 / 0.76 |
| Mean rank shift (on shares) | 0.385; null p(≥ obs) = 0.896 | 0.238; null p(≤ obs) = 0.002 |
| Rate of compositional change (on shares) | 0.00138; null p(≥ obs) = 0.001 | 0.00473; null p(≥ obs) = 0.001 |
| Turnover (appearance / disappearance) | 0 / 0 (closed balanced panel) | 0 / 0 |

Leave-outs on panel A: dropping the foreign dealers leaves VR at 4.43; foreign-only VR is 0.73, inside that group's null (0.29–2.19). So US dealer raw volumes co-move; foreign IHC volumes do not. Composition walks in one direction (rate of change p = 0.001). Rank clocks / mean rank shift on panel A are not unusual under a cyclic-shift null; on panel E4, ranks are *more* stable than the null (p = 0.002).

Windows and leave-outs are in the aggregate file. All of this is descriptive. It is not a forecast, and it is not part of the pre-registered Y-9C trading-OT study.

## Validation this turn

- **Stored aggregates** match the published teaching-page figures (VR 4.45 vs null 0.44–2.00 on panel A; foreign-only 0.73 inside its null; rate-of-change p = 0.001).
- **`--synthetic` self-test** (skill script): two small constructed communities (a shared-factor co-moving set and an independent set), fixed seed, checks that VR is above 1 and above a short cyclic-shift null on the co-moving set, and not on the independent set; and that a designed two-way rank swap is recovered by `rank_shift`. This does not re-fit the Y-9C proxy panel.
- **Not re-run this turn:** the original scout script with 999 cyclic shifts on the proxy panel (minutes, and the panel is not in this repo).

## Mandatory checks the skill carries

- Use **raw amounts** for variance-ratio and synchrony. VR on shares of a closed composition is degenerate (the total has variance zero).
- Use **shares** for rank shift, rank clocks, and rate of compositional change.
- Always run a **cyclic-shift null** (Hallett et al. 2014), which keeps each series' autocorrelation. An iid shuffle is not enough.
- On a closed balanced panel, appearance/disappearance turnover is identically zero; do not report that as a finding.
- Report leave-outs (a subset that may not co-move can be hidden in the aggregate VR).

## Stage 4 decision

Recommend promotion of codyn for **describing co-movement and rank rearrangement in a closed group of units over time**, with the cyclic-shift null and the raw-vs-shares split above. A later three-application pass is still worth doing; it was not a condition of this approval.
