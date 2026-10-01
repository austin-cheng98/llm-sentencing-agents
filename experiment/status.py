"""Which cells of an arm are still missing, and how far collection has got.

    python3 experiment/status.py todo ARM JUDGE [--run R1]
    python3 experiment/status.py

`todo` prints the step numbers not yet recorded for that agent in that arm, which
is what a collection worker reads at the top of each loop. With no arguments it
prints a grid of the four displacement arms.
"""
import json, glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JUDGES = ["P1", "P2", "P3", "P4", "P5", "P6", "S1", "H1"]
ARMS = ["peerdelta", "tooldelta", "peerdelta_ng", "tooldelta_ng"]


def have(run):
    h = {}
    for f in glob.glob(os.path.join(ROOT, "runs", run, "*.jsonl")):
        for line in open(f):
            if not line.strip():
                continue
            r = json.loads(line)
            if r["ok"]:
                h.setdefault((r["arm"], r["judge"]), set()).add(r["step"])
    return h


def main(argv):
    run = "R1"
    if "--run" in argv:
        i = argv.index("--run")
        run = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if len(argv) > 2 and argv[1] == "todo":
        arm, judge = argv[2], argv[3]
        # the memory arms run the full sequence, including the returning cases
        n = 20 if arm in ("nohist", "ownhist", "social") else 16
        h = have(run).get((arm, judge), set())
        print(" ".join(str(s) for s in range(n) if s not in h))
        return
    h = have(run)
    tot = done = 0
    for a in ARMS:
        row = []
        for j in JUDGES:
            n = len(h.get((a, j), set()) & set(range(16)))
            tot += 16
            done += n
            row.append(f"{j}:{n:2d}")
        print(f"  {a:14s} " + "  ".join(row))
    print(f"leaf decisions: {done}/{tot} complete ({100 * done / tot:.0f}%)")


if __name__ == "__main__":
    main(sys.argv)
