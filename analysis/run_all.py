"""Runs every analysis in order and writes the JSON each one produces."""
import subprocess, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["integrity", "anchoring", "trailer", "randomization", "framing",
         "memory", "crossmodel", "inference", "cascade", "dispersion", "confidence", "census",
         "robustness", "equivalence", "balanced", "crosslineage", "power"]

for name in STEPS:
    print(f"\n{'=' * 62}\n{name}\n{'=' * 62}", flush=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, f"{name}.py")])
    if r.returncode != 0:
        sys.exit(f"{name} failed")

for name, path in (("r7_source_access", os.path.join(HERE, "..", "experiment",
                                                      "r7_source_access.py")),
                   ("revision_macros", os.path.join(HERE, "revision_macros.py"))):
    print(f"\n{'=' * 62}\n{name}\n{'=' * 62}", flush=True)
    r = subprocess.run([sys.executable, path, "analyze"] if name == "r7_source_access"
                       else [sys.executable, path])
    if r.returncode != 0:
        sys.exit(f"{name} failed")
