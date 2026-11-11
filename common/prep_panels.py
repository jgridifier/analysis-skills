"""Build the analysis panels from the raw Drive files and write a data manifest.

Raw files are read from $AS_DATA_DIR (default /workspace/scout/data) and never committed.
Panels are written to $AS_WORK_DIR (default <repo>/.work/panels), which is git-ignored.
The manifest (file names, Drive ids, retrieval date, row counts, sha256 of the fetched
bytes) is written to data/MANIFEST.json and IS committed: it carries no row-level data.

Usage: python common/prep_panels.py
"""
import hashlib, json, os, pathlib
import numpy as np, pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
D = pathlib.Path(os.environ.get("AS_DATA_DIR", "/workspace/scout/data"))
O = pathlib.Path(os.environ.get("AS_WORK_DIR", ROOT / ".work" / "panels"))
O.mkdir(parents=True, exist_ok=True)

DRIVE = {  # name -> (Drive file id, note)
    "VIXCLS.csv": "1oR2YeiLnbwzaUfS48h5iyoj_0GOAq7gs",
    "T10Y2Y.csv": "1StWWFDf1D4tuIdnpEpi1ZF7lxI52IbSU",
    "DGS2.csv": "15_SMUHNukWjF45TXGxEyhuyDYSEYimGp",
    "DGS10.csv": "19lhQpy3JxSTVyS73s7jCA9ly1CjdusXF",
    "MORTGAGE30US.csv": "1czZ1kub5e-7kf81ROdso06WNkTuXH-sx",
    "NFCI.csv": "1XtT0rC15EPaOsh2Oc_Xsw06Dky98GmWm",
    "STLFSI4.csv": "18VuYJxft7OOfpd5EdyX0qv4dX3lGZtsN",
    "ebp_monthly.csv": "1VeBSWZjwd_65hqvhLQ3TuutYn8QEOKJ0",
    "county_panel.xlsx": "1YfMJUsjbQoOEC5k8JiqeYSX8atFZDsbVi9lomoyV5Zg",
}
RETRIEVED = "2026-11-10"  # date the files were fetched from Drive for the first scout run


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def s(name):
    x = pd.read_csv(D / f"{name}.csv"); x.columns = ["date", name]
    x["date"] = pd.to_datetime(x["date"]); x[name] = pd.to_numeric(x[name], errors="coerce")
    return x.set_index("date")[name].dropna()


def main():
    ser = {n: s(n) for n in ["VIXCLS", "T10Y2Y", "DGS2", "DGS10", "MORTGAGE30US", "NFCI", "STLFSI4"]}
    ebp = pd.read_csv(D / "ebp_monthly.csv", parse_dates=["date"]).set_index("date")
    # monthly panel (month-end mean) -- identical logic to the 2026-11-10 scout prep.py
    M = pd.DataFrame({k: v.resample("ME").mean() for k, v in ser.items()})
    e = ebp[["gz_spread", "ebp"]].copy(); e.index = e.index + pd.offsets.MonthEnd(0)
    M = M.join(e, how="left").loc["1990-01-31":]
    M["dDGS2_12"] = M.DGS2 - M.DGS2.shift(12)
    M["dMORT_12"] = M.MORTGAGE30US - M.MORTGAGE30US.shift(12)
    M["dGZ_3"] = M.gz_spread - M.gz_spread.shift(3)
    M["y_fwd6"] = M.gz_spread.shift(-6) - M.gz_spread
    M["dGZ"] = M.gz_spread.diff(); M["dVIX"] = M.VIXCLS.diff(); M["dDGS10"] = M.DGS10.diff()
    M.index.name = "date"; M.to_csv(O / "monthly_panel.csv")
    W = pd.DataFrame({k: v.resample("W-FRI").mean() for k, v in ser.items()}).loc["1994-01-07":]
    W = W.ffill(limit=2).dropna(); W.index.name = "date"; W.to_csv(O / "weekly_panel.csv")
    Dd = pd.DataFrame({k: ser[k] for k in ["VIXCLS", "T10Y2Y", "DGS2", "DGS10"]}).loc["1990-01-02":].dropna()
    Dd.index.name = "date"; Dd.to_csv(O / "daily_panel.csv")
    # county sheet: tab 1 = panel, tab "Education" = attainment by period
    x = pd.ExcelFile(D / "county_panel.xlsx")
    P = pd.read_excel(x, sheet_name=0); E = pd.read_excel(x, sheet_name="Education")
    P.to_csv(O / "county_panel.csv", index=False); E.to_csv(O / "county_edu.csv", index=False)

    rows = {"VIXCLS.csv": len(ser["VIXCLS"]), "T10Y2Y.csv": len(ser["T10Y2Y"]), "DGS2.csv": len(ser["DGS2"]),
            "DGS10.csv": len(ser["DGS10"]), "MORTGAGE30US.csv": len(ser["MORTGAGE30US"]), "NFCI.csv": len(ser["NFCI"]),
            "STLFSI4.csv": len(ser["STLFSI4"]), "ebp_monthly.csv": len(ebp), "county_panel.xlsx": len(P)}
    man = {"retrieved": RETRIEVED, "source": "Google Drive (owner's research data)",
           "note": "Raw files are not committed. sha256 is of the fetched bytes; rows = non-missing observations "
                   "(FRED) or data rows (other files).",
           "files": [{"file": f, "drive_id": DRIVE[f], "rows": int(rows[f]), "bytes": (D / f).stat().st_size,
                      "sha256": sha(D / f)} for f in DRIVE],
           "panels": {p.name: {"rows": int(sum(1 for _ in open(p)) - 1), "sha256": sha(p)}
                      for p in sorted(O.glob("*.csv"))}}
    (ROOT / "data").mkdir(exist_ok=True)
    json.dump(man, open(ROOT / "data" / "MANIFEST.json", "w"), indent=1)
    print(json.dumps(man["panels"], indent=1))


if __name__ == "__main__":
    main()
