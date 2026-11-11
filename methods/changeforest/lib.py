"""Shared helpers for the changeforest applications."""
import json, os, pathlib, time
import numpy as np, pandas as pd
from changeforest import changeforest, Control

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORK = pathlib.Path(os.environ.get("AS_WORK_DIR", ROOT / ".work" / "panels"))
FIG = pathlib.Path(os.environ.get("AS_FIG_DIR", "")) if os.environ.get("AS_FIG_DIR") else None


def out_dir(here):
    o = pathlib.Path(here).resolve().parent / os.environ.get("AS_OUT_NAME", "out"); o.mkdir(exist_ok=True); return o


def fig_path(here, name):
    d = FIG or out_dir(here); d.mkdir(parents=True, exist_ok=True); return d / name


def cf(Z, method="random_forest", ctl=None):
    t = time.perf_counter()
    r = changeforest(Z, method, "bs", ctl) if ctl else changeforest(Z, method, "bs")
    return r, time.perf_counter() - t


def zscore(X):
    return ((X - X.mean()) / X.std()).values


def match(ref, others, tol):
    """For each break in ref: share of `others` runs with a break within +-tol rows."""
    return [float(np.mean([any(abs(c - o) <= tol for o in oc) for oc in others])) for c in ref]


def seed_stable(Z, cps, seeds=range(10), tol=13, keep=0.8):
    runs = [cf(Z, "random_forest", Control(seed=s))[0].split_points() for s in seeds]
    m = match(cps, runs, tol)
    return runs, m, [c for c, x in zip(cps, m) if x >= keep]


def var1_null(Z, reps=5, seed=7):
    """Stationary VAR(1) null with constant Gaussian innovations fitted to Z: autocorrelated, no breaks."""
    rng = np.random.default_rng(seed); Y, X = Z[1:], Z[:-1]
    A = np.linalg.lstsq(X, Y, rcond=None)[0]; E = Y - X @ A; S = np.cov(E.T); L = np.linalg.cholesky(S)
    rho = float(np.max(np.abs(np.linalg.eigvals(A)))); out = []
    for _ in range(reps):
        z = np.zeros_like(Z); z[0] = Z[0]
        eps = rng.standard_normal(Z.shape) @ L.T
        for t in range(1, len(Z)): z[t] = z[t - 1] @ A + eps[t]
        out.append(len(cf(z)[0].split_points()))
    return {"spectral_radius": round(rho, 4), "ncp": out}


def dump(here, res):
    import changeforest as cfm, ruptures, sklearn
    res["versions"] = {"changeforest": getattr(cfm, "__version__", "1.2.1"), "ruptures": ruptures.__version__,
                       "sklearn": sklearn.__version__, "numpy": np.__version__, "pandas": pd.__version__}
    p = out_dir(here) / "results.json"
    json.dump(res, open(p, "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else int(o))
    print("wrote", p)
