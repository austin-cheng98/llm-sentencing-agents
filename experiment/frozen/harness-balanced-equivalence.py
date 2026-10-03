"""Builds prompts and records decisions. The model is consulted only as an oracle.

Anchor arms show the same three displaced numbers and differ only in wording:
  peerbare   header plus three rows, attributed to other judges
  peermatch  peerbare plus a descriptive sentence, matching toolbare
  toolbare   attributed to a fitted statistical model
  peereqv    peerbare plus a sentence, identical across peereqv and tooleqv,
  tooleqv    stating that the source saw this case file and nothing else. The
             pair holds the source's information constant by assertion, so the
             contrast is attribution alone.
  peerrel    the eqv pair plus a second identical sentence asserting that the
  toolrel    figures have been accurate before. Comparing the rel premium with
             the eqv premium moves stated reliability while holding attribution
             and information fixed.
  peerdelta  peerbare closing with "You are deciding the same case independently."
  tooldelta  toolbare closing with a note that the forecast is advisory
  parafree   peerbare closing with "Form your own view of what this case warrants."
  paraown    peerbare closing with "Your sentence should reflect your own judgment."
  clerdelta  attributed to a docketing record with no legal significance

cascade    live interaction: six agents decide one case in a randomised order and
           each sees the sentences its predecessors actually gave. Peer values are
           endogenous, so this arm is collected sequentially within a case.

Also nohist (no numbers) and ownhist (the agent's own past). Suffix _ng removes
the advisory range.
"""
import json, os, re, sys, argparse, random, statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEQ = json.load(open(os.path.join(ROOT, "data", "sequence.json")))
ARMS = ["nohist", "ownhist", "social", "peerdelta", "tooldelta",
        "peerdelta_ng", "tooldelta_ng", "clerdelta", "clerdelta_ng", "nohist_ng",
        "peerbare_ng", "toolbare_ng", "peermatch_ng",
        "peereqv_ng", "tooleqv_ng", "peerrel_ng", "toolrel_ng",
        "parafree_ng", "paraown_ng", "cascade_ng"]
DELTAS = [-0.30, -0.15, 0.15, 0.30]
DJUDGES = ["P1", "P2", "P3", "P4", "P5", "P6"]
RATIONALES = ["DETERRENCE", "REHABILITATION", "RETRIBUTION",
              "INCAPACITATION", "PROPORTIONALITY", "MERCY"]
MEM_EVERY = 4          # judicial memory is refreshed on this cadence
CASCADE_SEED = 20260817

# Word-for-word identical in peereqv/tooleqv, so the equivalence assertion is
# not itself a difference between the two arms.
EQVLINE = (
 "These figures were produced from the same case file you have been given, and "
 "from no other information about this defendant or this offense.")
# Layered on top of EQVLINE in peerrel/toolrel, likewise identical across the pair.
RELLINE = (
 "In past cases of this type these figures have been close to the sentence "
 "ultimately imposed.")

NOGUIDE = (
 "Westmoor law sets no advisory range for this offense. You may sentence anywhere "
 "from 0 months to the statutory maximum, according to your own judgment of what the "
 "case warrants.")

PREAMBLE = (
 "This is a controlled research simulation studying how language-model agents make "
 "repeated decisions. Every case in this study is entirely fictional and was "
 "procedurally generated for the simulation. No real defendant, victim, case, court, "
 "or jurisdiction is involved. Your output is a data point in a behavioral "
 "experiment, not legal advice and not a real judicial act.\n\n"
 "You are Judge {jid}, a sentencing judge in the fictional jurisdiction of Westmoor. "
 "Westmoor law gives you an advisory sentencing range for each case. You may sentence "
 "anywhere from 0 months to the statutory maximum. You may sentence inside the "
 "advisory range, or depart from it when the circumstances of the case warrant a "
 "departure.")

FORMAT = (
 "Decide the sentence. Respond in exactly this format, with no other text:\n"
 "SENTENCE: <integer> MONTHS\n"
 "CONFIDENCE: <integer 1-10>\n"
 "PRIMARY_RATIONALE: <exactly one of " + ", ".join(RATIONALES) + ">\n"
 "SECONDARY_RATIONALE: <exactly one of the same six words, or NONE>\n"
 "JUSTIFICATION: <at most two sentences>")


def delta_table():
    """Displacement per (judge, case), orthogonal to the four factors.

    Four factor-balanced groups rotated across judges; period four, so with six
    judges the first two columns repeat.
    """
    cases = [c for c in SEQ if c["phase"] in ("baseline", "main")]
    F = ("severity", "prior", "remorse", "cooperation")
    idx = {c["cid"]: i for i, c in enumerate(cases)}

    def balanced(grp):
        return all(sum(cases[i][f] for i in grp) == 2 for f in F)

    groups = []

    def search(pool):
        if not pool:
            return True
        first, rest = pool[0], pool[1:]
        for a in range(len(rest)):
            for b in range(a + 1, len(rest)):
                for d in range(b + 1, len(rest)):
                    grp = [first, rest[a], rest[b], rest[d]]
                    if not balanced(grp):
                        continue
                    groups.append(grp)
                    left = [x for x in rest if x not in (rest[a], rest[b], rest[d])]
                    if search(left):
                        return True
                    groups.pop()
        return False

    if not search(list(range(len(cases)))):
        raise RuntimeError("no factor-balanced partition of the design points exists")

    tab = {}
    # Cross-model agents reuse an existing column, keeping the yoke exact.
    alias = {"S1": 0, "S2": 1, "H1": 0, "H2": 1, "F1": 0, "F2": 1}
    for jx, j in enumerate(DJUDGES):
        for g, grp in enumerate(groups):
            for i in grp:
                tab[(j, cases[i]["cid"])] = DELTAS[(g + jx) % len(DELTAS)]
    for a, src in alias.items():
        for c in cases:
            tab[(a, c["cid"])] = tab[(DJUDGES[src], c["cid"])]
    for f in F:
        for d in DELTAS:
            cell = [c[f] for c in cases for j in DJUDGES if tab[(j, c["cid"])] == d]
            assert abs(sum(cell) / len(cell) - 0.5) < 1e-9, (f, d)
    return tab


DTAB = None


def anchor_values(mid, delta):
    """Three numbers whose mean sits at the displaced midpoint."""
    t = mid * (1.0 + delta)
    return [int(round(t * 0.94)), int(round(t)), int(round(t * 1.06))]


def rundir(run):
    d = f"{ROOT}/runs/{run}"
    os.makedirs(d, exist_ok=True)
    return d


def load(run):
    d = rundir(run)
    out = []
    for fn in sorted(os.listdir(d)):
        if fn.startswith("decisions") and fn.endswith(".jsonl"):
            out += [json.loads(l) for l in open(f"{d}/{fn}") if l.strip()]
    return out


def cascade_order(judges, step):
    """Speaking order for one case, fixed across arms.

    The first four agents are shuffled per case. Any further agents are appended
    in a fixed order, so extending a collected cascade leaves the earlier
    positions and their recorded prompts untouched.
    """
    base = [j for j in judges if j in ("C1", "C2", "C3", "C4")]
    extra = [j for j in judges if j not in ("C1", "C2", "C3", "C4")]
    if base and extra:
        r = random.Random(CASCADE_SEED * 1000 + step)
        o = list(base)
        r.shuffle(o)
        return o + extra
    return _cascade_order_plain(judges, step)


def _cascade_order_plain(judges, step):
    """Speaking order for one case. Randomised per case, fixed across arms.

    Holding the order fixed across arms is what makes the yoke exact: the judge
    who sees three prior numbers in `social` is the same judge, at the same
    point, who sees three numbers in `clerical`.
    """
    r = random.Random(CASCADE_SEED * 1000 + step)
    o = list(judges)
    r.shuffle(o)
    return o


def memory_block(hist):
    """Compact profile of a judge's own past decisions.

    Only completed memory epochs are summarised. Reporting the running record
    after every single case would leak the immediately preceding decision and
    turn self-memory into a one-step anchor, which is a different manipulation
    from the one this arm is meant to deliver.
    """
    n = (len(hist) // MEM_EVERY) * MEM_EVERY
    h = hist[:n]
    if not h:
        return ""
    dep = [d["sentence"] - d["mid"] for d in h]
    def gap(f):
        a = [d["sentence"] - d["mid"] for d in h if d[f] == 1]
        b = [d["sentence"] - d["mid"] for d in h if d[f] == 0]
        if not a or not b:
            return None
        return st.mean(a) - st.mean(b)
    lines = [f"You have decided {len(h)} cases in this jurisdiction so far.",
             f"Your mean sentence was {st.mean([d['sentence'] for d in h]):.1f} months.",
             f"Relative to the advisory range midpoint you have averaged "
             f"{dep and st.mean(dep):+.1f} months.",
             f"You sentenced within the advisory range in "
             f"{sum(1 for d in h if d['lo'] <= d['sentence'] <= d['hi'])} of {len(h)} cases."]
    for f, lab in (("remorse", "expressed remorse"), ("cooperation", "provided substantial assistance")):
        g = gap(f)
        if g is not None:
            lines.append(f"Where the defendant {lab}, your sentences averaged "
                         f"{g:+.1f} months relative to cases where the defendant did not.")
    prim = [d["primary"] for d in h if d["primary"]]
    if prim:
        top = max(set(prim), key=prim.count)
        lines.append(f"Your most frequently cited rationale has been {top} "
                     f"({prim.count(top)} of {len(prim)} cases).")
    return "YOUR RECORD ON THIS BENCH\n" + "\n".join(lines)


def peer_block(arm, jids, vals):
    if not vals:
        return ""
    if arm == "social":
        rows = "\n".join(f"  Judge {j} sentenced this defendant to {v} months."
                         for j, v in zip(jids, vals))
        return ("SENTENCES ALREADY ENTERED IN THIS CASE BY OTHER JUDGES OF THIS BENCH\n"
                + rows + "\nYou are deciding the same case independently.")
    if arm.startswith("tooldelta"):
        rows = "\n".join(f"  Predicted sentence {i+1}: {v} months."
                         for i, v in enumerate(vals))
        return ("STATISTICAL FORECAST FOR THIS DOCKET\n"
                "A regression model fitted to historical dispositions in this "
                "jurisdiction returns the following predicted sentences for a case "
                "with this profile.\n" + rows +
                "\nThe forecast is advisory and is not a judicial determination.")
    if arm.startswith("peerdelta"):
        rows = "\n".join(f"  Judge {j} sentenced this defendant to {v} months."
                         for j, v in zip(jids, vals))
        return ("SENTENCES ALREADY ENTERED IN THIS CASE BY OTHER JUDGES OF THIS BENCH\n"
                + rows + "\nYou are deciding the same case independently.")
    # Matched-trailer arms. The peer and forecast arms above each carry a closing
    # line the other does not, so the attribution is not their only difference.
    # These two strip both trailers, leaving the source label as the sole contrast.
    if arm.startswith("cascade"):
        rows = "\n".join(f"  Judge {j} sentenced this defendant to {v} months."
                         for j, v in zip(jids, vals))
        return ("SENTENCES ALREADY ENTERED IN THIS CASE BY OTHER JUDGES OF THIS BENCH\n"
                + rows)
    if arm.startswith("peerbare"):
        rows = "\n".join(f"  Judge {j} sentenced this defendant to {v} months."
                         for j, v in zip(jids, vals))
        return ("SENTENCES ALREADY ENTERED IN THIS CASE BY OTHER JUDGES OF THIS BENCH\n"
                + rows)
    # Length- and structure-matched to the forecast block: header, one descriptive
    # sentence, three rows. The bare peer block lacks that sentence, so the bare
    # pair is matched only at the end of the block, not through it.
    if arm.startswith("peermatch"):
        rows = "\n".join(f"  Judge {j} sentenced this defendant to {v} months."
                         for j, v in zip(jids, vals))
        return ("SENTENCES ALREADY ENTERED IN THIS CASE BY OTHER JUDGES OF THIS BENCH\n"
                "Three other judges of this jurisdiction have already entered sentences "
                "for this defendant on the present docket.\n" + rows)
    # Paraphrases of the closing instruction, to test whether the effect belongs to
    # the idea or to one string.
    if arm.startswith("parafree"):
        rows = "\n".join(f"  Judge {j} sentenced this defendant to {v} months."
                         for j, v in zip(jids, vals))
        return ("SENTENCES ALREADY ENTERED IN THIS CASE BY OTHER JUDGES OF THIS BENCH\n"
                + rows + "\nForm your own view of what this case warrants.")
    if arm.startswith("paraown"):
        rows = "\n".join(f"  Judge {j} sentenced this defendant to {v} months."
                         for j, v in zip(jids, vals))
        return ("SENTENCES ALREADY ENTERED IN THIS CASE BY OTHER JUDGES OF THIS BENCH\n"
                + rows + "\nYour sentence should reflect your own judgment of the case.")
    if arm.startswith("toolbare"):
        rows = "\n".join(f"  Predicted sentence {i+1}: {v} months."
                         for i, v in enumerate(vals))
        return ("STATISTICAL FORECAST FOR THIS DOCKET\n"
                "A regression model fitted to historical dispositions in this "
                "jurisdiction returns the following predicted sentences for a case "
                "with this profile.\n" + rows)
    # Informational-equivalence arms. The blocks above leave the peer and the
    # forecast free to differ in how much the source could know, so attribution
    # and information move together. These four state the source's information
    # in a sentence that is identical across the pair, leaving the header and the
    # row labels as the only contrast.
    if arm.startswith("peereqv"):
        rows = "\n".join(f"  Judge {j} sentenced this defendant to {v} months."
                         for j, v in zip(jids, vals))
        return ("SENTENCES ALREADY ENTERED IN THIS CASE BY OTHER JUDGES OF THIS BENCH\n"
                + EQVLINE + "\n" + rows)
    if arm.startswith("tooleqv"):
        rows = "\n".join(f"  Predicted sentence {i+1}: {v} months."
                         for i, v in enumerate(vals))
        return ("STATISTICAL FORECAST FOR THIS DOCKET\n"
                + EQVLINE + "\n" + rows)
    # The same pair with stated reliability raised for both sources at once.
    if arm.startswith("peerrel"):
        rows = "\n".join(f"  Judge {j} sentenced this defendant to {v} months."
                         for j, v in zip(jids, vals))
        return ("SENTENCES ALREADY ENTERED IN THIS CASE BY OTHER JUDGES OF THIS BENCH\n"
                + EQVLINE + " " + RELLINE + "\n" + rows)
    if arm.startswith("toolrel"):
        rows = "\n".join(f"  Predicted sentence {i+1}: {v} months."
                         for i, v in enumerate(vals))
        return ("STATISTICAL FORECAST FOR THIS DOCKET\n"
                + EQVLINE + " " + RELLINE + "\n" + rows)
    if arm.startswith("clerdelta"):
        rows = "\n".join(f"  Stored reference value {i+1}: {v} months."
                         for i, v in enumerate(vals))
        return ("DOCKETING SYSTEM RECORD\n"
                "The case-management system has attached the following stored values to "
                "this docket. They are artifacts of data entry, carry no legal "
                "significance, and are unrelated to the merits of this case.\n" + rows)
    return ""


def build_prompt(run, arm, jid, step, judges):
    global DTAB
    c = SEQ[step]
    recs = load(run)
    hist = [r for r in recs if r["arm"] == arm and r["judge"] == jid and r["ok"]]
    ng = arm.endswith("_ng")
    body = c["text_alt"] if c["phase"] == "reexposure" else c["text"]
    head = PREAMBLE.format(jid=jid)
    if ng:
        # Drop the institutional anchor.
        head = head[:head.index("Westmoor law gives you")] + NOGUIDE
    parts = [head, f"CASE FILE\n{body}"]
    parts.append(f"Statutory maximum: {c['statmax']} months." if ng else
                 f"ADVISORY RANGE: {c['lo']} to {c['hi']} months. "
                 f"Statutory maximum: {c['statmax']} months.")
    if arm in ("ownhist", "social"):
        m = memory_block(hist)
        if m:
            parts.append(m)
    if arm.startswith(("peerdelta", "tooldelta", "clerdelta", "peerbare", "toolbare",
                       "peermatch", "parafree", "paraown",
                       "peereqv", "tooleqv", "peerrel", "toolrel")):
        if DTAB is None:
            DTAB = delta_table()
        d = DTAB[(jid, c["cid"])]
        vals = anchor_values(c["mid"], d)
        ids = ["K", "R", "T"]
        parts.append(peer_block(arm, ids, vals))
    if arm.startswith("cascade"):
        order = cascade_order(judges, step)
        pos = order.index(jid)
        done = {r["judge"]: r["sentence"] for r in recs
                if r["arm"] == arm and r["step"] == step and r["ok"]}
        jj = [j for j in order[:pos] if j in done]
        vals = [done[j] for j in jj]
        b = peer_block(arm, jj, vals)
        if b:
            parts.append(b)
    if arm == "social":
        order = cascade_order(judges, step)
        pos = order.index(jid)
        if True:
            prior_j = order[:pos]
            done = {r["judge"]: r["sentence"] for r in recs
                    if r["arm"] == "social" and r["step"] == step and r["ok"]}
            jj = [j for j in prior_j if j in done]
            vals = [done[j] for j in jj]
        b = peer_block(arm, jj, vals)
        if b:
            parts.append(b)
    parts.append(FORMAT)
    return "\n\n".join(parts)


def parse(raw):
    def g(k):
        m = re.search(rf"{k}:\s*(.+)", raw or "", re.I)
        return m.group(1).strip() if m else None
    s = g("SENTENCE")
    sent = None
    if s:
        m = re.search(r"-?\d+", s.replace(",", ""))
        sent = int(m.group()) if m else None
    conf = g("CONFIDENCE")
    conf = int(re.search(r"\d+", conf).group()) if conf and re.search(r"\d+", conf) else None
    def rat(k):
        v = (g(k) or "").upper()
        for r in RATIONALES:
            if r in v:
                return r
        return None
    return {"sentence": sent, "confidence": conf, "primary": rat("PRIMARY_RATIONALE"),
            "secondary": rat("SECONDARY_RATIONALE"),
            "justification": (g("JUSTIFICATION") or "")[:400]}


def record(run, arm, jid, step, raw, model, judges, shard=""):
    c = SEQ[step]
    p = parse(raw)
    ok = p["sentence"] is not None and 0 <= p["sentence"] <= c["statmax"] * 2
    global DTAB
    peer_ids, peer_vals, delta = [], [], None
    if arm.startswith(("peerdelta", "tooldelta", "clerdelta", "peerbare", "toolbare",
                       "peermatch", "parafree", "paraown",
                       "peereqv", "tooleqv", "peerrel", "toolrel")):
        if DTAB is None:
            DTAB = delta_table()
        delta = DTAB[(jid, c["cid"])]
        peer_ids, peer_vals = ["K", "R", "T"], anchor_values(c["mid"], delta)
    elif arm.startswith("cascade"):
        order = cascade_order(judges, step)
        pos = order.index(jid)
        done = {r["judge"]: r["sentence"] for r in load(run)
                if r["arm"] == arm and r["step"] == step and r["ok"]}
        peer_ids = [j for j in order[:pos] if j in done]
        peer_vals = [done[j] for j in peer_ids]
    elif arm == "social":
        order = cascade_order(judges, step)
        pos = order.index(jid)
        done = {r["judge"]: r["sentence"] for r in load(run)
                if r["arm"] == "social" and r["step"] == step and r["ok"]}
        peer_ids = [j for j in order[:pos] if j in done]
        peer_vals = [done[j] for j in peer_ids]
    rec = {"run": run, "model": model, "arm": arm, "judge": jid, "step": step,
           "cid": c["cid"], "phase": c["phase"], "lo": c["lo"], "hi": c["hi"],
           "mid": c["mid"], "statmax": c["statmax"], "offense_type": c["offense_type"],
           "severity": c["severity"], "prior": c["prior"], "remorse": c["remorse"],
           "cooperation": c["cooperation"], "peer_ids": peer_ids, "peer_vals": peer_vals,
           "peer_mean": (st.mean(peer_vals) if peer_vals else None), "delta": delta,
           "dev": None, "text_form": ("alt" if c["phase"] == "reexposure" else "orig"),
           "ok": ok, "raw": (raw or "")[:1200], **p}
    if ok:
        rec["dev"] = (rec["sentence"] - c["mid"]) / c["mid"]
    fn = f"decisions{('.' + shard) if shard else ''}.jsonl"
    with open(f"{rundir(run)}/{fn}", "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prompt", "record", "status", "order"])
    ap.add_argument("--run", required=True)
    ap.add_argument("--arm"); ap.add_argument("--judge"); ap.add_argument("--step", type=int)
    ap.add_argument("--raw"); ap.add_argument("--model", default="")
    ap.add_argument("--shard", default="")
    ap.add_argument("--judges", default="A,B,C,D")
    a = ap.parse_args()
    js = a.judges.split(",")
    if a.cmd == "prompt":
        sys.stdout.write(build_prompt(a.run, a.arm, a.judge, a.step, js))
    elif a.cmd == "record":
        raw = a.raw if a.raw is not None else sys.stdin.read()
        r = record(a.run, a.arm, a.judge, a.step, raw, a.model, js, a.shard)
        print(json.dumps({k: r[k] for k in ("arm", "judge", "step", "cid",
                                            "sentence", "primary", "ok")}))
    elif a.cmd == "order":
        print(" ".join(cascade_order(js, a.step)))
    else:
        recs = load(a.run)
        print(json.dumps({"n": len(recs), "ok": sum(r["ok"] for r in recs),
                          "by_arm": {x: sum(1 for r in recs if r["arm"] == x) for x in ARMS}}))
