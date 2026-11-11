# Evidence behind this skill

From `methods/changeforest/RESULTS.md` (workflow run 2026-11-10; all three applications reproduced exactly in a clean environment):

| application | n | breaks (stable ≥8/10) | iid null | VAR(1) null | change-in-mean | gate result |
|---|---|---|---|---|---|---|
| weekly changes, 6 rate/stress series | 1,709 | 35 (28) | 0 ×5 | **20–37** (radius 0.957) | 0 | null failed → prewhitened: 22 (12), VAR null 0–2 |
| weekly LEVELS (pre-processing check) | 1,710 | 63 | — | 64–71 (radius 0.997) | — | artifact |
| daily changes, 4 series | 9,174 | 28 (23) | 0 ×3 | 0 ×3 (radius 0.50) | 0 | pass |
| monthly credit-spread changes, 4 series | 440 | 2 (2): 1998-08, 2012-07 | 0 ×10 | 0 ×10 (radius 0.42) | 0 | pass |

Monthly credit example: sd of ΔGZ 0.069 → 0.331 → 0.205 and corr(ΔGZ, Δlog VIX) −0.02 → 0.70 → 0.68 across the three segments.
