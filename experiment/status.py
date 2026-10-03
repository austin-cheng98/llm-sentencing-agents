"""Report missing collection cells."""
import json, glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JUDGES = ["P1", "P2", "P3", "P4", "P5", "P6", "S1", "H1"]
ARMS = ["peerdelta", "tooldelta", "peerdelta_ng", "tooldelta_ng"]
R6_JUDGES = ["P1", "P2", "P3", "P4", "P5", "P6", "S1", "S2", "H1", "H2"]
R6_JUDGES += [f"G{i:02d}" for i in range(1, 17)]
R6_ARMS = ["peerbare_ng", "toolbare_ng", "peermatch_ng"]


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
        n = 20 if arm in ("nohist", "ownhist", "social") else 16
        h = have(run).get((arm, judge), set())
        print(" ".join(str(s) for s in range(n) if s not in h))
        return
    h = have(run)
    judges, arms = (R6_JUDGES, R6_ARMS) if run == "R6" else (JUDGES, ARMS)
    tot = done = 0
    for a in arms:
        row = []
        for j in judges:
            n = len(h.get((a, j), set()) & set(range(16)))
            tot += 16
            done += n
            row.append(f"{j}:{n:2d}")
        print(f"  {a:14s} " + "  ".join(row))
    print(f"leaf decisions: {done}/{tot} complete ({100 * done / tot:.0f}%)")


if __name__ == "__main__":
    main(sys.argv)
