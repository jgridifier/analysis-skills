"""changeforest application 1 -- regimes in the joint distribution of weekly changes in six
rates/stress series (log VIX, 10y-2y, 2y, 30y mortgage, NFCI, STLFSI4), 1994-2026.
Ported from the scout's m2_changeforest.py (levels run, kept as the pre-processing check) and
m2b.py (changes run + robustness). Timing fields are reported but never compared.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from lib import *
import ruptures as rpt
from sklearn.cluster import KMeans
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
res = {}
W = pd.read_csv(WORK / "weekly_panel.csv", parse_dates=["date"]).set_index("date")
cols = ["VIXCLS", "T10Y2Y", "DGS2", "MORTGAGE30US", "NFCI", "STLFSI4"]
# --- pre-processing check: the same detector on LEVELS (scout's first, flawed run) ---
XL = W[cols].copy(); XL["VIXCLS"] = np.log(XL["VIXCLS"]); ZL = zscore(XL)
rl, _ = cf(ZL); lev = rl.split_points(); gaps = np.diff(lev)
res["B0_levels_artifact"] = {"n_cps": len(lev), "median_gap_weeks": float(np.median(gaps)), "min_gap_weeks": float(gaps.min()), "max_gap_weeks": float(gaps.max())}
res["R_levels_var1_null"] = var1_null(ZL, reps=3)
# --- main run on weekly CHANGES ---
X = XL.diff().dropna(); X.columns = ["dlogVIX", "dT10Y2Y", "dDGS2", "dMORT", "dNFCI", "dSTLFSI4"]
Z = zscore(X); dates = X.index
r, t = cf(Z); cps = r.split_points()
res["B1_n"] = len(Z); res["B1_period"] = [str(dates[0].date()), str(dates[-1].date())]; res["B1_rf_secs"] = t
res["B1_rf_cps"] = [str(dates[i].date()) for i in cps]
b = [0] + cps + [len(Z)]
res["B1_segments"] = [dict(start=str(dates[a].date()), end=str(dates[c - 1].date()), weeks=c - a,
    **{("sd_" + k): round(float(X.iloc[a:c][k].std()), 3) for k in X.columns},
    NFCI_level=round(float(W.loc[dates[a]:dates[c - 1], "NFCI"].mean()), 2), VIX_level=round(float(W.loc[dates[a]:dates[c - 1], "VIXCLS"].mean()), 1),
    corr_dVIX_dDGS2=round(float(X.iloc[a:c][["dlogVIX", "dDGS2"]].corr().iloc[0, 1]), 2)) for a, c in zip(b[:-1], b[1:])]
rk, tk = cf(Z, "knn"); rm, tm = cf(Z, "change_in_mean")
res["B2_knn_cps"] = [str(dates[i].date()) for i in rk.split_points()]; res["B2_cim_cps"] = [str(dates[i].date()) for i in rm.split_points()]
runs, m, stable = seed_stable(Z, cps)
res["B2_seed_reproduce"] = {str(dates[c].date()): round(x, 2) for c, x in zip(cps, m)}; res["B2_seed_ncp"] = [len(s) for s in runs]
res["R_seed_stable_cps_8of10"] = [str(dates[c].date()) for c in stable]
drop = {cn: cf(np.delete(Z, j, axis=1))[0].split_points() for j, cn in enumerate(X.columns)}
res["B2_dropone_match"] = {str(dates[c].date()): round(x, 2) for c, x in zip(cps, match(cps, list(drop.values()), 13))}
res["B2_dropone_ncp"] = {k: len(v) for k, v in drop.items()}
cut = int(.7 * len(Z)); sub = cf(Z[:cut])[0].split_points(); ref_in = [c for c in cps if c < cut - 26]
res["B2_first70_ncp"] = len(sub); res["B2_first70_match"] = round(float(np.mean(match(ref_in, [sub], 13))), 2)
K = max(len(cps), 1)
rb = rpt.Binseg(model="rbf").fit(Z).predict(n_bkps=K)[:-1]; bl = rpt.Binseg(model="l2").fit(Z).predict(n_bkps=K)[:-1]
res["B2_rf_vs_binseg_rbf_match"] = round(float(np.mean(match(cps, [rb], 13))), 2); res["B2_rf_vs_binseg_l2_match"] = round(float(np.mean(match(cps, [bl], 13))), 2)
km = KMeans(n_clusters=K + 1, n_init=10, random_state=0).fit(Z).labels_
res["B2_kmeans_label_switches"] = int((np.diff(km) != 0).sum()); res["B2_cf_switches"] = len(cps)
rng = np.random.default_rng(1)
res["B2_shuffled_weekly_ncp"] = [len(cf(Z[rng.permutation(len(Z))])[0].split_points()) for _ in range(5)]
res["R_changes_var1_null"] = var1_null(Z, reps=5)
# remedy for the failed VAR(1) null: prewhiten with a VAR(1) fitted on the full sample, rerun on residuals
A = np.linalg.lstsq(Z[:-1], Z[1:], rcond=None)[0]; Ez = Z[1:] - Z[:-1] @ A; Ez = (Ez - Ez.mean(0)) / Ez.std(0)
rp, _ = cf(Ez); pw = rp.split_points(); pruns, pm, pstable = seed_stable(Ez, pw)
res["R_prewhitened"] = {"ncp": len(pw), "cps": [str(dates[i + 1].date()) for i in pw],
    "seed_ncp": [len(s) for s in pruns], "stable_8of10": [str(dates[i + 1].date()) for i in pstable],
    "var1_null": var1_null(Ez, reps=5), "shuffled_ncp": [len(cf(Ez[np.random.default_rng(2).permutation(len(Ez))])[0].split_points())]}
dump(__file__, res)
fig, ax = plt.subplots(3, 1, figsize=(12, 7), sharex=True)
for a, (c, lab) in zip(ax, [("VIXCLS", "VIX (weekly avg)"), ("NFCI", "NFCI"), ("DGS2", "2y yield")]):
    a.plot(W.index, W[c], lw=.8, color="#1f2937"); a.set_ylabel(lab, fontsize=9)
    for i in cps: a.axvline(dates[i], color="#e11d48", lw=1.6 if i in stable else .6, alpha=1 if i in stable else .5)
ax[0].set_title("changeforest on weekly changes of 6 series: breaks (bold = recur in >=8/10 seeds)", fontsize=10)
plt.tight_layout(); plt.savefig(fig_path(__file__, "changeforest_app1_weekly.png"), dpi=110); plt.close()
fig, ax = plt.subplots(figsize=(12, 2.6)); ax.plot(W.index, W.VIXCLS, lw=.7, color="#1f2937")
for i in lev: ax.axvline(W.index[i], color="#f59e0b", lw=.8)
ax.set_title(f"Failure mode: on persistent LEVELS changeforest returns {len(lev)} breaks ~{np.median(gaps):.0f} weeks apart", fontsize=10)
plt.tight_layout(); plt.savefig(fig_path(__file__, "changeforest_app1_levels_artifact.png"), dpi=110); plt.close()
