"""Write the per-arm decision census as LaTeX."""
import json, os, sys, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

LABEL = {"peerdelta": "Peer, guideline present", "tooldelta": "Forecast, guideline present",
         "peerdelta_ng": "Peer, original closing line", "tooldelta_ng": "Forecast, hedged",
         "peerbare_ng": "Peer, bare block", "toolbare_ng": "Forecast, bare block",
         "peermatch_ng": "Peer, structure-matched", "parafree_ng": "Peer, paraphrase one",
         "paraown_ng": "Peer, paraphrase two", "clerdelta_ng": "Docketing artifact",
         "nohist": "No numbers, guideline present", "nohist_ng": "No numbers, guideline removed",
         "ownhist": "Own-record summary", "cascade_ng": "Live cascade",
         "peereqv_ng": "Peer, same-file sentence", "tooleqv_ng": "Forecast, same-file sentence",
         "peerrel_ng": "Peer, stated reliability", "toolrel_ng": "Forecast, stated reliability"}
MODEL = {"opus5": "Opus 5", "sonnet5": "Sonnet 5", "haiku45": "Haiku 4.5",
         "gpt6": "GPT-6 Luna"}
ORDER = ["peerbare_ng", "toolbare_ng", "peermatch_ng", "parafree_ng", "paraown_ng",
         "peerdelta_ng", "tooldelta_ng", "clerdelta_ng", "peerdelta", "tooldelta",
         "peereqv_ng", "tooleqv_ng", "peerrel_ng", "toolrel_ng",
         "nohist", "nohist_ng", "ownhist", "cascade_ng"]


def main():
    cells, agents, seen = collections.Counter(), collections.defaultdict(set), set()
    with open(os.path.join(ROOT, "data", "decisions.jsonl")) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            k = (r.get("model"), r.get("arm"), r.get("judge"), r.get("cid"), r.get("step"))
            if k in seen:
                continue
            seen.add(k)
            cells[(r["arm"], r["model"])] += 1
            agents[(r["arm"], r["model"])].add(r["judge"])

    lines = ["\\begin{tabular}{llrr}", "\\toprule",
             "Arm & Model & Agents & Decisions \\\\", "\\midrule"]
    total = 0
    for arm in ORDER:
        for m in MODEL:
            n = cells.get((arm, m))
            if not n:
                continue
            lines.append(f"{LABEL.get(arm, arm)} & {MODEL[m]} & "
                         f"{len(agents[(arm, m)])} & {n} \\\\")
            total += n
    lines += ["\\midrule", f"\\multicolumn{{3}}{{l}}{{Total}} & {total} \\\\",
              "\\bottomrule", "\\end{tabular}"]
    out = os.path.join(ROOT, "analysis", "out_census.tex")
    open(out, "w").write("\n".join(lines) + "\n")
    print(f"  wrote analysis/out_census.tex, {total} decisions over "
          f"{len(set(a for a, _ in cells))} arms and {len(MODEL)} models")
    for arm in ORDER:
        for m in MODEL:
            if cells.get((arm, m)):
                print(f"    {LABEL[arm]:30s} {MODEL[m]:11s} "
                      f"{len(agents[(arm, m)]):2d} agents  {cells[(arm, m)]:4d}")


if __name__ == "__main__":
    main()
