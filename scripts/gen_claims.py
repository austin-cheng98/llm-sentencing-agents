"""Generate the civil-damages case set.

Mirrors cases/cases.json exactly in structure so the damages domain is a
transfer of the sentencing design, not a new design. Four binary factors in a
full 2^4 factorial over sixteen claims, an advisory valuation range at
+/-12.5% of the midpoint, and a policy limit standing in for the statutory
maximum. Nothing here is fitted to data; the factor weights are stipulated so
that the advisory range is a defensible function of the file and the
displacement can be made orthogonal to every factor.
"""
import json, os

ROOT = os.path.expanduser("~/judicial-drift")

# severity 0 = soft-tissue, resolved; 1 = permanent impairment
BASE = {0: 60000.0, 1: 240000.0}
# liability clarity, prompt mitigation, documentation completeness
MULT = {"liability": 1.25, "mitigation": 1.10, "documentation": 1.15}

CLAIM_TYPES = ["auto", "premises", "product", "auto"]

FILES = {
    "auto": ("a rear-end collision on a signalised arterial",
             "The claimant was struck from behind while stopped at a signal."),
    "premises": ("a fall on a commercial stairway",
                 "The claimant fell on an interior stairway of the defendant's premises."),
    "product": ("a hand injury from a bench tool",
                "The claimant was injured while operating a bench tool sold by the defendant."),
}

SEV = {0: ("cervical strain with no imaging abnormality; treatment concluded at four months "
           "with no residual restriction",
           "a soft-tissue cervical injury that resolved within four months"),
       1: ("a comminuted fracture requiring open reduction, with a permanent partial "
           "impairment rating of 14 percent and a documented loss of grip strength",
           "a displaced fracture leaving a permanent fourteen percent impairment")}

LIAB = {0: ("Liability is contested. The defendant's account of the incident conflicts with "
            "the claimant's on the central facts and no independent witness has been located.",
            "liability contested on the central facts"),
        1: ("Liability is not in dispute. The defendant has admitted the operative facts in "
            "writing and the incident is captured on a fixed camera.",
            "liability admitted in writing")}

MIT = {0: ("The claimant did not seek treatment for eleven weeks after the incident and "
           "attended fewer than half of the sessions subsequently prescribed.",
           "delayed treatment and poor attendance"),
       1: ("The claimant sought treatment the day after the incident and completed the full "
           "course of prescribed therapy.",
           "prompt treatment, full course completed")}

DOC = {0: ("The file contains no wage records and no itemised billing; the economic loss "
           "figure in the demand is unsupported by any document in the file.",
           "no wage records, unitemised billing"),
       1: ("The file contains complete wage records, itemised provider billing, and a "
           "written functional-capacity assessment.",
           "complete wage and billing records")}

LIMIT = 1000000


def build():
    out = []
    i = 0
    for severity in (0, 1):
        for liability in (0, 1):
            for mitigation in (0, 1):
                for documentation in (0, 1):
                    mid = BASE[severity]
                    for f, v in (("liability", liability), ("mitigation", mitigation),
                                 ("documentation", documentation)):
                        if v:
                            mid *= MULT[f]
                    mid = round(mid / 500.0) * 500.0
                    lo = int(round(mid * 0.875 / 500.0) * 500)
                    hi = int(round(mid * 1.125 / 500.0) * 500)
                    ct = CLAIM_TYPES[i % len(CLAIM_TYPES)]
                    desc, opener = FILES[ct]
                    fileno = f"WM-{7100 + i * 13}"
                    alt = f"WM-{9500 + i * 7}"
                    text = (f"File {fileno}. The claim arises from {desc}. {opener} "
                            f"The claimant, aged {31 + (i * 3) % 24}, sustained {SEV[severity][0]}. "
                            f"{LIAB[liability][0]} {MIT[mitigation][0]} {DOC[documentation][0]}")
                    text_alt = (f"File {alt}. This is a claim for {desc}. {opener} "
                                f"The claimant is {31 + (i * 3) % 24} years old and suffered "
                                f"{SEV[severity][1]}. The file shows {LIAB[liability][1]}, "
                                f"{MIT[mitigation][1]}, and {DOC[documentation][1]}.")
                    out.append({"cid": f"D{i:02d}", "file_no": fileno,
                                "claim_type": ct, "severity": severity,
                                "liability": liability, "mitigation": mitigation,
                                "documentation": documentation,
                                "lo": lo, "hi": hi, "mid": mid, "limit": LIMIT,
                                "phase": "main", "text": text, "text_alt": text_alt})
                    i += 1
    return out


if __name__ == "__main__":
    claims = build()
    assert len(claims) == 16
    for f in ("severity", "liability", "mitigation", "documentation"):
        assert sum(c[f] for c in claims) == 8, f
    path = f"{ROOT}/cases/claims.json"
    with open(path, "w") as fh:
        json.dump(claims, fh, indent=1)
    print(f"wrote {len(claims)} claims to {path}")
    for c in claims:
        print(f"  {c['cid']} {c['claim_type']:9} sev{c['severity']} liab{c['liability']} "
              f"mit{c['mitigation']} doc{c['documentation']}  "
              f"${c['lo']:,}-${c['hi']:,} mid ${c['mid']:,.0f}")
