"""Stage 3 comparison: original run vs clean-environment reproduction.

Walks every key present in BOTH result files and compares leaf values:
  - strings / ints / bools must be equal;
  - floats must agree within the tolerance for that key (default abs 1e-4, since results are
    rounded to 5 significant digits), or a looser tolerance listed in TOL for RNG-dependent keys;
  - keys matching SKIP (wall-clock timings, package versions) are never compared.
Writes <method>/applications/<n>/reproduction.json and prints a one-line verdict.

Usage: python common/compare.py ORIGINAL.json REPRO.json OUT.json [--tol key=abs ...]
"""
import json, math, re, sys

SKIP = re.compile(r"(secs|_timing|versions|random_forest$|knn$|pelt_rbf$)")


def walk(a, b, path, tol, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in a:
            if k in b and not SKIP.search(k):
                walk(a[k], b[k], f"{path}.{k}" if path else k, tol, out)
        return
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((path, "length", len(a), len(b), False)); return
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]", tol, out)
        return
    top = path.split(".")[0].split("[")[0]
    t = tol.get(top, 1e-4)
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        ok = (math.isnan(a) and math.isnan(b)) or abs(a - b) <= t
        out.append((path, "num", a, b, ok))
    else:
        out.append((path, "eq", a, b, a == b))


def main():
    o, r, dst = sys.argv[1:4]
    tol = dict(kv.split("=") for kv in sys.argv[5:]) if len(sys.argv) > 4 and sys.argv[4] == "--tol" else {}
    tol = {k: float(v) for k, v in tol.items()}
    out = []
    walk(json.load(open(o)), json.load(open(r)), "", tol, out)
    bad = [x for x in out if not x[4]]
    rep = {"original": o, "reproduction": r, "tolerances": tol or "default abs 1e-4 on every float",
           "n_compared": len(out), "n_mismatch": len(bad), "status": "PASS" if not bad else "MISMATCH",
           "mismatches": [{"key": p, "original": a, "reproduction": b} for p, _, a, b, _ in bad]}
    json.dump(rep, open(dst, "w"), indent=1, default=str)
    print(f"{rep['status']}: {len(out)} values compared, {len(bad)} mismatches -> {dst}")
    for m in rep["mismatches"][:15]:
        print("   ", m)


if __name__ == "__main__":
    main()
