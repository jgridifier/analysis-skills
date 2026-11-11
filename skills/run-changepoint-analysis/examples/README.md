# Examples

```bash
# daily changes of four rate/vol series (low persistence: no prewhitening needed)
python scripts/changepoint.py --csv daily_panel.csv --cols VIXCLS,T10Y2Y,DGS2,DGS10 --log-cols VIXCLS --tol 63

# weekly averages: persistence is high, so --prewhiten auto will prewhiten
python scripts/changepoint.py --csv weekly_panel.csv --cols VIXCLS,T10Y2Y,DGS2,MORTGAGE30US,NFCI,STLFSI4 --log-cols VIXCLS --tol 13

# self-test on simulated data with breaks at rows 400 (variance) and 800 (correlation)
python scripts/changepoint.py --synthetic
```
Full worked applications with original-vs-reproduced numbers: `methods/changeforest/applications/{1,2,3}` and the
newsroom articles on the Pages site.
