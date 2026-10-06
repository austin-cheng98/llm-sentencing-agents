"""Recompute the released civil-damages analyses from the recorded decisions."""
import importlib
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = str(ROOT / "scripts")
sys.path.insert(0, SCRIPTS)

expanduser = os.path.expanduser
os.path.expanduser = lambda path: str(ROOT) if path == "~/judicial-drift" else expanduser(path)
try:
    import damages as D
finally:
    os.path.expanduser = expanduser

D.ROOT = str(ROOT)

for name in ("damages_analysis", "damages_analysis_ext",
             "damages_analysis_prox", "damages_analysis_d2"):
    print(f"\n{'=' * 60}\n{name}\n{'=' * 60}", flush=True)
    if name == "damages_analysis_ext":
        # This freeze predates the separate A12/A01 proximity confirmation.
        load = D.load
        D.load = lambda run: [
            row for row in load(run)
            if run != "D1" or row["judge"] not in {"A12", "A01"}
        ]
        try:
            importlib.import_module(name).main()
        finally:
            D.load = load
    else:
        importlib.import_module(name).main()
