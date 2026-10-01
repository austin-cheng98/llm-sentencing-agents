"""Randomization inference by permuting the displacement allocation.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "experiment"))
from common import load, ols, factor_matrix, PRIMARY, ROOT
import harness as H


def case_groups():
    """The four factor-balanced groups the displacement was assigned over."""
    tab = H.delta_table()
    cases = [c for c in H.SEQ if c["phase"] in ("baseline", "main")]
    g = {}
    for c in cases:
        g.setdefault(tab[("P1", c["cid"])], []).append(c["cid"])
    return list(g.values())


def ri_pull(recs, arm, B=9999, seed=11):
    d = [r for r in recs if r["arm"] == arm]
    if len(d) < 20:
        return None
    grps = case_groups()
    cid2g = {c: i for i, gg in enumerate(grps) for c in gg}
    y = np.array([r["dev"] for r in d])
    F = factor_matrix(d)
    gi = np.array([cid2g[r["cid"]] for r in d])
    ju = np.array([r["judge"] for r in d])

    def slope(dv):
        return ols(np.column_stack([np.ones(len(y)), dv, F]), y)[1]

    obs = slope(np.array([r["delta"] for r in d]))
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(B):
        perm = np.empty(len(y))
        for j in np.unique(ju):
            m = ju == j
            lv = rng.permutation(H.DELTAS)
            perm[m] = [lv[k] for k in gi[m]]
        if abs(slope(perm)) >= abs(obs) - 1e-12:
            cnt += 1
    return {"est": float(obs), "p": (cnt + 1) / (B + 1), "n": len(d)}


def ri_premium(recs, suf="", B=9999, seed=13):
    """Sharp null on attribution: swap labels within a cell."""
    d = [r for r in recs if r["arm"] in (f"peerdelta{suf}", f"tooldelta{suf}")]
    y = np.array([r["dev"] for r in d])
    dl = np.array([r["delta"] for r in d])
    F = factor_matrix(d)
    peer = np.array([1.0 if r["arm"].startswith("peer") else 0.0 for r in d])
    cell = np.array([f"{r['judge']}|{r['cid']}" for r in d])

    def prem(pv):
        return ols(np.column_stack([np.ones(len(y)), dl, pv, dl * pv, F]), y)[3]

    obs = prem(peer)
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(B):
        pv = peer.copy()
        for c in np.unique(cell):
            m = cell == c
            if m.sum() > 1 and rng.random() < 0.5:
                pv[m] = 1.0 - pv[m]
        if abs(prem(pv)) >= abs(obs) - 1e-12:
            cnt += 1
    return {"est": float(obs), "p": (cnt + 1) / (B + 1), "n": len(d)}


def main():
    recs = [r for r in load(model=PRIMARY) if r.get("delta") is not None]
    out = {"pull": {}, "premium": {}}
    for arm in ("peerdelta", "tooldelta", "peerdelta_ng", "tooldelta_ng", "clerdelta_ng"):
        r = ri_pull(recs, arm)
        if r:
            out["pull"][arm] = r
            print(f"  {arm:15s} pull={r['est']:+.3f}  p={r['p']:.4f}  n={r['n']}")
    for suf, lab in (("", "guideline"), ("_ng", "no guideline")):
        r = ri_premium(recs, suf)
        out["premium"][lab] = r
        print(f"  premium, {lab:14s} {r['est']:+.3f}  p={r['p']:.4f}  n={r['n']}")
    json.dump(out, open(f"{ROOT}/analysis/out_randomization.json", "w"), indent=1)


if __name__ == "__main__":
    main()
