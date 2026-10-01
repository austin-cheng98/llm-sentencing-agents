"""Runs every analysis in order and writes the JSON each one produces."""
import subprocess, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# robustness and power come last: power reads the JSON that inference and
# crossmodel write, and revision_macros reads both of theirs
STEPS = ["integrity", "anchoring", "trailer", "randomization", "framing",
         "memory", "crossmodel", "inference", "cascade", "dispersion", "confidence", "census",
         "robustness", "equivalence", "balanced", "crosslineage", "power", "revision_macros"]

for name in STEPS:
    print(f"\n{'=' * 62}\n{name}\n{'=' * 62}", flush=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, f"{name}.py")])
    if r.returncode != 0:
        sys.exit(f"{name} failed")
