# DenseLines — density line charts

- **Citation:** Moritz, D. & Fisher, D. (2018). "DenseLines: Efficient Many-To-One Context Preservation in Line Chart Visualizations." arXiv:1808.06019.
- **Package:** authors' Rust reference at github.com/domoritz/line-density-rust @ 083890c; NumPy port in this repo (`skills/run-line-density-chart/scripts/line_density.py`), checked against that reference on the scout (max relative difference 2.1e-7). The port is transparent and has no neural nets.
- **Question type:** how do you see the typical shape, and the unusual branches, in a plot of hundreds or thousands of overlapping short series?
- **Scout run:** research-lab `docs/methods-scout/runs/2026-11-13/m2_denselines.py`, `denselines.py`, `m2a_parity.py`, `m2b_brush_sensitivity.py`, on SYNTHETIC mock zero-based-budgeting data (not real budgets). Teaching page: https://jgridifier.github.io/research-lab/methods-scout/2026-11-13.html#m2
- **Approval:** [APPROVAL.md](APPROVAL.md) (Jared, 2026-11-13, 11:51 PM ET).
- **Status:** see [RESULTS.md](RESULTS.md). Skill: [`run-line-density-chart`](../../skills/run-line-density-chart/SKILL.md).
