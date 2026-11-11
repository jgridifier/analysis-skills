# Evidence behind this skill

From `methods/partykit/RESULTS.md` (workflow run 2026-11-10; trees reproduced exactly in a clean environment):

| application | shape | n | result | null | baseline | gates |
|---|---|---|---|---|---|---|
| credit-spread regimes (ctree) | monthly time series | 423 | root VIX ≤ 31.9; 4 leaves; root = VIX in 68% of block bootstraps | iid 3%, **circular shift 60%** | **lost to hist mean OOS** (R² −0.31) | reproduce ✓ null ✗ baseline ✗ |
| VIX→spread sensitivity (MOB) | monthly time series | 440 | split NFCI ≤ 0.057; ΔVIX slope 0.029 vs 0.059 | **shift of state vars 53%** | BIC −513.6 vs pooled −350.5, dummy-OLS −418.5 | reproduce ✓ null ✗ baseline ✓ |
| county unemployment-shock subgroups (ctree) | cross-section | 3,074 | GR root unemp 2007 ≤ 4.3 (7 leaves); COVID root labor force ≈14.6k (8 leaves) | iid 0% / 4% | CV R² ≈ CART, within 0.035 of OLS | all ✓ |
