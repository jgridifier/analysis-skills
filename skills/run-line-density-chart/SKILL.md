---
name: run-line-density-chart
description: Use when you need to see the typical shape, and the unusual branches, in a plot of hundreds or thousands of overlapping short series — e.g. "the spaghetti chart is unreadable", "is there a group of series that peel off from the main bundle?"
---

# Run a density line-chart analysis

Overlaying a thousand short series as raw lines hides both the typical path and the unusual ones. DenseLines (Moritz & Fisher 2018) rasters each series, normalises it by its own arc length (column sums), and adds the images, so ink reflects how many series pass through each pixel, not how wiggly the noisiest ones are.

Recommended method: **DenseLines**, NumPy port of the authors' Rust reference, approved 2026-11-13. Teaching page: https://jgridifier.github.io/research-lab/methods-scout/2026-11-13.html#m2. Approval: [`methods/denselines/APPROVAL.md`](../../methods/denselines/APPROVAL.md). Evidence: [`methods/denselines/RESULTS.md`](../../methods/denselines/RESULTS.md). Transparent; no neural nets.

The three-application reproduction pipeline has not been run on this repo's real panels; the evidence is the 2026-11-13 scout (SYNTHETIC mock budgets, plus a Rust-parity check) and the `--synthetic` self-test. Say so when you use this skill.

## 1. Pre-process (mandatory)

- Align series on a common x-scale (time, year, index). Map y-values to integer pixel rows with a stated range (the reference clamps and truncates).
- If series start or stop at different x, you **must** set `gap_safe=True`. The reference, and the port's default path, divide 0/0 and write NaN in every column that any series does not cover, which poisons the aggregate.
- Do not feed this a single long series; it is a many-series overlay.

## 2. Choose the method

| method | use when | don't use when |
|---|---|---|
| **DenseLines, `gap_safe=True`** — start here for real panels | many overlapping short series, possibly with staggered spans | you need a statistical cluster assignment; this is a view plus a brush, not a model |
| DenseLines, default (reference semantics) | parity checks against the Rust reference | staggered start/stop dates |
| Unnormalised overlay (baseline) | always compare; it over-represents wiggly series | as the only view |
| Residual brush + optional keyword | after you can see a branch in the density | treating one smooth width as a finding (the scout brush was bandwidth-fragile) |

## 3. Robustness protocol (report all of it)

- Report whether `gap_safe` was on, the canvas size, and the y-range used for pixel mapping.
- If you brush a branch, vary the smooth width and the columns you brush; report whether the branch survives (the scout missed some clusters at larger widths).
- When a text or label signal exists, report brush alone, keyword alone, and the union, with precision and recall against any labelled group.
- The NumPy port was within 2.1e-7 relative of the Rust reference on full-span bundles (n = 100, 1,000, 5,000) but is 10–120× slower. Do not expect the 50,000-series speed figure; that step ran out of memory on the scout and was never finished.

## 4. Interpret and report

- Bright ink is where many series go. A branch off the main ridge is a candidate group, not a cluster until a sensitivity check (and, if you have them, labels) agrees.
- Arc-length normalisation down-weights series that spend a lot of ink zigzagging.

Template: question; n series, x-span, canvas; `gap_safe`; what the density shows; brush / keyword results and sensitivity; limitations (including that Stage 2–3 has not been run on the real panels, and that Rust pixel-parity was not re-run at promotion).

## 5. Scripts

`scripts/line_density.py`

```bash
python skills/run-line-density-chart/scripts/line_density.py --synthetic
python skills/run-line-density-chart/scripts/line_density.py --csv series.csv --width 400 --height 300 --gap-safe --out density.json
```

`--synthetic` replays the scout's gap-case invariants (50 series, 10 stopping at column 300: default path has 100 NaN columns; `gap_safe` has 0 and a column-sum of 40 after the stop) and checks that a full-span bundle has column sums equal to the number of series. It does not rebuild the Rust reference.

## Citations

Moritz, D. & Fisher, D. (2018). "DenseLines: Efficient Many-To-One Context Preservation in Line Chart Visualizations." arXiv:1808.06019. Rust reference: github.com/domoritz/line-density-rust @ 083890c.
