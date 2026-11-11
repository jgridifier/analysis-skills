#!/usr/bin/env python3
"""General change-point analysis with the protocol from run-changepoint-analysis/SKILL.md.

  python changepoint.py --csv panel.csv --date-col date --cols A,B,C --transform diff \
      [--log-cols A] [--prewhiten auto|yes|no] [--seeds 10] [--tol 13] [--out report.json]
  python changepoint.py --synthetic            # self-test on simulated data (used by CI)

Steps: transform (levels -> changes) -> standardize -> persistence check (VAR(1) spectral radius)
-> optional VAR(1) prewhitening -> changeforest random_forest (binary segmentation) -> seed stability
(keep breaks recurring in >= 80% of seeds) -> nulls (iid shuffle + stationary VAR(1) simulation)
-> baseline (change_in_mean) -> per-segment sd / correlation summary. Writes JSON; prints a short report.
"""
import argparse, json, sys
import numpy as np, pandas as pd
from changeforest import changeforest, Control


def cps_of(Z, method="random_forest", seed=None):
    r = changeforest(Z, method, "bs", Control(seed=seed)) if seed is not None else changeforest(Z, method, "bs")
    return list(r.split_points())


def var1(Z):
    A = np.linalg.lstsq(Z[:-1], Z[1:], rcond=None)[0]; E = Z[1:] - Z[:-1] @ A
    return A, E, float(np.max(np.abs(np.linalg.eigvals(A))))


def var1_sims(Z, reps, seed=7):
    A, E, rho = var1(Z); L = np.linalg.cholesky(np.cov(E.T) + 1e-12 * np.eye(Z.shape[1])); rng = np.random.default_rng(seed); out = []
    for _ in range(reps):
        z = np.zeros_like(Z); z[0] = Z[0]; eps = rng.standard_normal(Z.shape) @ L.T
        for t in range(1, len(Z)): z[t] = z[t - 1] @ A + eps[t]
        out.append(len(cps_of(z)))
    return rho, out


def recur(ref, runs, tol):
    return [float(np.mean([any(abs(c - o) <= tol for o in r) for r in runs])) for c in ref]


def analyse(X, seeds=10, tol=13, prewhiten="auto", null_reps=5, keep=0.8, rho_max=0.8):
    X = X.dropna()
    if isinstance(X.index, pd.DatetimeIndex): X.index = X.index.strftime("%Y-%m-%d")
    Z = ((X - X.mean()) / X.std()).values; idx = X.index
    _, _, rho = var1(Z); res = {"n": len(Z), "dims": list(X.columns), "persistence_spectral_radius": round(rho, 4)}
    pw = prewhiten == "yes" or (prewhiten == "auto" and rho > rho_max)
    if pw:
        A, E, _ = var1(Z); Z = (E - E.mean(0)) / E.std(0); idx = idx[1:]
        res["prewhitened"] = True; res["persistence_after_prewhitening"] = round(var1(Z)[2], 4)
    else:
        res["prewhitened"] = False
    cps = cps_of(Z); runs = [cps_of(Z, seed=s) for s in range(seeds)]; rr = recur(cps, runs, tol)
    stable = [c for c, x in zip(cps, rr) if x >= keep]
    rng = np.random.default_rng(1)
    shuffled = [len(cps_of(Z[rng.permutation(len(Z))])) for _ in range(null_reps)]
    rho_n, var_null = var1_sims(Z, null_reps)
    cim = cps_of(Z, "change_in_mean")
    b = [0] + stable + [len(Z)]; Xs = X.loc[idx]
    segs = []
    for a, c in zip(b[:-1], b[1:]):
        seg = Xs.iloc[a:c]; cm = seg.corr().values; iu = np.triu_indices(len(X.columns), 1)
        segs.append({"start": str(idx[a]), "end": str(idx[c - 1]), "n": c - a,
                     "sd": {k: round(float(v), 4) for k, v in seg.std().items()},
                     "mean_abs_corr": round(float(np.nanmean(np.abs(cm[iu]))), 3) if len(X.columns) > 1 else None})
    res.update({"breaks_default_seed": [str(idx[c]) for c in cps], "n_breaks_by_seed": [len(r) for r in runs],
                "break_recurrence": {str(idx[c]): round(x, 2) for c, x in zip(cps, rr)},
                "stable_breaks": [str(idx[c]) for c in stable], "null_iid_shuffle_n_breaks": shuffled,
                "null_var1_n_breaks": var_null, "null_var1_spectral_radius": round(rho_n, 4),
                "baseline_change_in_mean_n_breaks": len(cim), "segments_on_stable_breaks": segs})
    null_ok = max(var_null) <= max(1, 0.2 * len(stable)) and max(shuffled) == 0
    res["verdict"] = ("no stable breaks" if not stable else
                      "breaks distinguishable from the stationary null" if null_ok else
                      "NOT distinguishable from a stationary autocorrelated null: do not report these as regimes")
    return res


def synthetic():
    rng = np.random.default_rng(0); n = 1200
    X = np.concatenate([rng.normal(0, 1, (400, 3)), rng.normal(0, 2.0, (400, 3)), rng.multivariate_normal([0, 0, 0], [[1, .8, .8], [.8, 1, .8], [.8, .8, 1]], 400)])
    df = pd.DataFrame(X, columns=["a", "b", "c"], index=pd.RangeIndex(n))
    r = analyse(df, seeds=5, tol=20, null_reps=3)
    st = [int(s) for s in r["stable_breaks"]]
    assert any(abs(s - 400) <= 20 for s in st), r; assert any(abs(s - 800) <= 20 for s in st), r
    assert max(r["null_iid_shuffle_n_breaks"]) == 0, r
    print("synthetic OK:", r["stable_breaks"], r["verdict"]); return r


def main():
    p = argparse.ArgumentParser(); p.add_argument("--csv"); p.add_argument("--date-col", default="date"); p.add_argument("--cols")
    p.add_argument("--transform", choices=["diff", "none"], default="diff"); p.add_argument("--log-cols", default="")
    p.add_argument("--prewhiten", choices=["auto", "yes", "no"], default="auto"); p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--tol", type=int, default=13); p.add_argument("--null-reps", type=int, default=5)
    p.add_argument("--out"); p.add_argument("--synthetic", action="store_true"); a = p.parse_args()
    if a.synthetic: synthetic(); return
    df = pd.read_csv(a.csv, parse_dates=[a.date_col]).set_index(a.date_col)
    X = df[a.cols.split(",")].astype(float)
    for c in filter(None, a.log_cols.split(",")): X[c] = np.log(X[c])
    if a.transform == "diff": X = X.diff()
    else: print("warning: running on levels; persistent levels produce spurious, evenly spaced breaks", file=sys.stderr)
    r = analyse(X, a.seeds, a.tol, a.prewhiten, a.null_reps)
    if a.out: json.dump(r, open(a.out, "w"), indent=1)
    print(json.dumps({k: r[k] for k in ["n", "persistence_spectral_radius", "prewhitened", "n_breaks_by_seed", "stable_breaks",
                                         "null_iid_shuffle_n_breaks", "null_var1_n_breaks", "baseline_change_in_mean_n_breaks", "verdict"]}, indent=1))


if __name__ == "__main__":
    main()
