"""Analysis for the damages transfer run D1, as amended.

The confirmatory estimand is the pooled pull slope: the OLS coefficient on
`delta` in a regression of `dev` on displacement with the two primary arms
pooled. The premium (the `delta x arm` interaction) is secondary and is
reported with its minimum detectable effect; it is not interpreted as either a
replication or a null.

Confirmatory sample: agents A02, A05, A08, A10 x 16 claims x 2 primary arms.
The specification matches the sentencing pull slope (constant, displacement,
the four case factors) with an arm indicator added because the arms are pooled.
Standard errors cluster on claim. The registered p-value comes from
randomization inference with B = 9,999 and seed 17, permuting the displacement
allocation within agent.

Registered in damages/AMENDMENT-D1-manipulation-check.md.
"""
import json
import sys
import numpy as np

sys.path.insert(0, "/Users/austincheng/judicial-drift/scripts")
import damages as D

PANEL = ("A02", "A05", "A08", "A10")
RUN = "D1"
B = 9999
SEED = 17
Z_MDE = 2.8015852185999996          # (z_0.975 + z_0.80), the registered constant
BENCH_PULL = 0.61                   # \pullPeerN = \pullToolN, sentencing no-guideline arms
BENCH_PREMIUM = 0.206               # \iMS, the structure-matched sentencing premium
WEBB = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5),
                 np.sqrt(0.5), 1.0, np.sqrt(1.5)])


def ols(X, y):
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    return b


def cluster_vcov(X, y, b, g):
    """Cluster-robust covariance with the standard small-sample correction."""
    n, k = X.shape
    u = y - X @ b
    XtX_inv = np.linalg.pinv(X.T @ X)
    meat = np.zeros((k, k))
    for c in np.unique(g):
        m = g == c
        s = X[m].T @ u[m]
        meat += np.outer(s, s)
    G = len(np.unique(g))
    corr = (G / (G - 1.0)) * ((n - 1.0) / (n - np.linalg.matrix_rank(X)))
    return corr * XtX_inv @ meat @ XtX_inv


def wild_bootstrap(X, y, g, j, B=B, seed=SEED):
    """p for H0: beta_j = 0, imposing the null on the residuals. House method."""
    rng = np.random.default_rng(seed)
    b_full = ols(X, y)
    t_obs = b_full[j] / np.sqrt(cluster_vcov(X, y, b_full, g)[j, j])
    keep = [i for i in range(X.shape[1]) if i != j]
    Xr = X[:, keep]
    br = ols(Xr, y)
    ur = y - Xr @ br
    fitted = Xr @ br
    clusters = np.unique(g)
    cnt = 0
    for _ in range(B):
        w = rng.choice(WEBB, size=len(clusters))
        wv = np.empty(len(y))
        for ci, c in enumerate(clusters):
            wv[g == c] = w[ci]
        yb = fitted + ur * wv
        bb = ols(X, yb)
        tb = bb[j] / np.sqrt(cluster_vcov(X, yb, bb, g)[j, j])
        if abs(tb) >= abs(t_obs) - 1e-12:
            cnt += 1
    return float(t_obs), (cnt + 1) / (B + 1)


def load_panel():
    rows = [r for r in D.load(RUN)
            if r["ok"] and r["judge"] in PANEL and r["arm"] in D.PRIMARY_ARMS]
    rows.sort(key=lambda r: (r["arm"], r["judge"], r["step"]))
    return rows


def build(rows, fixed_effects=False, interaction=False):
    y = np.array([r["dev"] for r in rows])
    delta = np.array([r["delta"] for r in rows])
    tool = np.array([1.0 if r["arm"] == "dtool_ng" else 0.0 for r in rows])
    cid = np.array([r["cid"] for r in rows])
    cols = [np.ones(len(y)), delta]
    names = ["const", "delta"]
    cols.append(tool)
    names.append("tool")
    if interaction:
        cols.append(delta * tool)
        names.append("delta_x_tool")
    if fixed_effects:
        for c in sorted(set(cid))[1:]:
            cols.append((cid == c).astype(float))
            names.append(f"cid_{c}")
    else:
        for f in D.FACTORS:
            cols.append(np.array([float(r[f]) for r in rows]))
            names.append(f)
    return np.column_stack(cols), y, cid, names


def fit(rows, j_name, **kw):
    X, y, cid, names = build(rows, **kw)
    j = names.index(j_name)
    b = ols(X, y)
    V = cluster_vcov(X, y, b, cid)
    se = float(np.sqrt(V[j, j]))
    G = len(np.unique(cid))
    return {
        "n": len(rows),
        "clusters": G,
        "est": float(b[j]),
        "se": se,
        "ci95_z": [float(b[j] - 1.959963985 * se), float(b[j] + 1.959963985 * se)],
        "mde": Z_MDE * se,
    }


def ri_pvalue(rows, j_name, B=B, seed=SEED, **kw):
    """Randomization inference, permuting the displacement allocation within agent.

    Each agent's sixteen displacement values are permuted across that agent's
    sixteen claims, which preserves the per-agent 4/4/4/4 marginal. The two arms
    of a matched agent-claim pair see the same figures by construction, so the
    permutation is applied to the pair, not to each arm separately.
    """
    X, y, cid, names = build(rows, **kw)
    j = names.index(j_name)
    b = ols(X, y)
    t_obs = b[j] / np.sqrt(cluster_vcov(X, y, b, cid)[j, j])

    # map (judge, step) -> row indices, and the agent's own delta vector
    agents = sorted({r["judge"] for r in rows})
    by_agent = {}
    for a in agents:
        steps = sorted({r["step"] for r in rows if r["judge"] == a})
        idx = [[i for i, r in enumerate(rows) if r["judge"] == a and r["step"] == s]
               for s in steps]
        dv = np.array([rows[ix[0]]["delta"] for ix in idx])
        by_agent[a] = (idx, dv)

    rng = np.random.default_rng(seed)
    dcol = names.index("delta")
    has_ix = "delta_x_tool" in names
    if has_ix:
        xcol = names.index("delta_x_tool")
        tool = X[:, names.index("tool")].copy()
    Xp = X.copy()
    cnt = 0
    for _ in range(B):
        newd = np.empty(len(rows))
        for a in agents:
            idx, dv = by_agent[a]
            perm = rng.permutation(len(dv))
            for k, ix in enumerate(idx):
                newd[ix] = dv[perm[k]]
        Xp[:, dcol] = newd
        if has_ix:
            Xp[:, xcol] = newd * tool
        bb = ols(Xp, y)
        tb = bb[j] / np.sqrt(cluster_vcov(Xp, y, bb, cid)[j, j])
        if abs(tb) >= abs(t_obs) - 1e-12:
            cnt += 1
    return float(t_obs), (cnt + 1) / (B + 1)


def ri_rotation_exact(rows, j_name, **kw):
    """RI over the design's own randomization set: the four group-to-displacement
    rotations per agent. With four agents the set has 4^4 = 256 allocations and is
    enumerated exactly."""
    import itertools
    X, y, cid, names = build(rows, **kw)
    j = names.index(j_name)
    b = ols(X, y)
    t_obs = b[j] / np.sqrt(cluster_vcov(X, y, b, cid)[j, j])
    agents = sorted({r["judge"] for r in rows})
    # recover each claim's group index from the frozen delta table on agent A01
    base = {c: D.DTAB[(D.AGENTS[0], c)] for c in {r["cid"] for r in rows}}
    grp = {c: D.DELTAS.index(base[c]) for c in base}
    dcol = names.index("delta")
    has_ix = "delta_x_tool" in names
    if has_ix:
        xcol = names.index("delta_x_tool")
        tool = X[:, names.index("tool")].copy()
    Xp = X.copy()
    cnt = tot = 0
    for rot in itertools.product(range(len(D.DELTAS)), repeat=len(agents)):
        rmap = dict(zip(agents, rot))
        newd = np.array([D.DELTAS[(grp[r["cid"]] + rmap[r["judge"]]) % len(D.DELTAS)]
                         for r in rows], dtype=float)
        Xp[:, dcol] = newd
        if has_ix:
            Xp[:, xcol] = newd * tool
        bb = ols(Xp, y)
        tb = bb[j] / np.sqrt(cluster_vcov(Xp, y, bb, cid)[j, j])
        tot += 1
        if abs(tb) >= abs(t_obs) - 1e-12:
            cnt += 1
    return float(t_obs), cnt / tot, tot


def exact_matches(rows):
    """Exploratory, not registered. How often does a valuation land exactly on the
    central displayed figure, and does that differ by arm? Tested as a matched
    sign test over agent-claim pairs, which is the unit the design matches on."""
    import json
    from math import comb
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
    # exact two-sided binomial on the discordant pairs
    k = min(peer_only, tool_only)
    p = min(1.0, 2.0 * sum(comb(disc, i) for i in range(k + 1)) / 2.0 ** disc) \
        if disc else 1.0
    return {
        "n_pairs": len(pairs),
        "peer_total": sum(v for (_, _, a), v in hit.items() if a == "dpeer_ng"),
        "tool_total": sum(v for (_, _, a), v in hit.items() if a == "dtool_ng"),
        "both": both, "peer_only": peer_only, "tool_only": tool_only,
        "p_exact_sign_test": float(p),
    }


def main():
    rows = load_panel()
    assert len(rows) == 128, len(rows)

    out = {"run": RUN, "panel": list(PANEL), "n": len(rows),
           "benchmark_pull": BENCH_PULL, "benchmark_premium": BENCH_PREMIUM,
           "mde_constant": Z_MDE}

    print(f"confirmatory panel: {len(rows)} decisions, agents {' '.join(PANEL)}, "
          f"arms {' '.join(D.PRIMARY_ARMS)}")

    # ---- confirmatory: pooled pull slope ----
    pooled = fit(rows, "delta")
    t_ri, p_ri = ri_pvalue(rows, "delta")
    Xp, yp, gp, _ = build(rows)
    t_wb, p_wb = wild_bootstrap(Xp, yp, gp, 1)
    t_rot, p_rot, n_rot = ri_rotation_exact(rows, "delta")
    pooled.update({"t": t_ri, "p_ri": p_ri, "p_wild": p_wb,
                   "p_ri_rotation_exact": p_rot, "rotation_set_size": n_rot})
    out["pooled_slope"] = pooled
    print("\n--- confirmatory: pooled pull slope (arms pooled) ---")
    print(f"  slope = {pooled['est']:+.3f}   clustered se {pooled['se']:.3f}   "
          f"t = {pooled['t']:+.2f}   G = {pooled['clusters']}")
    print(f"  95% CI [{pooled['ci95_z'][0]:+.3f}, {pooled['ci95_z'][1]:+.3f}]")
    print(f"  p (RI, B={B}, seed {SEED}, within-agent permutation) = {p_ri:.4f}")
    print(f"  p (RI, exact over the {n_rot} design rotations)      = {p_rot:.4f}"
          f"   <- the design's own randomization set")
    print(f"  p (wild cluster bootstrap, house method)            = {p_wb:.4f}")
    print(f"  MDE = {pooled['mde']:.3f}   benchmark (sentencing, no guideline) "
          f"= {BENCH_PULL:.2f}")

    # robustness: claim fixed effects instead of the four factors
    fe = fit(rows, "delta", fixed_effects=True)
    _, p_fe = ri_pvalue(rows, "delta", fixed_effects=True)
    fe["p_ri"] = p_fe
    out["pooled_slope_claim_fe"] = fe
    print(f"\n  robustness, claim fixed effects: slope = {fe['est']:+.3f} "
          f"(se {fe['se']:.3f}), 95% CI [{fe['ci95_z'][0]:+.3f}, "
          f"{fe['ci95_z'][1]:+.3f}], p = {p_fe:.4f}, MDE = {fe['mde']:.3f}")

    # ---- descriptive: per-arm slopes ----
    print("\n--- descriptive: slope within each arm ---")
    out["by_arm"] = {}
    for arm in D.PRIMARY_ARMS:
        sub = [r for r in rows if r["arm"] == arm]
        X, y, cid, names = build(sub)
        drop = names.index("tool")
        keep = [i for i in range(X.shape[1]) if i != drop]
        X = X[:, keep]
        b = ols(X, y)
        se = float(np.sqrt(cluster_vcov(X, y, b, cid)[1, 1]))
        rec = {"n": len(sub), "est": float(b[1]), "se": se, "mde": Z_MDE * se,
               "ci95_z": [float(b[1] - 1.959963985 * se),
                          float(b[1] + 1.959963985 * se)]}
        out["by_arm"][arm] = rec
        print(f"  {arm:10s} n={rec['n']:3d}  slope = {rec['est']:+.3f} "
              f"(se {se:.3f})  95% CI [{rec['ci95_z'][0]:+.3f}, "
              f"{rec['ci95_z'][1]:+.3f}]")

    # ---- secondary: the premium, reported with its MDE ----
    prem = fit(rows, "delta_x_tool", interaction=True)
    _, p_prem = ri_pvalue(rows, "delta_x_tool", interaction=True)
    # the registered sign convention is peer minus tool; the regressor is tool
    prem_signed = -prem["est"]
    prem.update({"p_ri": p_prem,
                 "peer_minus_tool": float(prem_signed),
                 "peer_minus_tool_ci95_z": [float(-prem["ci95_z"][1]),
                                            float(-prem["ci95_z"][0])]})
    out["premium_secondary"] = prem
    print("\n--- secondary: peer premium (difference in slopes) ---")
    print(f"  peer minus tool = {prem_signed:+.3f}   clustered se {prem['se']:.3f}")
    print(f"  95% CI [{prem['peer_minus_tool_ci95_z'][0]:+.3f}, "
          f"{prem['peer_minus_tool_ci95_z'][1]:+.3f}]   p (RI) = {p_prem:.4f}")
    print(f"  MDE = {prem['mde']:.3f}   benchmark = {BENCH_PREMIUM:.3f}   "
          f"MDE at or below benchmark: {prem['mde'] <= BENCH_PREMIUM}")

    # ---- residual spread, for the record ----
    X, y, cid, names = build(rows, fixed_effects=True, interaction=True)
    b = ols(X, y)
    u = y - X @ b
    dof = len(y) - np.linalg.matrix_rank(X)
    out["resid_sd"] = float(np.sqrt(float(u @ u) / dof))
    out["dev_sd"] = float(np.std(y, ddof=1))
    out["dev_mean"] = float(np.mean(y))

    # ---- decision rule ----
    lo, hi = pooled["ci95_z"]
    if pooled["est"] > 0 and lo > 0:
        verdict = ("displacement moves valuations in the damages domain: the pooled "
                   "slope is positive and the interval excludes zero")
    elif lo <= 0 <= hi:
        verdict = ("inconclusive: the interval contains zero. This is not evidence "
                   "that displacement has no effect")
    else:
        verdict = ("the interval excludes zero in the negative direction")
    out["verdict"] = verdict
    out["randomization_set_note"] = (
        "The displacement allocation is randomized only through the "
        "group-to-displacement rotation, one of four per agent. With four agents "
        "the randomization set holds 4^4 = 256 allocations, so the smallest "
        "attainable two-sided p is 1/256 = 0.0039 and the distribution of the "
        "test statistic is coarse. The registered within-agent permutation test "
        "draws from a much larger set that the design did not actually sample "
        "from. Both are reported. Reducing the panel from twelve agents to four "
        "shrank this set from 4^12 to 4^4; that cost was not noted in the "
        "amendment and is recorded here.")
    print(f"\n--- registered decision rule ---\n  {verdict}")
    print(f"\nresidual sd (claim FE, arm, delta, interaction) = {out['resid_sd']:.4f}"
          f"   sd(dev) = {out['dev_sd']:.4f}   mean(dev) = {out['dev_mean']:+.4f}")

    T15 = 2.131449545559323  # t_{0.975} on G - 1 = 15 degrees of freedom
    pooled["ci95_t"] = [float(pooled["est"] - T15 * pooled["se"]),
                        float(pooled["est"] + T15 * pooled["se"])]
    print(f"\n  the same interval on t with G - 1 = 15 df: "
          f"[{pooled['ci95_t'][0]:+.3f}, {pooled['ci95_t'][1]:+.3f}]")

    em = exact_matches(rows)
    out["exact_matches_exploratory"] = em
    print("\n--- exploratory, not registered: valuations landing exactly on the "
          "central displayed figure ---")
    print(f"  dpeer_ng {em['peer_total']}/64   dtool_ng {em['tool_total']}/64")
    print(f"  matched agent-claim pairs: {em['n_pairs']}   both arms "
          f"{em['both']}   peer only {em['peer_only']}   tool only "
          f"{em['tool_only']}")
    print(f"  exact sign test on the discordant pairs: p = "
          f"{em['p_exact_sign_test']:.5f}")

    path = f"{D.ROOT}/analysis/damages_d1.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
