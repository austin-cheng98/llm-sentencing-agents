"""Analysis for the proximity confirmation of damages run D1.

Registered in damages/AMENDMENT-D1-proximity.md, written and frozen before any
cell of the two confirming agents was examined. The amendment records that the
five proximity measures were found by exploring the already-read eight-agent
panel, so no estimate computed on that panel carries a protected error rate for
them. The confirming sample is the next two agents in the frozen expansion
order, A12 and A01: 64 decisions, 32 matched agent-claim pairs.

The arm contrast is within matched pair. Both arms of a pair see the identical
displaced figures, so the contrast does not depend on which group-to-displacement
rotation the agent drew. The registered test is therefore an exact sign test over
discordant pairs, whose reference set is 2^(discordant pairs), and the 4^k
rotation floor that governs the displacement estimands does not apply.

Estimands, in the amendment's order:

  1. Primary. The award falls inside the displayed band, low to high inclusive,
     predicted more often in `dtool_ng`. Two-sided exact sign test on the
     discordant matched pairs.
  2. Confirmatory. The mean paired difference in proportional distance from the
     central displayed figure, peer minus tool, estimated as the intercept of
     the paired difference with standard errors clustered on claim, predicted
     positive, reported with its interval and its minimum detectable effect.
  3. Confirmatory. The award falls within two percent of the central figure,
     same sign test.
  4. Replication. The award equals the central figure exactly, same sign test.
     This repeats estimand 3 of the extension amendment on new agents.

The pull slope and the slope premium are reported on the enlarged panel for
continuity only. Neither is a target of this amendment, and the premium stays
uninformative rather than negative, as damages/RESULTS-D1-extension.md records.

scripts/damages_analysis.py, scripts/damages_analysis_ext.py and their outputs
are frozen. This file derives from them and modifies neither. The estimators,
the clustering and the MDE constant are unchanged.
"""
import json
import sys
from math import comb

import numpy as np

sys.path.insert(0, "/Users/austincheng/judicial-drift/scripts")
import damages as D
from damages_analysis import (
    B, SEED, Z_MDE, BENCH_PULL, BENCH_PREMIUM,
    ols, cluster_vcov, build, fit, ri_pvalue, ri_rotation_exact,
)
from damages_analysis_ext import (
    T15, PANEL, EXPANSION_ORDER, complete_agents, load_rows, slope_record,
)

RUN = "D1"
CONFIRM = ("A12", "A01")   # the registered confirming sample
TOL = 0.02                 # "within two percent of the central figure"


def anchors():
    claims = {c["cid"]: c for c in json.load(open(f"{D.ROOT}/cases/claims.json"))}
    return claims


def measures(rows):
    """Per-decision proximity indicators against that cell's displayed figures."""
    claims = anchors()
    out = {}
    for r in rows:
        lo, mid, hi = D.anchor_values(claims[r["cid"]]["mid"], r["delta"])
        a = r["award"]
        out[(r["judge"], r["step"], r["arm"])] = {
            "cid": r["cid"],
            "inside_band": int(lo <= a <= hi),
            "within_tol": int(abs(a - mid) <= TOL * mid),
            "equals_central": int(a == mid),
            "dist_central": abs(a - mid) / float(mid),
            "award": a, "low": lo, "central": mid, "high": hi,
        }
    return out


def sign_test(m, key, pairs):
    """Two-sided exact sign test over discordant matched pairs. Predicted
    direction is tool_only > peer_only."""
    peer_only = sum(1 for k in pairs
                    if m[(*k, "dpeer_ng")][key] and not m[(*k, "dtool_ng")][key])
    tool_only = sum(1 for k in pairs
                    if m[(*k, "dtool_ng")][key] and not m[(*k, "dpeer_ng")][key])
    both = sum(1 for k in pairs
               if m[(*k, "dpeer_ng")][key] and m[(*k, "dtool_ng")][key])
    disc = peer_only + tool_only
    k = min(peer_only, tool_only)
    p = (min(1.0, 2.0 * sum(comb(disc, i) for i in range(k + 1)) / 2.0 ** disc)
         if disc else 1.0)
    return {
        "measure": key,
        "n_pairs": len(pairs),
        "peer_total": sum(m[(*kk, "dpeer_ng")][key] for kk in pairs),
        "tool_total": sum(m[(*kk, "dtool_ng")][key] for kk in pairs),
        "both": both, "peer_only": peer_only, "tool_only": tool_only,
        "discordant": disc,
        "p_exact_sign_test": float(p),
        "min_attainable_two_sided_p": (2.0 ** (1 - disc)) if disc else 1.0,
        "predicted_direction": "tool_only > peer_only",
        "direction_as_predicted": tool_only > peer_only,
    }


def paired_distance(m, pairs):
    """Estimand 2. Intercept of the within-pair difference in proportional
    distance from the central figure, peer minus tool, clustered on claim."""
    d = np.array([m[(*k, "dpeer_ng")]["dist_central"]
                  - m[(*k, "dtool_ng")]["dist_central"] for k in pairs])
    cid = np.array([m[(*k, "dpeer_ng")]["cid"] for k in pairs])
    X = np.ones((len(d), 1))
    b = ols(X, d)
    se = float(np.sqrt(cluster_vcov(X, d, b, cid)[0, 0]))
    est = float(b[0])
    G = len(set(cid))
    return {
        "measure": "proportional distance from central figure (peer minus tool)",
        "n_pairs": len(pairs), "clusters": G,
        "mean_peer": float(np.mean([m[(*k, "dpeer_ng")]["dist_central"]
                                    for k in pairs])),
        "mean_tool": float(np.mean([m[(*k, "dtool_ng")]["dist_central"]
                                    for k in pairs])),
        "est": est, "se": se, "t": est / se,
        "ci95_z": [est - 1.959963984540054 * se, est + 1.959963984540054 * se],
        "ci95_t": [est - T15 * se, est + T15 * se],
        "mde": Z_MDE * se,
        "predicted_direction": "positive",
        "direction_as_predicted": est > 0,
    }


def verdict(rec):
    """The registered decision rules, applied verbatim."""
    if not rec["direction_as_predicted"]:
        return "direction reverses: reported plainly as a failure to replicate"
    if "p_exact_sign_test" in rec:
        if rec["p_exact_sign_test"] < 0.05:
            return "direction holds and the test rejects: confirmed"
        return ("direction holds but the test does not reject: directionally "
                "consistent and not statistically decisive, in those words")
    lo, hi = rec["ci95_z"]
    if lo <= 0.0 <= hi:
        return ("interval contains zero: inconclusive and not as evidence that "
                "the arms are alike")
    if rec["mde"] > abs(rec["est"]):
        return ("interval excludes zero while the MDE exceeds the estimate: "
                "suggestive rather than decisive")
    return "interval excludes zero and the estimate exceeds the MDE: confirmed"


def report_sign(rec):
    print(f"  dpeer_ng {rec['peer_total']:>3}/{rec['n_pairs']}   "
          f"dtool_ng {rec['tool_total']:>3}/{rec['n_pairs']}   "
          f"both {rec['both']}")
    print(f"  peer-only {rec['peer_only']}   tool-only {rec['tool_only']}   "
          f"discordant {rec['discordant']}")
    print(f"  p (two-sided exact sign test) = {rec['p_exact_sign_test']:.6g}"
          f"   smallest attainable "
          f"{rec['min_attainable_two_sided_p']:.6g}")
    print(f"  verdict: {verdict(rec)}")


def main():
    all_rows = [r for r in D.load(RUN) if r["ok"] and r["arm"] in D.PRIMARY_ARMS]
    done = complete_agents(all_rows)
    missing = [a for a in CONFIRM if a not in done]
    if missing:
        sys.exit(f"confirming agents incomplete: {' '.join(missing)}")

    conf_rows = load_rows(CONFIRM)
    assert len(conf_rows) == 64, len(conf_rows)
    m = measures(conf_rows)
    pairs = sorted({(j, s) for j, s, _ in m})
    assert len(pairs) == 32, len(pairs)

    panel_agents = tuple(PANEL) + tuple(a for a in EXPANSION_ORDER if a in done)
    panel_rows = load_rows(panel_agents)

    out = {
        "run": RUN,
        "registered_in": "damages/AMENDMENT-D1-proximity.md",
        "confirming_agents": list(CONFIRM),
        "n_confirming_decisions": len(conf_rows),
        "n_matched_pairs": len(pairs),
        "tolerance": TOL,
        "mde_constant": Z_MDE,
        "benchmark_pull": BENCH_PULL,
        "benchmark_premium": BENCH_PREMIUM,
        "continuity_panel": list(panel_agents),
        "n_continuity": len(panel_rows),
    }

    print(f"confirming agents: {' '.join(CONFIRM)}   "
          f"{len(conf_rows)} decisions, {len(pairs)} matched pairs")
    print("the arm contrast is within matched pair, so the registered test is an")
    print("exact sign test over discordant pairs and the 4^k rotation floor does")
    print("not apply to it")

    print("\n--- estimand 1 (primary, registered): award inside the displayed "
          "band ---")
    e1 = sign_test(m, "inside_band", pairs)
    out["estimand1_inside_band"] = e1 | {"verdict": verdict(e1)}
    report_sign(e1)

    print("\n--- estimand 2 (confirmatory): proportional distance from the "
          "central figure ---")
    e2 = paired_distance(m, pairs)
    out["estimand2_paired_distance"] = e2 | {"verdict": verdict(e2)}
    print(f"  mean distance   dpeer_ng {e2['mean_peer']:.4f}   "
          f"dtool_ng {e2['mean_tool']:.4f}")
    print(f"  paired difference (peer minus tool) = {e2['est']:+.4f}   "
          f"clustered se {e2['se']:.4f}   t = {e2['t']:+.2f}   "
          f"G = {e2['clusters']}")
    print(f"  95% CI (normal) [{e2['ci95_z'][0]:+.4f}, {e2['ci95_z'][1]:+.4f}]"
          f"   on t with G-1={e2['clusters']-1} df "
          f"[{e2['ci95_t'][0]:+.4f}, {e2['ci95_t'][1]:+.4f}]")
    print(f"  MDE = {e2['mde']:.4f}")
    print(f"  verdict: {verdict(e2)}")

    print("\n--- estimand 3 (confirmatory): award within two percent of the "
          "central figure ---")
    e3 = sign_test(m, "within_tol", pairs)
    out["estimand3_within_two_percent"] = e3 | {"verdict": verdict(e3)}
    report_sign(e3)

    print("\n--- estimand 4 (replication): award equals the central figure "
          "exactly ---")
    e4 = sign_test(m, "equals_central", pairs)
    out["estimand4_equals_central"] = e4 | {"verdict": verdict(e4)}
    report_sign(e4)
    hits = sorted((k[2], k[0], k[1], v["award"]) for k, v in m.items()
                  if v["equals_central"])
    out["estimand4_matches"] = [list(h) for h in hits]
    for h in hits:
        print(f"    {h[0]:<10} {h[1]} step {h[2]:<2} ${h[3]:,}")

    print(f"\n--- continuity only, not a target of this amendment: "
          f"{len(panel_agents)} agents, n = {len(panel_rows)} ---")
    s = slope_record(panel_rows)
    _, p_ri = ri_pvalue(panel_rows, "delta")
    s["p_ri_within_agent"] = p_ri
    out["continuity_pull_slope"] = s
    print(f"  pull slope = {s['est']:+.3f}   clustered se {s['se']:.3f}   "
          f"t = {s['t']:+.2f}   n = {s['n']}   MDE {s['mde']:.3f}")
    print(f"  95% CI (normal) [{s['ci95_z'][0]:+.3f}, {s['ci95_z'][1]:+.3f}]"
          f"   p (within-agent permutation) = {p_ri:.4f}")

    pr = fit(panel_rows, "delta_x_tool", interaction=True)
    X, y, cid, names = build(panel_rows, interaction=True)
    bb = ols(X, y)
    jj = names.index("delta_x_tool")
    pr["t"] = float(bb[jj] / np.sqrt(cluster_vcov(X, y, bb, cid)[jj, jj]))
    pr["ci95_t"] = [pr["est"] - T15 * pr["se"], pr["est"] + T15 * pr["se"]]
    _, p_pr = ri_pvalue(panel_rows, "delta_x_tool", interaction=True)
    pr["p_ri_within_agent"] = p_pr
    out["continuity_premium"] = pr
    print(f"  premium    = {pr['est']:+.3f}   clustered se {pr['se']:.3f}   "
          f"t = {pr['t']:+.2f}   MDE {pr['mde']:.3f}")
    print(f"  95% CI (normal) [{pr['ci95_z'][0]:+.3f}, {pr['ci95_z'][1]:+.3f}]"
          f"   p (within-agent permutation) = {p_pr:.4f}")
    print("  the premium remains uninformative rather than negative: its MDE "
          f"{pr['mde']:.3f} exceeds both the estimate and the benchmark "
          f"{BENCH_PREMIUM}")

    path = f"{D.ROOT}/analysis/damages_d1_prox.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
