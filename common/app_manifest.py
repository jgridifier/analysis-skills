"""Write applications/<n>/manifest.json: which raw Drive files and derived panels an application
reads, with Drive ids, retrieval date, row counts and sha256 (from data/MANIFEST.json), plus
environment, seed and command. No row-level data is written.
"""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
MAN = json.load(open(ROOT / "data" / "MANIFEST.json"))
FRED = ["VIXCLS.csv", "T10Y2Y.csv", "DGS2.csv", "DGS10.csv", "MORTGAGE30US.csv", "NFCI.csv", "STLFSI4.csv"]
APPS = {
    ("partykit", 1): dict(files=FRED + ["ebp_monthly.csv"], panels=["monthly_panel.csv"], env="R", seed=20261110),
    ("partykit", 2): dict(files=FRED + ["ebp_monthly.csv"], panels=["monthly_panel.csv"], env="R", seed=20261110),
    ("partykit", 3): dict(files=["county_panel.xlsx"], panels=["county_panel.csv", "county_edu.csv"], env="R", seed=20261110),
    ("changeforest", 1): dict(files=["VIXCLS.csv", "T10Y2Y.csv", "DGS2.csv", "MORTGAGE30US.csv", "NFCI.csv", "STLFSI4.csv"], panels=["weekly_panel.csv"], env="py", seed="changeforest Control() default; seeds 0-9 for stability; numpy rng(1) shuffles, rng(7) VAR null"),
    ("changeforest", 2): dict(files=["VIXCLS.csv", "T10Y2Y.csv", "DGS2.csv", "DGS10.csv"], panels=["daily_panel.csv"], env="py", seed="changeforest Control() default; seeds 0-9; numpy rng(1) shuffles, rng(7) VAR null, rng(0) synthetic"),
    ("changeforest", 3): dict(files=FRED + ["ebp_monthly.csv"], panels=["monthly_panel.csv"], env="py", seed="changeforest Control() default; seeds 0-9; numpy rng(1) shuffles, rng(7) VAR null"),
}
ENV = {"R": {"lockfile": "env/r-conda-lock.txt", "packages": "env/r-packages.csv", "R": "4.4.3", "partykit": "1.2-29", "rpart": "4.1.27"},
       "py": {"lockfile": "env/requirements.lock.txt", "python": "3.13.5", "changeforest": "1.2.1", "ruptures": "1.1.10"}}
for (m, n), a in APPS.items():
    d = ROOT / "methods" / m / "applications" / str(n)
    cmd = f"Rscript methods/{m}/applications/{n}/run.R" if a["env"] == "R" else f"python methods/{m}/applications/{n}/run.py"
    out = {"retrieved": MAN["retrieved"], "source": MAN["source"],
           "raw_files": [f for f in MAN["files"] if f["file"] in a["files"]],
           "derived_panels": {p: MAN["panels"][p] for p in a["panels"]},
           "build_panels": "python common/prep_panels.py", "command": cmd, "seed": a["seed"], "environment": ENV[a["env"]],
           "committed_outputs": ["out/results.json (aggregates only)", "reproduction.json"]}
    json.dump(out, open(d / "manifest.json", "w"), indent=1)
print("ok")
