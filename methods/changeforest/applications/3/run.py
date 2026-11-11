"""changeforest application 3 (new in this repo; not in the scout) -- breaks in the joint monthly
distribution of credit-spread changes: GZ spread, excess bond premium, log VIX and the 10y yield,
1990-2026. 'Original' = first run in the scout venv; 'reproduction' = clean venv from the lockfile.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib import *
import ruptures as rpt
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
res = {}
M = pd.read_csv(WORK / "monthly_panel.csv", parse_dates=["date"]).set_index("date")
X = pd.DataFrame({"dGZ": M.gz_spread.diff(), "dEBP": M.ebp.diff(), "dlogVIX": np.log(M.VIXCLS).diff(), "dDGS10": M.DGS10.diff()}).dropna()
Z = zscore(X); dates = X.index
r, t = cf(Z); cps = r.split_points()
res["C1_n"] = len(Z); res["C1_period"] = [str(dates[0].date()), str(dates[-1].date())]; res["C1_secs"] = t
res["C1_cps"] = [str(dates[i].date()) for i in cps]
b = [0] + cps + [len(Z)]
res["C1_segments"] = [dict(start=str(dates[a].date()), end=str(dates[c - 1].date()), months=c - a,
    **{("sd_" + k): round(float(X.iloc[a:c][k].std()), 3) for k in X.columns},
    corr_dGZ_dlogVIX=round(float(X.iloc[a:c][["dGZ", "dlogVIX"]].corr().iloc[0, 1]), 2),
    GZ_level=round(float(M.loc[dates[a]:dates[c - 1], "gz_spread"].mean()), 2)) for a, c in zip(b[:-1], b[1:])]
res["C2_cim_cps"] = [str(dates[i].date()) for i in cf(Z, "change_in_mean")[0].split_points()]
res["C2_knn_cps"] = [str(dates[i].date()) for i in cf(Z, "knn")[0].split_points()]
runs, m, stable = seed_stable(Z, cps, tol=3)
res["C2_seed_ncp"] = [len(s) for s in runs]; res["C2_seed_reproduce"] = {str(dates[c].date()): round(x, 2) for c, x in zip(cps, m)}
res["C2_seed_stable_cps_8of10"] = [str(dates[c].date()) for c in stable]
K = max(len(cps), 1); rb = rpt.Binseg(model="rbf").fit(Z).predict(n_bkps=K)[:-1]
res["C2_rf_vs_binseg_rbf_match"] = round(float(np.mean(match(cps, [rb], 3))), 2) if cps else None
rng = np.random.default_rng(1)
res["C2_shuffled_ncp"] = [len(cf(Z[rng.permutation(len(Z))])[0].split_points()) for _ in range(10)]
res["C2_var1_null"] = var1_null(Z, reps=10)
dump(__file__, res)
fig, ax = plt.subplots(2, 1, figsize=(12, 5), sharex=True)
ax[0].plot(M.index, M.gz_spread, lw=.8, color="#1f2937"); ax[0].set_ylabel("GZ spread", fontsize=9)
ax[1].plot(X.index, X.dGZ.rolling(12).std(), lw=.8, color="#1f2937"); ax[1].set_ylabel("12m sd of dGZ", fontsize=9)
for a in ax:
    for i in cps: a.axvline(dates[i], color="#e11d48", lw=1.6 if i in stable else .6)
ax[0].set_title("changeforest on monthly credit-spread changes (bold = recur in >=8/10 seeds)", fontsize=10)
plt.tight_layout(); plt.savefig(fig_path(__file__, "changeforest_app3_credit.png"), dpi=110); plt.close()
