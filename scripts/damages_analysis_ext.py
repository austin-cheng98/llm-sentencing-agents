"""Analysis for the agent expansion of damages run D1.

Registered in damages/AMENDMENT-D1-extension.md, which was written after the
128-decision panel was complete and its result had been read. The amendment
records that ordering and does not claim a protected error rate for any estimate
that pools the original panel with the new agents.

Estimands, in the amendment's order:

  1. Primary. The pooled pull slope on the NEW AGENTS ONLY. These agents were
     never inspected before the amendment was registered, their rotations are
     independent of the original panel's, and the specification was fixed before
     the first new draw. The registered p-value is the design-exact randomization
     test over the 4^(new agents) group-to-displacement rotations.
  2. The pooled slope on all agents. This is the most precise summary of the
     collected decisions. Its Type I error rate is not protected, because the
     decision to extend was taken after reading the panel result, so its
     p-value is descriptive.
  3. Confirmatory, promoted from exploration. Exact matches to the central
     displayed figure occur in `dtool_ng` and not in `dpeer_ng`, tested by a
     two-sided exact sign test on the discordant matched agent-claim pairs of
     the new agents.
  4. Secondary. The premium (the `delta x arm` interaction), reported with its
     interval and its minimum detectable effect, and not interpreted as either
     a replication or a null.

scripts/damages_analysis.py and analysis/damages_d1.json are frozen by
damages/FREEZE-D1-extension.txt. This file derives from that script and does not
modify it or its output. The estimators, the clustering, the randomization
procedure and the MDE constant are unchanged.
"""
import itertools
import json
import sys
from math import comb

import numpy as np

sys.path.insert(0, "/Users/austincheng/judicial-drift/scripts")
import damages as D
from damages_analysis import (
    B, SEED, Z_MDE, BENCH_PULL, BENCH_PREMIUM,
    ols, cluster_vcov, wild_bootstrap, build, fit, ri_pvalue,
    ri_rotation_exact,
)

T15 = 2.131449545559323  # t_{0.975} on G - 1 = 15 degrees of freedom

RUN = "D1"
PANEL = ("A02", "A05", "A08", "A10")            # the original, already-read panel
EXPANSION_ORDER = ("A11", "A04", "A07", "A09",  # frozen before any collection
                   "A12", "A01", "A03", "A06")


def complete_agents(rows):
    """Agents with all 32 primary-arm cells. Only whole agents enter the panel,
    so every stopping point is exactly balanced on displacement and on all four
    case factors."""
    have = {}
    for r in rows:
        have.setdefault(r["judge"], set()).add((r["arm"], r["step"]))
    return [a for a in EXPANSION_ORDER if len(have.get(a, ())) == 32]


def load_rows(agents):
    rows = [r for r in D.load(RUN)
            if r["ok"] and r["judge"] in agents and r["arm"] in D.PRIMARY_ARMS]
    rows.sort(key=lambda r: (r["arm"], r["judge"], r["step"]))
    return rows


def exact_match_test(rows):
    """Estimand 3. A matched sign test over agent-claim pairs, which is the unit
    the design matches on: both arms of a pair see the same displaced figures."""
    claims = {c["cid"]: c for c in json.load(open(f"{D.ROOT}/cases/claims.json"))}
    hit = {}
    for r in rows:
        central = D.anchor_values(claims[r["cid"]]["mid"], r["delta"])[1]
        hit[(r["judge"], r["step"], r["arm"])] = int(r["award"] == central)
    pairs = sorted({(j, s) for j, s, _ in hit})
    peer_only = sum(1 for k in pairs
                    if hit[(*k, "dpeer_ng")] and not hit[(*k, "dtool_ng")])
    tool_only = sum(1 for k in pairs
                    if hit[(*k, "dtool_ng")] and not hit[(*k, "dpeer_ng")])
    both = sum(1 for k in pairs
               if hit[(*k, "dpeer_ng")] and hit[(*k, "dtool_ng")])
    disc = peer_only + tool_only
    k = min(peer_only, tool_only)
    p = (min(1.0, 2.0 * sum(comb(disc, i) for i in range(k + 1)) / 2.0 ** disc)
         if disc else 1.0)
    matches = sorted((r["arm"], r["judge"], r["step"], r["award"]) for r in rows
                     if hit[(r["judge"], r["step"], r["arm"])])
    return {
        "n_pairs": len(pairs),
        "peer_total": sum(v for (_, _, a), v in hit.items() if a == "dpeer_ng"),
        "tool_total": sum(v for (_, _, a), v in hit.items() if a == "dtool_ng"),
        "both": both, "peer_only": peer_only, "tool_only": tool_only,
        "discordant": disc,
        "p_exact_sign_test": float(p),
        "predicted_direction": "tool_only > peer_only",
        "direction_as_predicted": tool_only > peer_only,
        "matches": [list(m) for m in matches],
    }


def rotation_floor(k):
    """Smallest attainable two-sided p in a design-exact test over 4^k rotations."""
    return 1.0 / (len(D.DELTAS) ** k)


def report_slope(tag, rec):
    print(f"  slope = {rec['est']:+.3f}   clustered se {rec['se']:.3f}   "
          f"t = {rec['t']:+.2f}   G = {rec['clusters']}   n = {rec['n']}")
    print(f"  95% CI (normal) [{rec['ci95_z'][0]:+.3f}, {rec['ci95_z'][1]:+.3f}]"
          f"   on t with G-1={rec['clusters']-1} df "
          f"[{rec['ci95_t'][0]:+.3f}, {rec['ci95_t'][1]:+.3f}]")
    print(f"  MDE = {rec['mde']:.3f}   benchmark (sentencing, no guideline) "
          f"= {BENCH_PULL:.2f}")


def slope_record(rows, **kw):
    rec = fit(rows, "delta", **kw)
    X, y, cid, names = build(rows, **kw)
    b = ols(X, y)
    j = names.index("delta")
    rec["t"] = float(b[j] / np.sqrt(cluster_vcov(X, y, b, cid)[j, j]))
    rec["ci95_t"] = [rec["est"] - T15 * rec["se"], rec["est"] + T15 * rec["se"]]
    return rec


def main():
    all_rows = [r for r in D.load(RUN) if r["ok"] and r["arm"] in D.PRIMARY_ARMS]
    new_agents = tuple(a for a in complete_agents(all_rows) if a not in PANEL)
    k = len(new_agents)
    agents = tuple(PANEL) + new_agents

    new_rows = load_rows(new_agents)
    pooled_rows = load_rows(agents)
    assert len(new_rows) == 32 * k, len(new_rows)
    assert len(pooled_rows) == 32 * len(agents), len(pooled_rows)

    floor_new = rotation_floor(k)
    out = {
        "run": RUN,
        "original_panel": list(PANEL),
        "new_agents": list(new_agents),
        "expansion_order": list(EXPANSION_ORDER),
        "n_new": len(new_rows),
        "n_all": len(pooled_rows),
        "rotation_set_new": len(D.DELTAS) ** k,
        "rotation_set_all": len(D.DELTAS) ** len(agents),
        "min_attainable_two_sided_p_new": floor_new,
        "registered_rule_reachable": floor_new < 0.05,
        "benchmark_pull": BENCH_PULL,
        "benchmark_premium": BENCH_PREMIUM,
        "mde_constant": Z_MDE,
    }

    print(f"original panel: {' '.join(PANEL)}   (complete, already read)")
    print(f"new agents:     {' '.join(new_agents)}   ({k} of 8 in the frozen "
          f"expansion order)")
    print(f"new-agents-only sample: {len(new_rows)} decisions, "
          f"design randomization set 4^{k} = {len(D.DELTAS) ** k}")
    print(f"all-agents sample:      {len(pooled_rows)} decisions, "
          f"4^{len(agents)} = {len(D.DELTAS) ** len(agents)}")
    print(f"smallest attainable two-sided p in the registered test: "
          f"1/{len(D.DELTAS) ** k} = {floor_new:.4f}")
    if floor_new >= 0.05:
        print("  THE REGISTERED DECISION RULE CANNOT REJECT AT THIS PANEL SIZE. "
              "No new-agents result below is capable of meeting it, whatever the "
              "data show.")
    else:
        print("  The registered decision rule is operable at this panel size.")

    # ---- estimand 1: primary, new agents only ----
    print(f"\n--- estimand 1 (primary, registered): pooled pull slope, "
          f"new agents only ---")
    e1 = slope_record(new_rows)
    t_rot, p_rot, n_rot = ri_rotation_exact(new_rows, "delta")
    t_ri, p_ri = ri_pvalue(new_rows, "delta")
    X1, y1, g1, _ = build(new_rows)
    t_wb, p_wb = wild_bootstrap(X1, y1, g1, 1)
    e1.update({"p_ri_rotation_exact": p_rot, "rotation_set_size": n_rot,
               "p_ri_within_agent": p_ri, "p_wild": p_wb,
               "min_attainable_two_sided_p": floor_new})
    out["estimand1_new_agents_slope"] = e1
    report_slope("new", e1)
    print(f"  p (design-exact RI over the {n_rot} rotations)  = {p_rot:.4f}"
          f"   <- the registered p-value")
    print(f"  p (within-agent permutation, B={B}, seed {SEED}) = {p_ri:.4f}"
          f"   (a larger set than the design sampled)")
    print(f"  p (wild cluster bootstrap, house method)       = {p_wb:.4f}")

    fe1 = slope_record(new_rows, fixed_effects=True)
    _, p_fe1 = ri_pvalue(new_rows, "delta", fixed_effects=True)
    fe1["p_ri_within_agent"] = p_fe1
    _, p_rot_fe1, _ = ri_rotation_exact(new_rows, "delta", fixed_effects=True)
    fe1["p_ri_rotation_exact"] = p_rot_fe1
    out["estimand1_new_agents_slope_claim_fe"] = fe1
    print(f"  robustness, claim fixed effects: slope = {fe1['est']:+.3f} "
          f"(se {fe1['se']:.3f}), 95% CI [{fe1['ci95_z'][0]:+.3f}, "
          f"{fe1['ci95_z'][1]:+.3f}], p(exact) = {p_rot_fe1:.4f}, "
          f"MDE = {fe1['mde']:.3f}")

    lo, hi = e1["ci95_z"]
    established = e1["est"] > 0 and lo > 0 and p_rot < 0.05
    if established:
        v1 = ("established on the registered rule: the slope is positive, the "
              "interval excludes zero, and the design-exact test rejects at 5%")
    elif e1["est"] > 0 and lo > 0:
        v1 = ("suggestive and not decisive, in those words: the interval excludes "
              "zero but the design-exact test does not reject at 5%")
    elif lo <= 0 <= hi:
        v1 = ("inconclusive, and not evidence that displacement has no effect: "
              "the interval contains zero")
    else:
        v1 = "the interval excludes zero in the negative direction"
    e1["verdict"] = v1
    print(f"  registered decision rule: {v1}")

    # ---- estimand 2: all agents, error rate not protected ----
    print(f"\n--- estimand 2: pooled pull slope, all {len(agents)} agents "
          f"(Type I error rate NOT protected) ---")
    e2 = slope_record(pooled_rows)
    t_ri2, p_ri2 = ri_pvalue(pooled_rows, "delta")
    X2, y2, g2, _ = build(pooled_rows)
    t_wb2, p_wb2 = wild_bootstrap(X2, y2, g2, 1)
    e2.update({"p_ri_within_agent": p_ri2, "p_wild": p_wb2,
               "error_rate_protected": False})
    out["estimand2_all_agents_slope"] = e2
    report_slope("all", e2)
    print(f"  p (within-agent permutation) = {p_ri2:.4f}   "
          f"p (wild bootstrap) = {p_wb2:.4f}")
    print(f"  The decision to extend followed reading the panel result, so these "
          f"p-values are descriptive.")
    print(f"  The design-exact set here holds 4^{len(agents)} = "
          f"{len(D.DELTAS) ** len(agents)} allocations and is not enumerated.")

    fe2 = slope_record(pooled_rows, fixed_effects=True)
    _, p_fe2 = ri_pvalue(pooled_rows, "delta", fixed_effects=True)
    fe2["p_ri_within_agent"] = p_fe2
    out["estimand2_all_agents_slope_claim_fe"] = fe2
    print(f"  robustness, claim fixed effects: slope = {fe2['est']:+.3f} "
          f"(se {fe2['se']:.3f}), 95% CI [{fe2['ci95_z'][0]:+.3f}, "
          f"{fe2['ci95_z'][1]:+.3f}], p = {p_fe2:.4f}, MDE = {fe2['mde']:.3f}")

    # ---- per-arm slopes, descriptive ----
    print("\n--- descriptive: slope within each arm ---")
    out["by_arm"] = {}
    for label, rws in (("new", new_rows), ("all", pooled_rows)):
        out["by_arm"][label] = {}
        for arm in D.PRIMARY_ARMS:
            sub = [r for r in rws if r["arm"] == arm]
            X, y, cid, names = build(sub)
            keep = [i for i in range(X.shape[1]) if i != names.index("tool")]
            X = X[:, keep]
            b = ols(X, y)
            se = float(np.sqrt(cluster_vcov(X, y, b, cid)[1, 1]))
            rec = {"n": len(sub), "est": float(b[1]), "se": se,
                   "mde": Z_MDE * se,
                   "ci95_z": [float(b[1] - 1.959963985 * se),
                              float(b[1] + 1.959963985 * se)]}
            out["by_arm"][label][arm] = rec
            print(f"  {label:3s} {arm:10s} n={rec['n']:3d}  "
                  f"slope = {rec['est']:+.3f} (se {se:.3f})  "
                  f"95% CI [{rec['ci95_z'][0]:+.3f}, {rec['ci95_z'][1]:+.3f}]")

    # ---- estimand 3: confirmatory exact-match asymmetry, new agents ----
    print("\n--- estimand 3 (confirmatory on the new agents): valuations landing "
          "exactly on the central displayed figure ---")
    e3 = exact_match_test(new_rows)
    out["estimand3_exact_matches_new_agents"] = e3
    print(f"  dpeer_ng {e3['peer_total']}/{len(new_rows)//2}   "
          f"dtool_ng {e3['tool_total']}/{len(new_rows)//2}")
    print(f"  matched agent-claim pairs {e3['n_pairs']}   both {e3['both']}   "
          f"peer only {e3['peer_only']}   tool only {e3['tool_only']}")
    print(f"  exact two-sided sign test on the {e3['discordant']} discordant "
          f"pairs: p = {e3['p_exact_sign_test']:.6f}")
    if e3["direction_as_predicted"] and e3["p_exact_sign_test"] < 0.05:
        v3 = "confirmed: the discordant pairs fall in the predicted direction and the sign test rejects at 5%"
    elif e3["direction_as_predicted"]:
        v3 = "directionally consistent and not statistically decisive"
    else:
        v3 = "not in the predicted direction"
    e3["verdict"] = v3
    print(f"  registered decision rule: {v3}")

    e3all = exact_match_test(pooled_rows)
    out["exact_matches_all_agents_descriptive"] = e3all
    print(f"  all agents, descriptive: dpeer_ng {e3all['peer_total']}/"
          f"{len(pooled_rows)//2}, dtool_ng {e3all['tool_total']}/"
          f"{len(pooled_rows)//2}, discordant {e3all['discordant']}, "
          f"p = {e3all['p_exact_sign_test']:.6f}")

    # ---- estimand 4: the premium, secondary ----
    print("\n--- estimand 4 (secondary): peer premium, difference in slopes ---")
    out["estimand4_premium"] = {}
    for label, rws in (("new", new_rows), ("all", pooled_rows)):
        prem = fit(rws, "delta_x_tool", interaction=True)
        _, p_prem = ri_pvalue(rws, "delta_x_tool", interaction=True)
        signed = -prem["est"]                  # registered sign: peer minus tool
        prem.update({"p_ri_within_agent": p_prem,
                     "peer_minus_tool": float(signed),
                     "peer_minus_tool_ci95_z": [float(-prem["ci95_z"][1]),
                                                float(-prem["ci95_z"][0])],
                     "mde_at_or_below_benchmark":
                         bool(prem["mde"] <= BENCH_PREMIUM)})
        if label == "new":
            _, p_rot_prem, _ = ri_rotation_exact(rws, "delta_x_tool",
                                                 interaction=True)
            prem["p_ri_rotation_exact"] = p_rot_prem
        out["estimand4_premium"][label] = prem
        print(f"  {label:3s} peer minus tool = {signed:+.3f}   se {prem['se']:.3f}"
              f"   95% CI [{prem['peer_minus_tool_ci95_z'][0]:+.3f}, "
              f"{prem['peer_minus_tool_ci95_z'][1]:+.3f}]")
        print(f"      p (within-agent RI) = {p_prem:.4f}"
              + (f"   p (design-exact) = {prem['p_ri_rotation_exact']:.4f}"
                 if label == "new" else "")
              + f"   MDE = {prem['mde']:.3f} vs benchmark {BENCH_PREMIUM:.3f}"
                f"   MDE at or below benchmark: "
                f"{prem['mde_at_or_below_benchmark']}")
    print("  Reported with its interval and its MDE, and not interpreted as "
          "either a replication or a null.")

    # ---- spread, for the record ----
    X, y, cid, names = build(pooled_rows, fixed_effects=True, interaction=True)
    b = ols(X, y)
    u = y - X @ b
    dof = len(y) - np.linalg.matrix_rank(X)
    out["resid_sd_all"] = float(np.sqrt(float(u @ u) / dof))
    out["dev_sd_all"] = float(np.std(y, ddof=1))
    out["dev_mean_all"] = float(np.mean(y))
    print(f"\nresidual sd (claim FE, arm, delta, interaction, all agents) = "
          f"{out['resid_sd_all']:.4f}   sd(dev) = {out['dev_sd_all']:.4f}   "
          f"mean(dev) = {out['dev_mean_all']:+.4f}")

    out["cannot_settle"] = (
        "Whether peer attribution produces more pull than tool attribution in "
        "the damages domain. One model lineage, one additional domain, no human "
        "baseline, and no variation in the realism of the valuation model's "
        "provenance.")

    path = f"{D.ROOT}/analysis/damages_d1_ext.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
