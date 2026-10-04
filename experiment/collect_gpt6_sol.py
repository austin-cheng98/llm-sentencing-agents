"""Collect a frozen, matched GPT-6-sol replication."""
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

RUN = "R8"
MODEL = "gpt-6-sol"
TAG = "gpt6sol"
EFFORT = "high"
JUDGES = ["P1", "P2", "P3", "P4", "P5", "P6", "S1", "S2",
          "H1", "H2"] + [f"G{i:02d}" for i in range(1, 17)]
ARMS = ["peerbare_ng", "toolbare_ng", "peermatch_ng"]
SEED = 20261004
RUN_DIR = ROOT / "runs" / RUN
MANIFEST = RUN_DIR / "manifest.jsonl"
ATTEMPTS = RUN_DIR / "attempts.jsonl"
DATA = RUN_DIR / "decisions.jsonl"
FREEZE = ROOT / "experiment" / "FREEZE-gpt6-sol.txt"
PROTOCOL = ROOT / "experiment" / "prereg-gpt6-sol-replication.md"
DTAB = harness.delta_table()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def key(row):
    return row["arm"], row["judge"], int(row["step"])


def prompt(arm, judge, step):
    return harness.build_prompt(RUN, arm, judge, step, JUDGES)


def verify_r6():
    source = ROOT / "data" / "decisions.jsonl"
    rows = [json.loads(s) for s in source.read_text().splitlines() if s]
    rows = [r for r in rows if r.get("run") == "R6" and r.get("model") == "gpt6"]
    expected = {(a, j, step) for a in ARMS for j in JUDGES for step in range(16)}
    found = [key(r) for r in rows]
    if len(rows) != 1248 or set(found) != expected or len(found) != len(set(found)):
        raise SystemExit("R6 is not a complete, unique 1,248-cell comparison; stopping")
    for r in rows:
        c = harness.SEQ[int(r["step"])]
        delta = DTAB[(r["judge"], c["cid"])]
        if (r["cid"] != c["cid"] or r.get("delta") != delta or
                r.get("peer_vals") != harness.anchor_values(c["mid"], delta)):
            raise SystemExit(f"R6 allocation differs at {key(r)}; stopping")


def init():
    verify_r6()
    if MANIFEST.exists() or ATTEMPTS.exists() or DATA.exists() or FREEZE.exists():
        raise SystemExit("R8 files already exist; refusing to overwrite")
    RUN_DIR.mkdir(parents=True, exist_ok=False)
    tasks = []
    for arm in ARMS:
        for judge in JUDGES:
            for step in range(16):
                text = prompt(arm, judge, step)
                c = harness.SEQ[step]
                tasks.append({"arm": arm, "judge": judge, "step": step,
                              "cid": c["cid"],
                              "prompt_sha256": hashlib.sha256(text.encode()).hexdigest()})
    random.Random(SEED).shuffle(tasks)
    with MANIFEST.open("w") as f:
        for i, task in enumerate(tasks, 1):
            task["task"] = i
            f.write(json.dumps(task, ensure_ascii=False) + "\n")
    inputs = [PROTOCOL, Path(__file__), ROOT / "experiment" / "harness.py",
              ROOT / "experiment" / "prompts.txt", ROOT / "data" / "sequence.json",
              MANIFEST]
    lines = ["Run R8 frozen inputs", f"cells  {len(tasks)}",
             f"manifest_sha256  {digest(MANIFEST)}"]
    lines.extend(f"input_sha256  {digest(p)}  {p.relative_to(ROOT)}" for p in inputs)
    FREEZE.write_text("\n".join(lines) + "\n")
    print(f"Frozen {len(tasks)} cells; manifest SHA-256 {digest(MANIFEST)}")


def verify_freeze():
    if not FREEZE.exists() or not MANIFEST.exists():
        raise SystemExit("run init and freeze R8 before collection")
    for line in FREEZE.read_text().splitlines():
        if line.startswith("input_sha256  "):
            _, expected, name = line.split("  ", 2)
            path = ROOT / name
            if not path.exists() or digest(path) != expected:
                raise SystemExit(f"frozen input changed: {name}")
    manifest_hash = next((x.split("  ", 1)[1] for x in FREEZE.read_text().splitlines()
                          if x.startswith("manifest_sha256  ")), None)
    if digest(MANIFEST) != manifest_hash:
        raise SystemExit("R8 manifest hash mismatch")


def read_jsonl(path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text().splitlines():
        try:
            if line:
                rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def append_jsonl(path, row):
    with path.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()


def run_one(task, codex_path, workdir, attempt):
    text = prompt(task["arm"], task["judge"], task["step"])
    prompt_hash = hashlib.sha256(text.encode()).hexdigest()
    if prompt_hash != task["prompt_sha256"]:
        raise RuntimeError(f"prompt hash mismatch at task {task['task']}")
    fd, out_name = tempfile.mkstemp(prefix="r8-", suffix=".txt")
    os.close(fd)
    Path(out_name).unlink(missing_ok=True)
    out_path = Path(out_name)
    cmd = [codex_path, "exec", "--model", MODEL, "--ephemeral", "--sandbox",
           "read-only", "--skip-git-repo-check", "-C", workdir,
           "-c", 'model_reasoning_effort="high"', "--json",
           "--output-last-message", str(out_path), "-"]
    started = datetime.now(timezone.utc).isoformat()
    failure = None
    tool_calls = 0
    result = None
    try:
        result = subprocess.run(cmd, input=text, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, timeout=240, check=False)
        for line in result.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            item = event.get("item", {})
            if event.get("type") == "item.started" and any(
                    s in str(item.get("type", "")) for s in ("command", "tool", "function")):
                tool_calls += 1
        if result.returncode:
            failure = f"codex_exit_{result.returncode}"
    except subprocess.TimeoutExpired:
        failure = "timeout_240s"
    except Exception as exc:
        failure = f"collector_error_{type(exc).__name__}"
    raw = out_path.read_text(errors="replace") if out_path.exists() else ""
    out_path.unlink(missing_ok=True)
    if not raw and failure is None:
        failure = "empty_model_output"
    c = harness.SEQ[task["step"]]
    parsed = harness.parse(raw)
    sentence = parsed["sentence"]
    ok = (sentence is not None and 0 <= sentence <= c["statmax"] * 2 and
          failure is None)
    delta = DTAB[(task["judge"], task["cid"])]
    vals = harness.anchor_values(c["mid"], delta)
    return {
        "run": RUN, "model": TAG, "model_id": MODEL, "reasoning_effort": EFFORT,
        "attempt": attempt, "arm": task["arm"], "judge": task["judge"],
        "step": task["step"], "cid": task["cid"], "phase": c["phase"],
        "lo": c["lo"], "hi": c["hi"], "mid": c["mid"], "statmax": c["statmax"],
        "offense_type": c["offense_type"], "severity": c["severity"],
        "prior": c["prior"], "remorse": c["remorse"],
        "cooperation": c["cooperation"], "peer_ids": ["K", "R", "T"],
        "peer_vals": vals, "peer_mean": sum(vals) / len(vals), "delta": delta,
        "dev": ((sentence - c["mid"]) / c["mid"] if sentence is not None else None),
        "text_form": "orig", "ok": ok, "failure": failure,
        "tool_calls": tool_calls, "prompt_sha256": prompt_hash,
        "started_at": started, "finished_at": datetime.now(timezone.utc).isoformat(),
        "returncode": result.returncode if result else None,
        "cli_stderr": ((result.stderr or "")[-500:] if result and failure else ""),
        "raw": raw[:1200], **parsed,
    }


def collect(workers=5):
    verify_freeze()
    tasks = [json.loads(s) for s in MANIFEST.read_text().splitlines() if s]
    final_rows = read_jsonl(DATA)
    final_keys = {key(r) for r in final_rows}
    attempts = read_jsonl(ATTEMPTS)
    by_key = {}
    for row in attempts:
        by_key.setdefault(key(row), []).append(row)
    todo = [t for t in tasks if key(t) not in final_keys]
    if not todo:
        print("All manifest cells already have final records.")
        return
    codex_path = shutil.which("codex")
    if not codex_path:
        raise SystemExit("Codex CLI not found")
    workdir = "/private/tmp/gpt6-sol-isolated"
    Path(workdir).mkdir(parents=True, exist_ok=True)
    start = datetime.now(timezone.utc).isoformat()
    print(f"Starting {len(todo)} cells at {start}; concurrency={workers}", flush=True)
    completed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        pending = set()
        task_for = {}
        for task in todo:
            history = by_key.get(key(task), [])
            last = max(history, key=lambda r: r["attempt"]) if history else None
            if last and (last.get("raw") or last["attempt"] >= 2):
                append_jsonl(DATA, last)
                final_keys.add(key(last))
                completed += 1
                continue
            attempt = (last["attempt"] + 1) if last else 1
            future = pool.submit(run_one, task, codex_path, workdir, attempt)
            pending.add(future)
            task_for[future] = (task, attempt)
        while pending:
            done, pending = concurrent.futures.wait(
                pending, return_when=concurrent.futures.FIRST_COMPLETED)
            for future in done:
                task, attempt = task_for.pop(future)
                row = future.result()
                append_jsonl(ATTEMPTS, row)
                by_key.setdefault(key(task), []).append(row)
                if not row["raw"] and attempt == 1:
                    retry = pool.submit(run_one, task, codex_path, workdir, 2)
                    pending.add(retry)
                    task_for[retry] = (task, 2)
                    continue
                append_jsonl(DATA, row)
                final_keys.add(key(task))
                completed += 1
                if completed % 25 == 0 or completed == len(todo):
                    status = "ok" if row["ok"] else row["failure"] or "parse_failure"
                    print(f"completed {completed}/{len(todo)}; last {row['arm']} "
                          f"{row['judge']} {row['cid']}: {status}", flush=True)
    end = datetime.now(timezone.utc).isoformat()
    rows = read_jsonl(DATA)
    counts = {a: sum(r["arm"] == a for r in rows) for a in ARMS}
    valid = {a: sum(r["arm"] == a and r["ok"] for r in rows) for a in ARMS}
    print(f"Finished {end}; records={len(rows)}, valid={sum(valid.values())}; "
          f"by arm={json.dumps(counts, sort_keys=True)}", flush=True)


def audit():
    verify_freeze()
    tasks = [json.loads(s) for s in MANIFEST.read_text().splitlines() if s]
    rows = read_jsonl(DATA)
    expected = {key(t) for t in tasks}
    keys = [key(r) for r in rows]
    if len(tasks) != 1248 or len(rows) != 1248 or set(keys) != expected or len(set(keys)) != len(keys):
        raise SystemExit(f"cell audit failed: manifest={len(tasks)} records={len(rows)} unique={len(set(keys))}")
    for task in tasks:
        text = prompt(task["arm"], task["judge"], task["step"])
        if hashlib.sha256(text.encode()).hexdigest() != task["prompt_sha256"]:
            raise SystemExit(f"prompt changed for {key(task)}")
    report = {"run": RUN, "model_id": MODEL, "reasoning_effort": EFFORT,
              "cells": len(rows), "valid": sum(r["ok"] for r in rows),
              "parse_failures": sum(r["sentence"] is None for r in rows),
              "tool_calls": sum(r["tool_calls"] for r in rows),
              "by_arm": {a: {"attempted": sum(r["arm"] == a for r in rows),
                             "valid": sum(r["arm"] == a and r["ok"] for r in rows)}
                         for a in ARMS},
              "manifest_sha256": digest(MANIFEST), "freeze_sha256": digest(FREEZE)}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=("init", "collect", "audit"))
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()
    {"init": init, "collect": lambda: collect(args.workers), "audit": audit}[args.command]()
