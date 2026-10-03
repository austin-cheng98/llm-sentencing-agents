"""Collect and analyze the frozen GPT-6 Luna source-access follow-up."""
import argparse
import concurrent.futures
import hashlib
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiment"))
import harness

RUN_DIR = ROOT / "runs" / "R7"
MANIFEST = RUN_DIR / "manifest.jsonl"
DATA = RUN_DIR / "decisions.jsonl"
NOTES = RUN_DIR / "collection-notes.md"
JUDGES = ["P1", "P2", "P3", "P4", "P5", "P6", "S1", "S2",
          "H1", "H2"] + [f"G{i:02d}" for i in range(1, 17)]
ARMS = ["peeraccess_ng", "toolaccess_ng", "peereqv_ng", "tooleqv_ng"]
PRIMARY_ARMS = ("peeraccess_ng", "toolaccess_ng")
PRIMARY_STEPS = (0, 1, 2, 5, 6, 7, 8, 10, 11, 12, 13, 15)
CUES = {
    "access": "Both sources are described as having reviewed the case file shown here.",
    "equiv": harness.EQVLINE,
}
DTAB = harness.delta_table()


def prompt(arm, judge, step):
    c = harness.SEQ[step]
    head = harness.PREAMBLE.format(jid=judge)
    head = head[:head.index("Westmoor law gives you")] + harness.NOGUIDE
    body = c["text_alt"] if c["phase"] == "reexposure" else c["text"]
    parts = [head, f"CASE FILE\n{body}",
             f"Statutory maximum: {c['statmax']} months."]
    delta = DTAB[(judge, c["cid"])]
    vals = harness.anchor_values(c["mid"], delta)
    rows = ([f"  Judge {j} sentenced this defendant to {v} months."
             for j, v in zip(("K", "R", "T"), vals)]
            if arm.startswith("peer") else
            [f"  Predicted sentence {i+1}: {v} months."
             for i, v in enumerate(vals)])
    if arm.startswith("peer"):
        block = ["SENTENCES ALREADY ENTERED IN THIS CASE BY OTHER JUDGES OF THIS BENCH",
                 "Three other judges of this jurisdiction have already entered sentences "
                 "for this defendant on the present docket."]
    else:
        block = ["STATISTICAL FORECAST FOR THIS DOCKET",
                 "A regression model fitted to historical dispositions in this "
                 "jurisdiction returns the following predicted sentences for a case "
                 "with this profile."]
    block.extend([CUES["access"] if arm.endswith("access_ng") else CUES["equiv"],
                  *rows])
    parts.append("\n".join(block))
    parts.append(harness.FORMAT)
    return "\n\n".join(parts)


def init_manifest():
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    if MANIFEST.exists() or DATA.exists():
        raise SystemExit("R7 files already exist; refusing to overwrite them")
    tasks = []
    for arm in ARMS:
        for judge in JUDGES:
            for step in range(16):
                text = prompt(arm, judge, step)
                tasks.append({"arm": arm, "judge": judge, "step": step,
                              "cid": harness.SEQ[step]["cid"],
                              "prompt_sha256": hashlib.sha256(text.encode()).hexdigest()})
    random.Random(20261003).shuffle(tasks)
    with MANIFEST.open("w") as f:
        for i, task in enumerate(tasks):
            task["task"] = i + 1
            f.write(json.dumps(task) + "\n")
    print(f"Wrote {len(tasks)} fixed tasks; manifest SHA-256: "
          f"{hashlib.sha256(MANIFEST.read_bytes()).hexdigest()}")


def run_one(task, codex_path, workdir):
    text = prompt(task["arm"], task["judge"], task["step"])
    if hashlib.sha256(text.encode()).hexdigest() != task["prompt_sha256"]:
        raise RuntimeError(f"prompt hash mismatch at task {task['task']}")
    fd, out_name = tempfile.mkstemp(prefix="r7-", suffix=".txt")
    os.close(fd)
    out_path = Path(out_name)
    command = [codex_path, "exec", "--model", "gpt-6-luna", "--ephemeral",
               "--sandbox", "read-only", "--skip-git-repo-check", "-C", workdir,
               "-c", 'model_reasoning_effort="xhigh"', "--json",
               "--output-last-message", str(out_path), "-"]
    input_text = ("Treat the following prompt as the full research decision task. "
                  "Do not use tools. Follow its response format exactly.\n\n" + text)
    tool_calls = 0
    failure = None
    try:
        result = subprocess.run(command, input=input_text, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=180, check=False)
        for line in result.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            item = event.get("item", {})
            if event.get("type") == "item.started" and any(
                    x in str(item.get("type", "")) for x in
                    ("command", "tool", "function")):
                tool_calls += 1
        raw = out_path.read_text(errors="replace") if out_path.exists() else ""
        if result.returncode:
            failure = f"codex_exit_{result.returncode}"
        if not raw:
            failure = failure or "empty_model_output"
    except subprocess.TimeoutExpired:
        result = None
        raw = out_path.read_text(errors="replace") if out_path.exists() else ""
        failure = "timeout_180s"
    finally:
        out_path.unlink(missing_ok=True)

    c = harness.SEQ[task["step"]]
    parsed = harness.parse(raw)
    ok = (parsed["sentence"] is not None and
          0 <= parsed["sentence"] <= c["statmax"] * 2 and failure is None)
    delta = DTAB[(task["judge"], task["cid"])]
    vals = harness.anchor_values(c["mid"], delta)
    return {
        "run": "R7", "model": "gpt6", "model_id": "gpt-6-luna",
        "reasoning_effort": "xhigh", "attempt": 1,
        "arm": task["arm"], "judge": task["judge"], "step": task["step"],
        "cid": task["cid"], "phase": c["phase"], "lo": c["lo"],
        "hi": c["hi"], "mid": c["mid"], "statmax": c["statmax"],
        "offense_type": c["offense_type"], "severity": c["severity"],
        "prior": c["prior"], "remorse": c["remorse"],
        "cooperation": c["cooperation"], "peer_ids": ["K", "R", "T"],
        "peer_vals": vals, "peer_mean": sum(vals) / len(vals),
        "delta": delta, "dev": ((parsed["sentence"] - c["mid"]) / c["mid"]
                                  if parsed["sentence"] is not None else None),
        "text_form": "orig", "ok": ok, "failure": failure,
        "tool_calls": tool_calls, "prompt_sha256": task["prompt_sha256"],
        "cli_stderr": ((result.stderr or "")[-500:] if result is not None and failure else ""),
        "raw": raw[:1200], **parsed,
    }


def collect(workers=5, primary_only=False):
    if not MANIFEST.exists():
        raise SystemExit("run init and freeze the manifest before collection")
    tasks = [json.loads(line) for line in MANIFEST.read_text().splitlines() if line]
    if primary_only:
        tasks = [t for t in tasks if t["arm"] in PRIMARY_ARMS
                 and t["step"] in PRIMARY_STEPS]
    attempted = set()
    if DATA.exists():
        attempted = {(r["arm"], r["judge"], r["step"])
                     for r in (json.loads(x) for x in DATA.read_text().splitlines() if x)}
    todo = [t for t in tasks if (t["arm"], t["judge"], t["step"]) not in attempted]
    codex_path = shutil.which("codex")
    if not codex_path:
        raise SystemExit("Codex CLI not found")
    workdir = "/private/tmp/r7-isolated"
    Path(workdir).mkdir(parents=True, exist_ok=True)
    start = datetime.now(timezone.utc).isoformat()
    scope = "primary sample" if primary_only else "full manifest"
    print(f"Starting {len(todo)} calls in {scope} at {start}; "
          f"concurrency={workers}", flush=True)
    done = 0
    with DATA.open("a") as out, concurrent.futures.ThreadPoolExecutor(
            max_workers=workers) as pool:
        futures = {pool.submit(run_one, t, codex_path, workdir): t for t in todo}
        for future in concurrent.futures.as_completed(futures):
            record = future.result()
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()
            done += 1
            if done % 25 == 0 or done == len(todo):
                print(f"completed {done}/{len(todo)} in this session "
                      f"(last {record['arm']} {record['judge']} {record['cid']}: "
                      f"{'ok' if record['ok'] else record['failure'] or 'parse failure'})",
                      flush=True)
    end = datetime.now(timezone.utc).isoformat()
    records = [json.loads(x) for x in DATA.read_text().splitlines() if x]
    counts = {a: sum(r["arm"] == a for r in records) for a in ARMS}
    valid = {a: sum(r["arm"] == a and r["ok"] for r in records) for a in ARMS}
    tools = sum(r["tool_calls"] for r in records)
    NOTES.write_text(
        "# R7 collection status\n\n"
        f"Latest collection session: {start} to {end}.\n\n"
        "GPT-6 Luna (`gpt-6-luna`) was called in fresh Codex CLI processes at "
        "xhigh reasoning effort, with a read-only sandbox. The frozen manifest "
        "contains 1,664 cells. The confirmatory sample is the 312 matched "
        "judge-case pairs in steps " + ", ".join(map(str, PRIMARY_STEPS)) +
        " for `peeraccess_ng` and `toolaccess_ng`; each selected cell is "
        "attempted once, with no replacement draws. Raw replies, prompt hashes, "
        "parse outcomes, and CLI status are in `decisions.jsonl`.\n\n"
        f"Attempted by arm: `{json.dumps(counts, sort_keys=True)}`.\n\n"
        f"Valid by arm: `{json.dumps(valid, sort_keys=True)}`.\n\n"
        f"Tool calls: {tools}.\n"
    )
    print(f"Session finished at {end}; attempted={sum(counts.values())}, "
          f"valid={sum(valid.values())}, tool_calls={tools}", flush=True)


def analyze():
    sys.path.insert(0, str(ROOT / "analysis"))
    from robustness import dev, premium
    from common import pull
    try:
        from scipy.stats import t as student_t
        tcrit = float(student_t.ppf(0.975, 15))
    except ImportError:
        tcrit = 2.131449545
    rows = [json.loads(x) for x in DATA.read_text().splitlines() if x]
    selected = [r for r in rows if r["step"] in PRIMARY_STEPS]
    by_arm = {a: [r for r in selected if r["arm"] == a and r["ok"]]
              for a in PRIMARY_ARMS}
    out = {"run": "R7", "model": "GPT-6 Luna",
           "primary_steps": list(PRIMARY_STEPS),
           "primary_pairs_target": len(JUDGES) * len(PRIMARY_STEPS),
           "attempted_by_arm_all": {a: sum(r["arm"] == a for r in rows)
                                    for a in ARMS},
           "valid_by_arm_primary_sample": {a: len(by_arm[a])
                                           for a in PRIMARY_ARMS},
           "failed_by_arm_primary_sample": {
               a: sum(r["arm"] == a and r["step"] in PRIMARY_STEPS and not r["ok"]
                      for r in rows) for a in PRIMARY_ARMS}}
    peer, tool = PRIMARY_ARMS
    left = {(r["judge"], r["cid"]) for r in by_arm[peer]}
    right = {(r["judge"], r["cid"]) for r in by_arm[tool]}
    d = [r for r in selected if r["ok"] and r["arm"] in PRIMARY_ARMS
         and (r["judge"], r["cid"]) in (left & right)]
    result = premium(d, peer, dev, B=9999, seed=17)
    if result:
        mde = (tcrit + 0.8416212336) * result["se"]
        result.update({"ci95_t15": [result["est"] - tcrit * result["se"],
                                    result["est"] + tcrit * result["se"]],
                       "mde80_t15": mde,
                       "benchmark": 0.206,
                       "mde_within_benchmark": mde <= 0.206})
    out["primary_premium"] = result
    out["secondary_explicit_cue"] = {
        "status": "incomplete; not analyzed",
        "attempted_by_arm": {a: sum(r["arm"] == a for r in rows)
                             for a in ("peereqv_ng", "tooleqv_ng")}}
    out["number_use"] = {}
    out["number_use"]["neutral_shared_file"] = {}
    for arm in PRIMARY_ARMS:
        d = by_arm[arm]
        beta, se = pull(d)
        out["number_use"]["neutral_shared_file"][arm] = {
            "slope": beta, "se_case_clustered": float(se), "n": len(d),
            "exact_match_rate": sum(r["sentence"] in r["peer_vals"] for r in d) / len(d),
            "outside_displayed_range_rate": sum(
                r["sentence"] < min(r["peer_vals"]) or
                r["sentence"] > max(r["peer_vals"]) for r in d) / len(d),
        }
    output = ROOT / "analysis" / "out_r7_source_access.json"
    output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    print(f"Wrote {output}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=("init", "collect", "analyze"))
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--primary-only", action="store_true")
    args = ap.parse_args()
    if args.command == "init":
        init_manifest()
    elif args.command == "collect":
        collect(args.workers, args.primary_only)
    else:
        analyze()
