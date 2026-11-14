# DenseLines — results and decision

**Status: PROMOTED** (Jared, 2026-11-13, 11:51 PM ET; see [APPROVAL.md](APPROVAL.md)).

The formal Stage 2–3 pipeline (three distinct applications on the analysis-skills real panels, clean-environment reproduction) has **not** been run. Promotion is from the 2026-11-13 methods-scout run that Jared approved from, plus a `--synthetic` self-test of the NumPy port. That limitation is in force until a later Stage 2–3 pass is added.

Original aggregates: `original/scout_aggregates.json` and `original/parity_aggregates.json`. Scout data were SYNTHETIC mock ZBB budgets, not real firm budgets.

## Scout evidence (2026-11-13)

### Parity with the authors' Rust reference (github.com/domoritz/line-density-rust @ 083890c)

On the reference's own sine + N(0, 12) generator, width 400 × height 300:

| n series | same nonzero pixels | max abs diff | max rel diff | column sums = n |
|---|---|---:|---:|---|
| 100 | yes | 8.63e-07 | 1.79e-07 | yes |
| 1,000 | yes | 6.67e-06 | 1.92e-07 | yes |
| 5,000 | yes | 3.35e-05 | 2.1e-07 | yes |

The NumPy port matches the Rust reference (max relative difference 2.1e-7) and is 10–120× slower. The 50,000-series speed step was killed by a 15.6 GB memory limit and was never finished; that is recorded in the parity file, which was transcribed from the run log.

### Gap behaviour

The reference returns NaN in every column once any series starts or stops (100 of 400 columns in the constructed case of 50 series, 10 of them stopping at column 300; the default port path matches). `gap_safe=True` leaves those columns finite, and the column sum after the stop is 40, equal to the number of series still running. **Use `gap_safe=True` for panels with staggered start or end dates.**

### Reading many short budget paths

On the Corning mock (1,052 series), a residual brush plus a text keyword recovered 94% of the planted AI-demand group (`brush_or_text` recall 0.937, precision 0.561). The same idea is weaker and less precise on the Morgan Stanley mock clusters. A bandwidth/smoothing sweep (`m2b_brush_sensitivity.json`) showed the brush is fragile: some smooth widths miss the branch entirely. Density ink slightly down-weights the noisiest decile relative to an unnormalised overlay, but the total-variation distance to the hidden true density barely moves.

## Validation this turn

- **`--synthetic` self-test** (skill script): replay the scout's gap case and the column-sum invariant with the same generator and seed (20261113). Asserts default-path NaN columns = 100, `gap_safe` NaN columns = 0, and `gap_safe` column-sum after column 300 = 40. Also checks that a full-span bundle has column sums equal to the number of series.
- **Not re-run this turn:** pixel-level parity against the Rust reference (would require building that reference; skipped under the "no heavy installs or builds" cap). The stored parity aggregates are the original record.

## Mandatory checks the skill carries

- For series that do not all span the same x-range, set `gap_safe=True`; the reference (and the default port path) will otherwise poison whole columns with NaN.
- A residual brush is a hint, not a finding: vary the smooth width and report whether the branch survives.
- Combine a brush with an independent keyword or label when one is available; neither is enough on its own in the scout.
- The port is the supported implementation here. The Rust reference remains the accuracy check, not the skill's runtime.

## Stage 4 decision

Recommend promotion of DenseLines for **visualising and interactively brushing many overlapping short series**. Do not treat a single brush as a discovered cluster without a sensitivity check. A later three-application pass is still worth doing; it was not a condition of this approval.
