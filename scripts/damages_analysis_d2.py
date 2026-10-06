"""Analyze the frozen GPT-6 Sol D2 replication and its matched D1 contrast."""
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import damages as D
D.ROOT = str(ROOT)
import damages_analysis as A
import damages_analysis_prox as P

AGENTS = ("A02", "A05", "A08", "A10", "A11", "A04", "A07", "A09", "A12", "A01")
ARMS = ("dpeer_ng", "dtool_ng")
MEASURES = ("inside_band", "dist_central", "within_tol", "equals_central")
T15 = 2.131449545559323


def rows(run):
    out = [r for r in D.load(run)
           if r["ok"] and r["judge"] in AGENTS and r["arm"] in ARMS]
    return sorted(out, key=lambda r: (r["judge"], r["step"], r["arm"]))


def matched_keys(measure_map):
    keys = {(j, s) for j, s, _ in measure_map}
    return sorted(k for k in keys
                  if all((*k, arm) in measure_map for arm in ARMS))


def clustered_mean_difference(values, claims):
    y = np.asarray(values, dtype=float)
    X = np.ones((len(y), 1))
    b = A.ols(X, y)
    se = float(np.sqrt(A.cluster_vcov(X, y, b, np.asarray(claims))[0, 0]))
    est = float(b[0])
    clusters = len(set(claims))
    return {
        "peer_minus_tool": est,
        "clustered_se": se,
        "ci95_t": [est - T15 * se, est + T15 * se],
        "clusters": clusters,
    }


def proximity(run_rows):
    m = P.measures(run_rows)
    pairs = matched_keys(m)
    out = {"n_rows": len(run_rows), "n_pairs": len(pairs), "measures": {}}
    for key in MEASURES:
        sign = None if key == "dist_central" else P.sign_test(m, key, pairs)
        peer_values = [m[(*pair, "dpeer_ng")][key] for pair in pairs]
        tool_values = [m[(*pair, "dtool_ng")][key] for pair in pairs]
        diffs = [peer - tool for peer, tool in zip(peer_values, tool_values)]
        claims = [m[(*pair, "dpeer_ng")]["cid"] for pair in pairs]
        clustered = clustered_mean_difference(diffs, claims)
        record = {"n_pairs": len(pairs), "sign_test": sign, **clustered}
        if key == "dist_central":
            record.update({
                "mean_peer": float(np.mean(peer_values)),
                "mean_tool": float(np.mean(tool_values)),
                "mde": float(A.Z_MDE * clustered["clustered_se"]),
            })
        else:
            record.update({
                "peer_total": int(sum(peer_values)),
                "tool_total": int(sum(tool_values)),
            })
        out["measures"][key] = record
    return out, m, pairs


def pull(rows_for_run):
    pooled = A.fit(rows_for_run, "delta")
    _, pooled["p_ri_within_agent"] = A.ri_pvalue(rows_for_run, "delta")
    premium = A.fit(rows_for_run, "delta_x_tool", interaction=True)
    _, premium["p_ri_within_agent"] = A.ri_pvalue(
        rows_for_run, "delta_x_tool", interaction=True)
    premium["orientation"] = "tool minus peer"
    return {"pooled_pull": pooled, "slope_premium": premium}


def model_contrast(d1_map, d2_map, d1_pairs, d2_pairs):
    common = sorted(set(d1_pairs) & set(d2_pairs))
    claims = [d1_map[(*pair, "dpeer_ng")]["cid"] for pair in common]
    out = {"n_common_pairs": len(common), "measures": {}}
    for key in MEASURES:
        d1 = np.asarray([d1_map[(*pair, "dpeer_ng")][key]
                         - d1_map[(*pair, "dtool_ng")][key] for pair in common])
        d2 = np.asarray([d2_map[(*pair, "dpeer_ng")][key]
                         - d2_map[(*pair, "dtool_ng")][key] for pair in common])
        rec = clustered_mean_difference(d2 - d1, claims)
        rec["interpretation"] = "descriptive D2-minus-D1 change in peer-minus-tool contrast"
        out["measures"][key] = rec
    return out


def main():
    d1_rows, d2_rows = rows("D1"), rows("D2")
    if len(d1_rows) != 320 or len(d2_rows) != 319:
        raise SystemExit(f"unexpected panel sizes: D1={len(d1_rows)}, D2={len(d2_rows)}")
    d1_prox, d1_map, d1_pairs = proximity(d1_rows)
    d2_prox, d2_map, d2_pairs = proximity(d2_rows)
    result = {
        "D1_Opus5": {"proximity": d1_prox, "pull": pull(d1_rows)},
        "D2_GPT6Sol_high": {"proximity": d2_prox, "pull": pull(d2_rows)},
        "model_contrast": model_contrast(d1_map, d2_map, d1_pairs, d2_pairs),
        "D2_missing_pair": {
            "arm": "dtool_ng", "judge": "A07", "step": 3,
            "reason": "no final model response; not retried per registration",
        },
        "agents": list(AGENTS),
        "analysis_note": "D1 proximity measures were selected after its initial panel; D2 was registered before GPT-6 Sol collection. D1-D2 contrast is descriptive.",
    }
    out = ROOT / "analysis" / "damages_d2.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for name in ("D1_Opus5", "D2_GPT6Sol_high"):
        p = result[name]["proximity"]
        print(f"{name}: {p['n_rows']} records, {p['n_pairs']} matched pairs")
        for key, v in p["measures"].items():
            if key == "dist_central":
                counts = (f"mean distance peer={v['mean_peer']:.4f} "
                          f"tool={v['mean_tool']:.4f} MDE={v['mde']:.4f}")
            else:
                counts = (f"peer={v['peer_total']}/{v['n_pairs']} "
                          f"tool={v['tool_total']}/{v['n_pairs']}")
            p_value = v["sign_test"]["p_exact_sign_test"] if v["sign_test"] else "n/a"
            print(f"  {key:14s} {counts} peer-tool={v['peer_minus_tool']:+.4f} "
                  f"CI=[{v['ci95_t'][0]:+.4f},{v['ci95_t'][1]:+.4f}] p={p_value}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
