#!/usr/bin/env bash
# Stage 3: rebuild clean environments from the lockfiles, rerun every application, compare.
# Needs the raw Drive files in $AS_DATA_DIR (see data/MANIFEST.json); they are never committed.
set -euo pipefail
cd "$(dirname "$0")"
: "${AS_DATA_DIR:=/workspace/scout/data}"; export AS_DATA_DIR
: "${AS_FIG_DIR:=$PWD/docs/fig}"; export AS_FIG_DIR
PYENV=${PYENV:-/tmp/as-clean-py}; RENV=${RENV:-/tmp/as-clean-r}
[ -x "$PYENV/bin/python" ] || { python3 -m venv "$PYENV"; "$PYENV/bin/pip" install -q --no-cache-dir -r env/requirements.lock.txt; }
[ -x "$RENV/bin/Rscript" ] || micromamba create -y -p "$RENV" --file env/r-conda-lock.txt
"$PYENV/bin/python" common/prep_panels.py
for i in 1 2 3; do "$RENV/bin/Rscript" methods/partykit/applications/$i/run.R; done
for i in 1 2 3; do "$PYENV/bin/python" methods/changeforest/applications/$i/run.py; done
C="$PYENV/bin/python common/compare.py"
$C methods/partykit/original/m1_results.json methods/partykit/applications/1/out/results.json methods/partykit/applications/1/reproduction.json
$C methods/partykit/original/m1_results.json methods/partykit/applications/2/out/results.json methods/partykit/applications/2/reproduction.json
$C methods/partykit/original/m1_results.json methods/partykit/applications/3/out/results.json methods/partykit/applications/3/reproduction.json --tol A4_gr_cv=0.03 A4_cv_cv=0.03
$C methods/changeforest/original/m2_results.json methods/changeforest/applications/1/out/results.json methods/changeforest/applications/1/reproduction.json
$C methods/changeforest/original/m2_results.json methods/changeforest/applications/2/out/results.json methods/changeforest/applications/2/reproduction.json
$C methods/changeforest/applications/3/out_original_scoutenv/results.json methods/changeforest/applications/3/out/results.json methods/changeforest/applications/3/reproduction.json
