"""Civil-damages transfer of the sentencing anchoring design.

The sentencing experiment asks whether an agent's pull toward displayed numbers
depends on what those numbers are said to be. This module runs the same
question on a second task: setting a monetary damages award on a civil claim
file. Nothing about the estimator changes. The outcome is the award's
proportional deviation from the advisory midpoint, the regressor is the
proportional displacement of the displayed figures, and the estimand is the
difference in slopes between the peer-attributed and model-attributed arms.

Two design choices are carried over deliberately. The advisory range is removed
in every arm, so no pull can be attributed to an institutional anchor the agent
is deferring to. And both primary arms carry a word-for-word identical sentence
stating that the displayed figures were derived from the same file and from
nothing else, which closes the reading that peer figures are simply more
informative than a model's. In the damages setting that reading is live in a way
it is not in sentencing, because comparable awards are arguably admissible
evidence, so the equivalence cue is in the primary arms rather than a follow-up.

Arms
  dpeer_ng      peer-attributed figures, structure-matched block, equivalence cue
  dtool_ng      model-attributed figures, structure-matched block, equivalence cue
  dpeerbare_ng  peer-attributed, header and rows only
  dtoolbare_ng  model-attributed, header and rows only

The first pair is the confirmatory comparison. The second is secondary and
tests whether the premium survives stripping the descriptive sentence and the
equivalence cue from both sides.
"""
import argparse, hashlib, json, os, random, re, statistics as st, sys

ROOT = os.path.expanduser("~/judicial-drift")
CLAIMS = json.load(open(f"{ROOT}/cases/claims.json"))
ARMS = ["dpeer_ng", "dtool_ng", "dpeerbare_ng", "dtoolbare_ng"]
PRIMARY_ARMS = ("dpeer_ng", "dtool_ng")
SECONDARY_ARMS = ("dpeerbare_ng", "dtoolbare_ng")
DELTAS = [-0.30, -0.15, 0.15, 0.30]
AGENTS = [f"A{i:02d}" for i in range(1, 13)]
FACTORS = ("severity", "liability", "mitigation", "documentation")
RATIONALES = ["ECONOMIC_LOSS", "PAIN_AND_SUFFERING", "COMPARABILITY",
              "LIABILITY_RISK", "PROPORTIONALITY", "EQUITY"]
ANCHOR_IDS = ("K", "R", "T")
MANIFEST_SEED = 20261003

PREAMBLE = (
 "This is a controlled research simulation studying how language-model agents make "
 "repeated decisions. Every claim in this study is entirely fictional and was "
 "procedurally generated for the simulation. No real claimant, defendant, insurer, "
 "claim, or jurisdiction is involved. Your output is a data point in a behavioral "
 "experiment, not legal advice, not a valuation opinion, and not a real settlement "
 "decision.\n\n"
 "You are Adjuster {aid}, a senior claims adjuster in the fictional jurisdiction of "
 "Westmoor. You resolve bodily-injury claims and enter a single settlement valuation "
 "for each file.")

NOGUIDE = (
 "Westmoor practice sets no advisory valuation range for claims of this type. You may "
 "enter any amount from $0 to the policy limit, according to your own judgment of what "
 "the file warrants.")

EQVLINE = (
 "These figures were produced from the same claim file you have been given, and from "
 "no other information about this claimant or this incident.")

FORMAT = (
 "Enter the settlement valuation. Respond in exactly this format, with no other text:\n"
 "AWARD: <integer> DOLLARS\n"
 "CONFIDENCE: <integer 1-10>\n"
 "PRIMARY_RATIONALE: <exactly one of " + ", ".join(RATIONALES) + ">\n"
 "SECONDARY_RATIONALE: <exactly one of the same six words, or NONE>\n"
 "JUSTIFICATION: <at most two sentences>")


def delta_table():
    """Assign a displacement to every (agent, claim) cell.

    Identical in construction to the sentencing table: the sixteen design
    points are partitioned by backtracking into four groups that are each
    balanced on all four binary factors, and the group-to-displacement mapping
    is rotated across agents. Without this, an estimated pull toward the
    displayed figures could absorb part of a factor effect.
    """
    idx = list(range(len(CLAIMS)))
    groups = []

    def balanced(grp):
        return all(sum(CLAIMS[i][f] for i in grp) == 2 for f in FACTORS)

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

    if not search(idx):
        raise RuntimeError("no factor-balanced partition of the design points exists")

    tab = {}
    for ax, agent in enumerate(AGENTS):
        for g, grp in enumerate(groups):
            for i in grp:
                tab[(agent, CLAIMS[i]["cid"])] = DELTAS[(g + ax) % len(DELTAS)]
    for f in FACTORS:
        for d in DELTAS:
            cell = [c[f] for c in CLAIMS for a in AGENTS
                    if tab[(a, c["cid"])] == d]
            assert abs(sum(cell) / len(cell) - 0.5) < 1e-9, (f, d)
    return tab


DTAB = delta_table()


def anchor_values(mid, delta):
    """Three figures whose mean sits exactly at the displaced midpoint.

    Rounded to the nearest hundred dollars. A coarser grid would put the
    displayed figures on the same round values that agents gravitate to on
    their own, which would confound displacement with roundness.
    """
    t = mid * (1.0 + delta)
    return [int(round(t * 0.94 / 100.0) * 100),
            int(round(t / 100.0) * 100),
            int(round(t * 1.06 / 100.0) * 100)]


def claim(step):
    return CLAIMS[step]


def anchor_block(arm, vals):
    if arm.startswith("dpeer"):
        rows = "\n".join(f"  Adjuster {j} valued this claim at ${v:,}."
                         for j, v in zip(ANCHOR_IDS, vals))
        head = "VALUATIONS ALREADY ENTERED ON THIS FILE BY OTHER ADJUSTERS OF THIS UNIT"
        desc = ("Three other adjusters in this unit have already entered valuations for "
                "this claimant on the present file.")
    else:
        rows = "\n".join(f"  Predicted valuation {i + 1}: ${v:,}."
                         for i, v in enumerate(vals))
        head = "VALUATION MODEL OUTPUT FOR THIS FILE"
        desc = ("A regression model fitted to historical settlements in this "
                "jurisdiction returns the following predicted valuations for a claim "
                "with this profile.")
    if arm in PRIMARY_ARMS:
        return "\n".join([head, desc, EQVLINE, rows])
    return "\n".join([head, rows])


def build_prompt(arm, agent, step):
    if arm not in ARMS:
        raise SystemExit(f"unknown arm {arm}")
    c = claim(step)
    vals = anchor_values(c["mid"], DTAB[(agent, c["cid"])])
    parts = [PREAMBLE.format(aid=agent) + " " + NOGUIDE,
             f"CLAIM FILE\n{c['text']}",
             f"Policy limit: ${c['limit']:,}.",
             anchor_block(arm, vals),
             FORMAT]
    return "\n\n".join(parts)


def parse(raw):
    def g(k):
        m = re.search(rf"{k}:\s*(.+)", raw or "", re.I)
        return m.group(1).strip() if m else None
    s = g("AWARD")
    award = None
    if s:
        m = re.search(r"-?[\d,]+", s)
        if m:
            try:
                award = int(m.group().replace(",", ""))
            except ValueError:
                award = None
    conf = g("CONFIDENCE")
    conf = int(re.search(r"\d+", conf).group()) if conf and re.search(r"\d+", conf) else None

    def rat(k):
        v = (g(k) or "").upper()
        for r in RATIONALES:
            if r in v:
                return r
        return None
    return {"award": award, "confidence": conf, "primary": rat("PRIMARY_RATIONALE"),
            "secondary": rat("SECONDARY_RATIONALE"),
            "justification": (g("JUSTIFICATION") or "")[:400]}


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


def record(run, arm, agent, step, raw, model, shard=""):
    c = claim(step)
    p = parse(raw)
    ok = p["award"] is not None and 0 <= p["award"] <= c["limit"] * 2
    delta = DTAB[(agent, c["cid"])]
    vals = anchor_values(c["mid"], delta)
    rec = {"run": run, "domain": "damages", "model": model, "arm": arm,
           "judge": agent, "step": step, "cid": c["cid"],
           "claim_type": c["claim_type"], "lo": c["lo"], "hi": c["hi"],
           "mid": c["mid"], "limit": c["limit"],
           **{f: c[f] for f in FACTORS},
           "anchor_ids": list(ANCHOR_IDS), "anchor_vals": vals,
           "anchor_mean": st.mean(vals), "delta": delta, "dev": None,
           "ok": ok, "raw": (raw or "")[:1200],
           "prompt_sha256": hashlib.sha256(
               build_prompt(arm, agent, step).encode()).hexdigest(), **p}
    if ok:
        rec["dev"] = (p["award"] - c["mid"]) / c["mid"]
    fn = f"decisions{('.' + shard) if shard else ''}.jsonl"
    with open(f"{rundir(run)}/{fn}", "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def init_manifest(run):
    d = rundir(run)
    path = f"{d}/manifest.jsonl"
    if os.path.exists(path):
        raise SystemExit("manifest exists; refusing to overwrite it")
    tasks = []
    for arm in ARMS:
        for agent in AGENTS:
            for step in range(len(CLAIMS)):
                text = build_prompt(arm, agent, step)
                tasks.append({"arm": arm, "judge": agent, "step": step,
                              "cid": CLAIMS[step]["cid"],
                              "primary": arm in PRIMARY_ARMS,
                              "prompt_sha256": hashlib.sha256(
                                  text.encode()).hexdigest()})
    random.Random(MANIFEST_SEED).shuffle(tasks)
    with open(path, "w") as f:
        for i, t in enumerate(tasks):
            t["task"] = i + 1
            f.write(json.dumps(t) + "\n")
    print(f"wrote {len(tasks)} tasks "
          f"({sum(t['primary'] for t in tasks)} primary) to {path}")
    print("manifest SHA-256:", hashlib.sha256(open(path, 'rb').read()).hexdigest())


def todo(run, arm, agent):
    have = {r["step"] for r in load(run)
            if r["arm"] == arm and r["judge"] == agent and r["ok"]}
    print(" ".join(str(s) for s in range(len(CLAIMS)) if s not in have))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prompt", "record", "status", "init", "todo"])
    ap.add_argument("--run", default="D1")
    ap.add_argument("--arm"); ap.add_argument("--judge"); ap.add_argument("--step", type=int)
    ap.add_argument("--raw"); ap.add_argument("--model", default="")
    ap.add_argument("--shard", default="")
    a = ap.parse_args()
    if a.cmd == "prompt":
        sys.stdout.write(build_prompt(a.arm, a.judge, a.step))
    elif a.cmd == "record":
        raw = a.raw if a.raw is not None else sys.stdin.read()
        r = record(a.run, a.arm, a.judge, a.step, raw, a.model, a.shard)
        print(json.dumps({k: r[k] for k in ("arm", "judge", "step", "cid",
                                            "award", "primary", "ok")}))
    elif a.cmd == "init":
        init_manifest(a.run)
    elif a.cmd == "todo":
        todo(a.run, a.arm, a.judge)
    else:
        recs = load(a.run)
        print(json.dumps({"n": len(recs), "ok": sum(r["ok"] for r in recs),
                          "by_arm": {x: sum(1 for r in recs if r["arm"] == x)
                                     for x in ARMS}}, indent=1))
