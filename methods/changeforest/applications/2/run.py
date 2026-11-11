"""changeforest application 2 -- volatility/correlation regimes in DAILY changes of log VIX,
10y-2y, 2y and 10y yields (n ~ 9.2k), plus a fit-time scaling benchmark on synthetic data.
Ported from the scout's m2_changeforest.py (B3) and m2b.py (daily shuffled null).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib import *
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
res = {}
Dd = pd.read_csv(WORK / "daily_panel.csv", parse_dates=["date"]).set_index("date")
DX = pd.DataFrame({"dlogVIX": np.log(Dd.VIXCLS).diff(), "dT10Y2Y": Dd.T10Y2Y.diff(), "dDGS2": Dd.DGS2.diff(), "dDGS10": Dd.DGS10.diff()}).dropna()
DX = DX[(DX.abs() < DX.abs().quantile(0.9999)).all(axis=1)]; DZ = zscore(DX); dd = DX.index
r, t = cf(DZ); dcps = r.split_points()
res["B3_n"] = len(DZ); res["B3_rf_secs"] = t; res["B3_cps"] = [str(dd[i].date()) for i in dcps]
b = [0] + list(dcps) + [len(DZ)]
res["B3_segments"] = [dict(start=str(dd[a].date()), end=str(dd[c - 1].date()), days=c - a,
    **{("sd_" + k): round(float(DX.iloc[a:c][k].std()), 4) for k in DX.columns},
    corr_dVIX_dDGS10=round(float(DX.iloc[a:c][["dlogVIX", "dDGS10"]].corr().iloc[0, 1]), 3)) for a, c in zip(b[:-1], b[1:])]
res["B3_cim_ncp"] = len(cf(DZ, "change_in_mean")[0].split_points())
# daily shuffled null: the scout drew 5 weekly-length permutations from rng(1) first; replay them
rng = np.random.default_rng(1); [rng.permutation(1709) for _ in range(5)]
res["B3_shuffled_daily_ncp"] = [len(cf(DZ[rng.permutation(len(DZ))])[0].split_points()) for _ in range(3)]
# new robustness: seeds (tolerance 63 trading days ~ one quarter), VAR(1) null
runs, m, stable = seed_stable(DZ, dcps, tol=63)
res["R_seed_ncp"] = [len(s) for s in runs]; res["R_seed_reproduce"] = {str(dd[c].date()): round(x, 2) for c, x in zip(dcps, m)}
res["R_seed_stable_cps_8of10"] = [str(dd[c].date()) for c in stable]
res["R_var1_null"] = var1_null(DZ, reps=3)
# scaling benchmark (synthetic; timings are environment-dependent and never compared)
rs = np.random.default_rng(0); sc = []
for n in [1000, 2000, 4000, 8000, 16000]:
    Xs = np.concatenate([rs.normal(0, 1, (n // 2, 5)), rs.normal(0, 1.6, (n - n // 2, 5))])
    rr, tt = cf(Xs); sc.append({"n": n, "random_forest": round(tt, 3), "random_forest_cps": rr.split_points()})
res["B3_scaling"] = sc
dump(__file__, res)
fig, ax = plt.subplots(figsize=(12, 3.2)); ax.plot(dd, DX.dDGS10.rolling(63).std(), lw=.8, color="#1f2937", label="63d sd of daily change in 10y")
for i in dcps: ax.axvline(dd[i], color="#e11d48", lw=1.4 if dd[i] in [dd[c] for c in stable] else .5)
ax.legend(fontsize=8); ax.set_title("Daily changes panel: changeforest breaks (bold = recur in >=8/10 seeds)", fontsize=10)
plt.tight_layout(); plt.savefig(fig_path(__file__, "changeforest_app2_daily.png"), dpi=110); plt.close()
