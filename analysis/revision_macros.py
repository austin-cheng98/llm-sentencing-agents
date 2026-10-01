"""Write revision statistics as LaTeX macros."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

R = json.load(open(f"{ROOT}/analysis/out_robustness.json"))
P = json.load(open(f"{ROOT}/analysis/out_power.json"))
B = json.load(open(f"{ROOT}/analysis/out_balanced.json"))
E = json.load(open(f"{ROOT}/analysis/out_equivalence.json"))
X = json.load(open(f"{ROOT}/analysis/out_crosslineage.json"))

out = []


def mac(n, v):
    out.append(f"\\newcommand{{\\{n}}}{{{v}}}")


def p(v):
    """Format a p-value."""
    return "<0.001" if v < 0.001 else f"{v:.3f}"


def sg(v, nd=3):
    """Format a signed estimate."""
    return f"${v:+.{nd}f}$".replace("+", "+").replace("-", "-")


s, a = R["sentences"], R["anchors"]
mac("rbSentN", s["n"])
mac("rbDistinct", s["distinct"])
mac("rbDivSix", f"{s['div6']:.0f}")
mac("rbDivTwelve", f"{s['div12']:.0f}")
mac("rbDivFive", f"{s['div5']:.0f}")
mac("rbMode", s["modes"][0][0])
mac("rbAncSix", f"{a['div6']:.1f}")
mac("rbAncFive", f"{a['div5']:.1f}")
mac("rbAncAll", f"{a['allthree_div6']:.0f}")

e = R["exact"]
mac("rbExact", f"{e['rate']:.0f}")
mac("rbExactN", e["n"])
mac("rbExactRound", f"{e['round_share']:.0f}")
mac("rbMatchRound", f"{e['rate_on_round_anchors']:.0f}")
mac("rbMatchPlain", f"{e['rate_no_round_anchor']:.0f}")

TAG = {"matched_struct": "MS", "matched_bare": "MB", "original_sentences": "OS"}
for k, t in TAG.items():
    c = R["premium_nonround"].get(k)
    if c:
        mac(f"rbNR{t}", f"{c['est']:+.2f}".replace("+", ""))
        mac(f"rbNR{t}p", p(c["p"]))
        mac(f"rbNR{t}n", c["n"])

for k, t in TAG.items():
    for mg, lab in (("0.15", "Lo"), ("0.3", "Hi")):
        c = R["by_magnitude"].get(k, {}).get(mg)
        if c:
            mac(f"rbMag{t}{lab}", f"{c['est']:+.2f}".replace("+", ""))
            mac(f"rbMag{t}{lab}p", p(c["p"]))

for k, t in TAG.items():
    for sc, lab in (("log", "Log"), ("caserank", "Rank")):
        c = R["scale"].get(k, {}).get(sc)
        if c:
            mac(f"rb{lab}{t}", f"{c['est']:+.2f}".replace("+", ""))
            mac(f"rb{lab}{t}p", p(c["p"]))

c = R["confidence"]
mac("rbConfDistinct", c["distinct"])
mac("rbConfTop", f"{c['top2_share']:.0f}")

I = json.load(open(f"{ROOT}/analysis/out_inference.json"))
if I.get("decoding", {}).get("sd") is not None:
    mac("decodeSD", f"{I['decoding']['sd']:.3f}")
    mac("decodeCells", I["decoding"]["cells"])

by = {r["label"]: r for r in P["rows"]}
mac("pwUnder", P["n_underpowered"])
mac("pwTotal", P["n_total"])
mac("pwBench", f"{P['benchmark']:.2f}")
for label, tag in (("premium sonnet5|no guideline", "SonNG"),
                   ("premium haiku45|no guideline", "HaiNG"),
                   ("premium sonnet5|guideline", "SonG"),
                   ("premium haiku45|guideline", "HaiG"),
                   ("guideline removal sonnet5", "GxSon"),
                   ("opus5 matched_struct", "MS"),
                   ("opus5 matched_bare", "MB"),
                   ("premium pooled small models", "Pool")):
    r = by.get(label)
    if r:
        mac(f"pwMde{tag}", f"{r['mde']:.2f}")
        mac(f"pwEst{tag}", f"{r['est']:+.2f}".replace("+", ""))
        mac(f"pwLo{tag}", f"{r['ci'][0]:+.2f}".replace("+", ""))
        mac(f"pwHi{tag}", f"{r['ci'][1]:+.2f}".replace("+", ""))

mac("blBench", f"{B['benchmark']:.3f}")
for key, tag in (("sonnet5|matched_struct", "SonMS"),
                 ("haiku45|matched_struct", "HaiMS"),
                 ("sonnet5|matched_bare", "SonMB"),
                 ("haiku45|matched_bare", "HaiMB")):
    r = B["rows"].get(key)
    if not r or r.get("est") is None:
        continue
    mac(f"bl{tag}N", r["n"])
    mac(f"bl{tag}Est", f"{r['est']:+.3f}".replace("+", ""))
    mac(f"bl{tag}P", p(r["p"]))
    mac(f"bl{tag}Mde", f"{r['mde']:.3f}")
    mac(f"bl{tag}Lo", f"{r['ci'][0]:+.3f}".replace("+", ""))
    mac(f"bl{tag}Hi", f"{r['ci'][1]:+.3f}".replace("+", ""))

eq = next((r for r in E["rows"] if r["label"] == "equivalence"
           and r.get("est") is not None), None)
if eq:
    mac("eqN", eq["n"])
    mac("eqEst", f"{eq['est']:+.3f}".replace("+", ""))
    mac("eqP", p(eq["p"]))
    mac("eqMde", f"{eq['mde']:.3f}")
    mac("eqLo", f"{eq['ci'][0]:+.3f}".replace("+", ""))
    mac("eqHi", f"{eq['ci'][1]:+.3f}".replace("+", ""))

for lab, tag in (("reliability", "rl"), ("peer_reliability", "rlPeer"),
                 ("tool_reliability", "rlTool")):
    r = next((x for x in E["rows"] if x["label"] == lab
              and x.get("est") is not None), None)
    if not r:
        continue
    mac(f"{tag}N", r["n"])
    mac(f"{tag}Est", f"{r['est']:+.3f}".replace("+", ""))
    mac(f"{tag}P", p(r["p"]))
    mac(f"{tag}Mde", f"{r['mde']:.3f}")
    mac(f"{tag}Lo", f"{r['ci'][0]:+.3f}".replace("+", ""))
    mac(f"{tag}Hi", f"{r['ci'][1]:+.3f}".replace("+", ""))

for lab, tag in (("matched_struct", "MS"), ("matched_bare", "MB")):
    r = X["rows"].get(f"{X['lineage']}|{lab}")
    if not r or r.get("est") is None:
        continue
    mac(f"xl{tag}N", r["n"])
    mac(f"xl{tag}Est", f"{r['est']:+.3f}".replace("+", ""))
    mac(f"xl{tag}P", p(r["p"]))
    mac(f"xl{tag}Mde", f"{r['mde']:.3f}")
    mac(f"xl{tag}Lo", f"{r['ci'][0]:+.3f}".replace("+", ""))
    mac(f"xl{tag}Hi", f"{r['ci'][1]:+.3f}".replace("+", ""))
    mac(f"xl{tag}Bench", f"{r['bench']:.3f}")

txt = "\n".join(out) + "\n"
open(f"{ROOT}/analysis/out_revision_macros.tex", "w").write(txt)
print(txt)
print(f"{len(out)} macros")
