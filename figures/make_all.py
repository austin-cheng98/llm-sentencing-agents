"""Rebuild every figure the paper uses, from this repository's own data.

Each script runs in its own process: figstyle.setup() changes global matplotlib
state, so sharing one interpreter would make the output depend on run order.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = ["fig_forest", "fig_sentences", "fig_models", "fig_main", "fig_cascade",
        "fig_damages_civil", "fig_design", "fig_confidence", "fig_factors"]

for name in FIGS:
    r = subprocess.run([sys.executable, os.path.join(HERE, name + ".py")],
                       capture_output=True, text=True)
    if r.returncode:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit(f"{name} failed")
    print("ok", name)
