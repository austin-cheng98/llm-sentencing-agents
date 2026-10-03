"""Rebuild all figures from analysis outputs."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGURES = ["fig_forest", "fig_sentences", "fig_models", "fig_main", "fig_cascade",
           "fig_design", "fig_confidence", "fig_factors"]

for name in FIGURES:
    print(f"\n{'=' * 62}\n{name}\n{'=' * 62}", flush=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, f"{name}.py")])
    if r.returncode != 0:
        sys.exit(f"{name} failed")
