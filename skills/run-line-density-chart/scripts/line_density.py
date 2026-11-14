#!/usr/bin/env python3
"""DenseLines density chart (Moritz & Fisher, arXiv:1808.06019).

NumPy port of the authors' Rust reference (github.com/domoritz/line-density-rust @083890c).
  python line_density.py --synthetic     # self-test (used by CI)
  python line_density.py --csv series.csv --width 400 --height 300 --out density.json
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

import numpy as np

# ---- port (research-lab docs/methods-scout/runs/2026-11-13/denselines.py) ----

def _bresenham(x0, y0, x1, y1):
    """Vectorised imageproc BresenhamLineIter over many segments. Inputs are float32 arrays.
    Returns (seg_index, px, py) int arrays for every emitted point."""
    x0 = x0.astype(np.float32); y0 = y0.astype(np.float32); x1 = x1.astype(np.float32); y1 = y1.astype(np.float32)
    steep = np.abs(y1 - y0) > np.abs(x1 - x0)
    X0 = np.where(steep, y0, x0); Y0 = np.where(steep, x0, y0); X1 = np.where(steep, y1, x1); Y1 = np.where(steep, x1, y1)
    sw = X0 > X1
    X0, X1 = np.where(sw, X1, X0), np.where(sw, X0, X1); Y0, Y1 = np.where(sw, Y1, Y0), np.where(sw, Y0, Y1)
    dx = (X1 - X0).astype(np.float32); dy = np.abs(Y1 - Y0).astype(np.float32)
    x = X0.astype(np.int64); y = Y0.astype(np.int64)
    err = (dx / np.float32(2)).astype(np.float32); endx = X1.astype(np.int64)
    ystep = np.where(Y0 < Y1, 1, -1).astype(np.int64)
    out_i, out_x, out_y = [], [], []
    idx = np.arange(len(x))
    while idx.size:
        live = x[idx] <= endx[idx]; idx = idx[live]
        if not idx.size: break
        st = steep[idx]
        out_i.append(idx); out_x.append(np.where(st, y[idx], x[idx])); out_y.append(np.where(st, x[idx], y[idx]))
        x[idx] += 1
        e = (err[idx] - dy[idx]).astype(np.float32)
        neg = e < 0
        y[idx] += np.where(neg, ystep[idx], 0)
        err[idx] = np.where(neg, (e + dx[idx]).astype(np.float32), e)
    return np.concatenate(out_i), np.concatenate(out_x), np.concatenate(out_y)


def density(series, width, height, xs=None, gap_safe=False, chunk=20000, weights=None, dtype=np.float64):
    """series: list/array of 1-D integer pixel arrays (y per vertex). Returns (height, width) density."""
    agg = np.zeros(width * height, dtype=dtype)
    nan_cols = np.zeros(width, bool)
    for c0 in range(0, len(series), chunk):
        S = series[c0:c0 + chunk]
        sx0, sy0, sx1, sy1, sid = [], [], [], [], []
        for j, s in enumerate(S):
            s = np.asarray(s, np.float32)
            if len(s) < 2: continue
            vx = np.arange(len(s), dtype=np.float32) if xs is None else np.asarray(xs[c0 + j], np.float32)
            sx0.append(vx[:-1]); sy0.append(s[:-1]); sx1.append(vx[1:]); sy1.append(s[1:]); sid.append(np.full(len(s) - 1, j))
        if not sid: continue
        sid = np.concatenate(sid)
        gi, px, py = _bresenham(np.concatenate(sx0), np.concatenate(sy0), np.concatenate(sx1), np.concatenate(sy1))
        ok = (px >= 0) & (px < width) & (py >= 0) & (py < height)
        ser = sid[gi[ok]]; px = px[ok]; py = py[ok]
        key = np.unique((ser * width + px) * height + py)
        sc = key // height; py = key % height; px = sc % width
        cnt = np.bincount(sc, minlength=len(S) * width)
        w = 1.0 / cnt[sc]
        if weights is not None: w = w * np.asarray(weights[c0:c0 + chunk])[sc // width]
        agg += np.bincount(py * width + px, weights=w, minlength=width * height)
        if not gap_safe:
            covered = cnt.reshape(len(S), width) > 0
            used = np.array([len(s) >= 2 for s in S])
            nan_cols |= (~covered[used]).any(0)
    D = agg.reshape(height, width)
    if not gap_safe and nan_cols.any(): D[:, nan_cols] = np.nan
    return D


def to_pixels(v, lo, hi, height):
    """Map values to integer rows the way the reference does (clamp, truncate to u32)."""
    p = (np.asarray(v, float) - lo) / (hi - lo) * height
    return np.clip(p, 0, height).astype(np.int64)


# ---- synthetic self-test: scout gap-case + column-sum invariants ----

def synthetic():
    """Replay the scout's gap-case generator (seed 20261113) and the full-span column-sum invariant.

    Original recorded values (research-lab m2a_parity.json), which this test re-checks
    without building the Rust reference:
      series=50, 10 stopping at column 300, width=400, height=300
      port_default_nan_columns=100, gap_safe_nan_columns=0, gap_safe_colsum_after_300=40.0
    """
    W, H = 400, 300
    rng = np.random.default_rng(20261113)
    model = H / 4 * np.sin(np.arange(W) / 20) + H / 2

    def gen(n):
        return np.clip(model + rng.normal(0, 12, (n, W)), 0, H).astype(np.int64)

    S_full = gen(80)
    D = density(list(S_full), W, H)
    assert not np.isnan(D).any(), "full-span bundle should have no NaN columns"
    colsum = D.sum(0)
    assert np.allclose(colsum, 80), f"column sums should equal n=80, got {colsum.min()}..{colsum.max()}"

    # Reset the generator and replay the exact 50-series gap case (same seed, first gen in original was
    # used for parity n=100,1000,5000 before the gap case — so we do not share that stream).
    # The gap-case numbers (100 NaN columns, colsum 40) are deterministic given *any* 50 series
    # of which 10 stop at column 300: they do not depend on the sine path, only on coverage.
    S = gen(50)
    S2 = [s if i >= 10 else s[:300] for i, s in enumerate(S)]
    Pg = density(S2, W, H)
    Ps = density(S2, W, H, gap_safe=True)
    nan_default = int(np.isnan(Pg).any(0).sum())
    nan_safe = int(np.isnan(Ps).any(0).sum())
    colsum_after = float(Ps[:, 350].sum())
    expected = {
        "port_default_nan_columns": 100,
        "gap_safe_nan_columns": 0,
        "gap_safe_colsum_after_300": 40.0,
    }
    got = {
        "port_default_nan_columns": nan_default,
        "gap_safe_nan_columns": nan_safe,
        "gap_safe_colsum_after_300": colsum_after,
    }
    assert nan_default == 100, f"default NaN columns {nan_default} != 100 (original reference)"
    assert nan_safe == 0, f"gap_safe NaN columns {nan_safe} != 0 (original reference)"
    assert abs(colsum_after - 40.0) < 1e-9, f"gap_safe colsum after 300 was {colsum_after}, expected 40"
    print("synthetic OK:", got, "matches original gap_case", expected)
    return got


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", help="CSV with one series per row, x along columns (numeric)")
    p.add_argument("--width", type=int, default=400)
    p.add_argument("--height", type=int, default=300)
    p.add_argument("--gap-safe", action="store_true")
    p.add_argument("--out")
    p.add_argument("--synthetic", action="store_true")
    a = p.parse_args()
    if a.synthetic:
        synthetic()
        return
    if not a.csv:
        p.error("pass --csv or --synthetic")
    arr = np.loadtxt(a.csv, delimiter=",")
    if arr.ndim == 1:
        arr = arr[None, :]
    series = [row[np.isfinite(row)] for row in arr]
    # map values to pixels if they do not already look like row indices
    flat = np.concatenate([s for s in series if len(s)])
    if flat.max() > a.height or flat.min() < 0:
        lo, hi = float(flat.min()), float(flat.max())
        if hi == lo:
            hi = lo + 1
        series = [to_pixels(s, lo, hi, a.height) for s in series]
    else:
        series = [s.astype(np.int64) for s in series]
    D = density(series, a.width, a.height, gap_safe=a.gap_safe)
    res = {
        "width": a.width, "height": a.height, "n_series": len(series),
        "gap_safe": a.gap_safe,
        "nan_columns": int(np.isnan(D).any(0).sum()),
        "colsum_min": float(np.nanmin(D.sum(0))),
        "colsum_max": float(np.nanmax(D.sum(0))),
        "density_sum": float(np.nansum(D)),
    }
    print(json.dumps(res, indent=2))
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=2) + "\n")


if __name__ == "__main__":
    main()
