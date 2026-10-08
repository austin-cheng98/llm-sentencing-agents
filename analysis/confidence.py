"""Summarize confidence and exact adoption by released model and arm."""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import FACTORS, PRIMARY, load, ols

ARMS = ["peerbare_ng", "peermatch_ng", "peerdelta_ng", "toolbare_ng",
        "tooldelta_ng", "clerdelta_ng"]
CROSS_MODELS = ["sonnet5", "haiku45", "gpt6", "gpt6sol"]
COMMON_ARMS = ["peerbare_ng", "peermatch_ng", "toolbare_ng"]
PROVIDERS = {"Claude": ["opus5", "sonnet5", "haiku45"],
             "OpenAI": ["gpt6", "gpt6sol"]}


def pull(records):
    y = np.array([r["dev"] for r in records])
    x = np.array([r["delta"] for r in records])
    factors = np.column_stack([[r[name] for r in records] for name in FACTORS]).astype(float)
    return float(ols(np.column_stack([np.ones(len(y)), x, factors]), y)[1])


def summarize(records, model, arms):
    out = []
    for arm in arms:
        data = [r for r in records if r["arm"] == arm and r.get("confidence")]
        if len(data) < 16:
            continue
        exact = sum(1 for r in data if r.get("peer_vals") and r["sentence"] in r["peer_vals"])
        out.append({"model": model, "arm": arm, "pull": pull(data),
                    "conf": float(np.mean([r["confidence"] for r in data])),
                    "exact": 100 * exact / len(data), "n": len(data)})
    return out


def main():
    primary = [r for r in load(model=PRIMARY) if r["run"] == "R1"]
    arms = summarize(primary, PRIMARY, ARMS)
    cross = []
    for model in CROSS_MODELS:
        cross.extend(summarize(load(model=model), model, ARMS))

    pulls = np.array([r["pull"] for r in arms])
    confidence = np.array([r["conf"] for r in arms])
    corr = float(np.corrcoef(pulls, confidence)[0, 1])

    cells = {(r["model"], r["arm"]): r["exact"] for r in arms + cross}
    provider_exact = []
    for arm in COMMON_ARMS:
        for provider, models in PROVIDERS.items():
            values = [cells[(model, arm)] for model in models if (model, arm) in cells]
            if values:
                provider_exact.append({"provider": provider, "arm": arm,
                                       "exact": float(np.mean(values)),
                                       "n_models": len(values)})

    out = {"arms": arms, "corr": corr, "cross": cross,
           "provider_exact": provider_exact}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_confidence.json")
    with open(path, "w") as stream:
        json.dump(out, stream, indent=1)
        stream.write("\n")

    print(f"  pull against confidence: r = {corr:+.2f} across {len(arms)} Opus arms")
    for row in arms + cross:
        print(f"  {row['model']:8s} {row['arm']:14s} pull={row['pull']:+.3f} "
              f"confidence={row['conf']:.2f} exact={row['exact']:.1f}% n={row['n']}")


if __name__ == "__main__":
    main()
