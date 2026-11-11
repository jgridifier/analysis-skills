# Examples

```bash
# cross-section: which county traits mark the biggest unemployment shock?
Rscript scripts/regime_tree.R --csv counties.csv --formula "shock ~ unemp_pre + gdp_growth + rucc + bach + log_lf" --alpha 0.01 --minbucket 50

# MOB: does the slope of y on x depend on state z?
Rscript scripts/regime_tree.R --csv monthly.csv --mode mob --formula "dGZ ~ dVIX + dDGS10 | NFCI + T10Y2Y + DGS2" --time-col date --minbucket 36 --alpha 0.01

# time series, forecasting check with a 6-month horizon gap
Rscript scripts/regime_tree.R --csv monthly.csv --formula "y_fwd6 ~ VIXCLS + NFCI + T10Y2Y" --time-col date --gap 6

Rscript scripts/regime_tree.R --synthetic
```
Full worked applications: `methods/partykit/applications/{1,2,3}` and the newsroom articles on the Pages site.
