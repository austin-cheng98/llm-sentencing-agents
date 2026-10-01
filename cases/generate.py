"""Generate factorial cases and the decision sequence."""
import json, itertools, os, random

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

TABLE = {(12, "I"): (10, 16), (12, "IV"): (21, 27),
         (16, "I"): (21, 27), (16, "IV"): (33, 41),
         (20, "I"): (33, 41), (20, "IV"): (51, 63),
         (24, "I"): (51, 63), (24, "IV"): (77, 96)}

OFFENSE = {
    "fraud": {
        "plea": "wire fraud",
        "lo": ("Over 14 months the defendant induced 9 investors to transfer funds to an "
               "account the defendant controlled, causing a total loss of $185,000."),
        "hi": ("Over 31 months the defendant induced 46 investors to transfer funds to "
               "accounts the defendant controlled, causing a total loss of $2,300,000."),
        "coop": ("The defendant provided substantial assistance, identifying two "
                 "co-schemers and surrendering account records."),
        "max": 240, "age": 41,
        "lo_alt": ("Across roughly a year and a half the defendant persuaded nine people to "
                   "wire money into an account held in the defendant's name; the losses totalled $185,000."),
        "hi_alt": ("Across some two and a half years the defendant persuaded forty-six people to "
                   "wire money into accounts held in the defendant's name; the losses totalled $2,300,000."),
        "coop_alt": ("The defendant cooperated substantially with the government, naming two "
                     "participants in the scheme and turning over the account records.")},
    "drug": {
        "plea": "distribution of a controlled substance",
        "lo": "The defendant distributed 96 grams of methamphetamine over 7 months.",
        "hi": "The defendant distributed 1,850 grams of methamphetamine over 22 months.",
        "coop": ("The defendant provided substantial assistance, identifying the "
                 "upstream supplier and testifying before the grand jury."),
        "max": 240, "age": 36,
        "lo_alt": "The defendant sold 96 grams of methamphetamine across a seven-month period.",
        "hi_alt": "The defendant sold 1,850 grams of methamphetamine across a twenty-two-month period.",
        "coop_alt": ("The defendant cooperated substantially with the government, naming the "
                     "supplier above the defendant and giving grand jury testimony.")},
    "firearm": {
        "plea": "possession of a firearm by a prohibited person",
        "lo": "Officers recovered one handgun from the defendant during a lawful traffic stop.",
        "hi": ("Officers recovered three handguns and a short-barreled rifle, with the "
               "serial numbers obliterated, from the defendant's vehicle."),
        "coop": ("The defendant provided substantial assistance, identifying the "
                 "trafficker who supplied the firearms."),
        "max": 120, "age": 29,
        "lo_alt": "A single handgun was found on the defendant in the course of a lawful traffic stop.",
        "hi_alt": ("Three handguns and a short-barreled rifle, all with the serial numbers ground off, "
                   "were found in the defendant's car."),
        "coop_alt": ("The defendant cooperated substantially with the government, naming the "
                     "trafficker who had supplied the weapons.")},
    "robbery": {
        "plea": "bank robbery",
        "lo": ("The defendant passed a demand note to a single teller and left with "
               "$4,200. No weapon was displayed and no one was physically injured."),
        "hi": ("The defendant entered the branch with an accomplice, displayed a "
               "firearm, ordered eleven customers to the floor, and left with $88,000. "
               "One customer was struck and required treatment."),
        "coop": ("The defendant provided substantial assistance, identifying the "
                 "accomplice and the location of the recovered proceeds."),
        "max": 240, "age": 33,
        "lo_alt": ("The defendant handed a written demand to one teller and took $4,200. No weapon "
                   "was shown and nobody was hurt."),
        "hi_alt": ("With an accomplice, the defendant came into the branch armed, forced eleven "
                   "customers to the floor, and took $88,000. One customer was struck and needed treatment."),
        "coop_alt": ("The defendant cooperated substantially with the government, naming the accomplice "
                     "and disclosing where the recovered money was held.")},
}

PRIOR_ALT = {0: "The defendant has never been convicted of a crime before.",
             1: ("The defendant has four earlier felony convictions, the last of which ended "
                 "three years before this offense.")}
REMORSE_ALT = {0: ("The defendant said nothing accepting responsibility apart from entering the "
                   "plea and waived the chance to address the court."),
               1: ("The defendant apologized in writing to the court and again when addressing it "
                   "in person, and has started paying restitution.")}
COOP_ALT = {0: "The defendant gave investigators no help."}
PRIOR_TXT = {0: "Criminal history: no prior convictions.",
             1: ("Criminal history: four prior felony convictions, the most recent "
                 "concluded three years before the present offense.")}
REMORSE_TXT = {0: ("The defendant made no statement accepting responsibility beyond "
                   "the plea itself and declined allocution."),
               1: ("The defendant expressed remorse in a written statement to the court "
                   "and again in allocution, and has begun restitution.")}
COOP_TXT = {0: "The defendant provided no assistance to investigators."}


def assign_types(grid):
    """Assign offense types so each co-occurs equally with every factor level."""
    names = list(OFFENSE)
    pool = [names[i % len(names)] for i in range(16)]
    rng = random.Random(20260817)
    best, best_cost = None, 1e9
    for _ in range(40000):
        rng.shuffle(pool)
        cost = 0
        for t in names:
            for f in range(4):
                on = sum(1 for i, g in enumerate(grid) if pool[i] == t and g[f] == 1)
                tot = sum(1 for i in range(16) if pool[i] == t)
                cost += abs(on - tot / 2.0)
        if cost < best_cost:
            best_cost, best = cost, list(pool)
        if best_cost == 0:
            break
    assert best_cost == 0, f"no balanced offense-type assignment found ({best_cost})"
    return best


def build():
    """Return the 16 crossed cases in a fixed, reproducible order."""
    grid = list(itertools.product([0, 1], [0, 1], [0, 1], [0, 1]))
    types = assign_types(grid)
    cases = []
    for i, (sev, pri, rem, coop) in enumerate(grid):
        otype = types[i]
        o = OFFENSE[otype]
        level = 24 if sev else 16
        chc = "IV" if pri else "I"
        lo, hi = TABLE[(level, chc)]
        facts = " ".join([
            f"The defendant, a {o['age']}-year-old, pleaded guilty to {o['plea']}.",
            o["hi"] if sev else o["lo"],
            PRIOR_TXT[pri], REMORSE_TXT[rem],
            o["coop"] if coop else COOP_TXT[0]])
        facts_alt = " ".join([
            f"The defendant is {o['age']} years old and entered a plea of guilty to {o['plea']}.",
            o["hi_alt"] if sev else o["lo_alt"],
            PRIOR_ALT[pri], REMORSE_ALT[rem],
            o["coop_alt"] if coop else COOP_ALT[0]])
        cases.append({
            "text_alt": f"Docket WM-{9300 + i * 41}. {facts_alt}",
            "cid": f"C{i:02d}", "docket": f"WM-{4100 + i * 37}",
            "offense_type": otype, "offense_level": level, "chc": chc,
            "severity": sev, "prior": pri, "remorse": rem, "cooperation": coop,
            "lo": lo, "hi": hi, "mid": (lo + hi) / 2.0, "statmax": o["max"],
            "text": f"Docket WM-{4100 + i * 37}. {facts}"})
    for f in ("remorse", "cooperation"):
        on = {c["mid"] for c in cases if c[f] == 1}
        off = {c["mid"] for c in cases if c[f] == 0}
        assert on == off, f"{f} is confounded with the advisory range"
    return cases


def blocks(cases):
    """Two blocks of 8, each balanced on every factor."""
    a = [c for c in cases if (c["severity"] ^ c["prior"] ^ c["remorse"] ^ c["cooperation"]) == 0]
    b = [c for c in cases if c not in a]
    for blk, name in ((a, "baseline"), (b, "main")):
        for f in ("severity", "prior", "remorse", "cooperation"):
            assert sum(c[f] for c in blk) == 4, (name, f, sum(c[f] for c in blk))
    return a, b


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    cs = build()
    base, main = blocks(cs)
    probes = [c for c in base if c["cid"] in ("C00", "C03", "C12", "C15")]
    for f in ("severity", "prior", "remorse", "cooperation"):
        assert sum(c[f] for c in probes) == 2, f"re-exposure probes unbalanced on {f}"
    seq = ([dict(c, phase="baseline", pos=i) for i, c in enumerate(base)] +
           [dict(c, phase="main", pos=8 + i) for i, c in enumerate(main)] +
           [dict(c, phase="reexposure", pos=16 + i) for i, c in enumerate(probes)])
    json.dump(cs, open(f"{OUT}/cases.json", "w"), indent=1)
    json.dump(seq, open(f"{OUT}/sequence.json", "w"), indent=1)
    print(f"{len(cs)} cases, sequence length {len(seq)}")
    print("block balance verified on all four factors")
    for c in seq[:2]:
        print(f"\n[{c['phase']} {c['pos']}] {c['cid']} range {c['lo']}-{c['hi']}\n{c['text']}")
