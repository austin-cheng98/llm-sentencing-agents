#!/usr/bin/env python3
"""Prepare and collect the fixed GPT-6 Sol damages replication, D2."""
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs" / "D2"
REG = ROOT / "damages" / "prereg-D2-gpt6-sol.md"
FREEZE = ROOT / "damages" / "FREEZE-D2-gpt6-sol.txt"
D1_MANIFEST = ROOT / "runs" / "D1" / "manifest.jsonl"
AGENTS = ("A02", "A05", "A08", "A10", "A11", "A04", "A07", "A09", "A12", "A01")
ARMS = ("dpeer_ng", "dtool_ng")
CODEX = "/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex"
EMPTY_CWD = Path("/private/tmp/gpt6-sol-d2-empty")
LOCK = threading.Lock()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def append(path, obj):
    with LOCK, open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def load_damages():
    expanduser = os.path.expanduser
    os.path.expanduser = lambda p: str(ROOT) if p == "~/judicial-drift" else expanduser(p)
    try:
        spec = importlib.util.spec_from_file_location("d2_damages", ROOT / "scripts" / "damages.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        os.path.expanduser = expanduser
    module.ROOT = str(ROOT)
    return module


def prepare():
    if RUN.exists():
        raise SystemExit(f"refusing to overwrite {RUN}")
    module = load_damages()
    source = [json.loads(line) for line in D1_MANIFEST.read_text().splitlines() if line]
    selected = [r for r in source if r["judge"] in AGENTS and r["arm"] in ARMS]
    expected = {(a, arm, step) for a in AGENTS for arm in ARMS for step in range(16)}
    found = {(r["judge"], r["arm"], r["step"]) for r in selected}
    if len(selected) != 320 or found != expected:
        raise SystemExit(f"D1 manifest selection mismatch: {len(selected)} cells")
    tasks = []
    for task, old in enumerate(selected, 1):
        prompt = module.build_prompt(old["arm"], old["judge"], old["step"])
        prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        if prompt_hash != old["prompt_sha256"]:
            raise SystemExit(f"D1 prompt hash mismatch at source task {old['task']}")
        tasks.append({
            "task": task,
            "source_task": old["task"],
            "arm": old["arm"],
            "judge": old["judge"],
            "step": old["step"],
            "cid": old["cid"],
            "prompt_sha256": prompt_hash,
            "model": "gpt-6-sol",
            "reasoning_effort": "high",
        })
    RUN.mkdir(parents=True)
    (RUN / "raw").mkdir()
    (RUN / "logs").mkdir()
    with open(RUN / "manifest.jsonl", "w", encoding="utf-8") as f:
        for task in tasks:
            f.write(json.dumps(task, ensure_ascii=False) + "\n")
    print(f"prepared {len(tasks)} prompt-hash-matched tasks in {RUN / 'manifest.jsonl'}")


def read_freeze():
    frozen = {}
    for line in FREEZE.read_text().splitlines():
        parts = line.split("  ", 1)
        if len(parts) == 2 and len(parts[0]) == 64:
            frozen[parts[1]] = parts[0]
    for rel, expected in frozen.items():
        actual = digest(ROOT / rel)
        if actual != expected:
            raise SystemExit(f"frozen input mismatch: {rel}")
    if not frozen:
        raise SystemExit("freeze file has no hashes")


def event_summary(stdout):
    types, tool_events = set(), 0
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        typ = event.get("type") or event.get("event")
        if typ:
            types.add(str(typ))
        item = event.get("item", {})
        item_type = item.get("type") if isinstance(item, dict) else None
        if item_type and any(s in item_type.lower() for s in ("command", "tool", "mcp")):
            tool_events += 1
    return sorted(types), tool_events


def collect_one(task, module):
    prompt = module.build_prompt(task["arm"], task["judge"], task["step"])
    if hashlib.sha256(prompt.encode("utf-8")).hexdigest() != task["prompt_sha256"]:
        raise RuntimeError(f"prompt hash mismatch for D2 task {task['task']}")
    raw_path = RUN / "raw" / f"{task['task']:03d}.txt"
    log_path = RUN / "logs" / f"{task['task']:03d}.json"
    append(RUN / "attempts.jsonl", {
        "event": "started", "task": task["task"], "utc": now(),
        "prompt_sha256": task["prompt_sha256"],
    })
    cmd = [CODEX, "exec", "--ephemeral", "--sandbox", "read-only",
           "--skip-git-repo-check", "--model", "gpt-6-sol", "--config",
           'model_reasoning_effort="high"', "--json", "--color", "never",
           "--output-last-message", str(raw_path), "-C", str(EMPTY_CWD), "-"]
    started = time.monotonic()
    proc = subprocess.run(cmd, input=prompt, text=True, encoding="utf-8",
                          capture_output=True, check=False)
    elapsed = round(time.monotonic() - started, 2)
    raw = raw_path.read_text(encoding="utf-8") if raw_path.exists() else None
    event_types, tool_events = event_summary(proc.stdout)
    rec = None
    if raw is not None:
        raw_path.write_text(raw, encoding="utf-8")
        with LOCK:
            rec = module.record("D2", task["arm"], task["judge"], task["step"],
                                raw, "gpt6sol", f"{task['arm']}_{task['judge']}")
    summary = {
        "task": task["task"], "source_task": task["source_task"],
        "exit_code": proc.returncode, "elapsed_seconds": elapsed,
        "final_message_present": raw is not None,
        "final_message_chars": len(raw) if raw is not None else 0,
        "parsed_ok": rec["ok"] if rec else None,
        "cli_event_types": event_types, "tool_events": tool_events,
        "stderr_chars": len(proc.stderr), "stderr_sha256": hashlib.sha256(
            proc.stderr.encode("utf-8")).hexdigest(),
    }
    log_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    append(RUN / "attempts.jsonl", {"event": "finished", "utc": now(), **summary})
    return summary


def collect(max_calls=None, workers=5):
    read_freeze()
    module = load_damages()
    tasks = [json.loads(line) for line in (RUN / "manifest.jsonl").read_text().splitlines() if line]
    attempted = set()
    attempt_path = RUN / "attempts.jsonl"
    if attempt_path.exists():
        for line in attempt_path.read_text().splitlines():
            event = json.loads(line)
            if event.get("event") == "started":
                attempted.add(event["task"])
    pending = [t for t in tasks if t["task"] not in attempted]
    if max_calls is not None:
        pending = pending[:max_calls]
    print(f"starting {len(pending)} unattempted tasks; concurrency={workers}", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(collect_one, task, module): task for task in pending}
        done = 0
        for future in concurrent.futures.as_completed(futures):
            task = futures[future]
            try:
                summary = future.result()
                status = "response" if summary["final_message_present"] else "no-response"
                print(f"D2 {task['task']}/320 {status} ({summary['elapsed_seconds']}s)", flush=True)
            except Exception as exc:
                append(attempt_path, {"event": "collector_error", "task": task["task"],
                                      "utc": now(), "error": type(exc).__name__})
                print(f"D2 {task['task']}/320 collector-error {type(exc).__name__}", flush=True)
            done += 1
    if done:
        print(f"finished {done} calls", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "collect"))
    parser.add_argument("--max-calls", type=int)
    parser.add_argument("--workers", type=int, default=5)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    else:
        collect(args.max_calls, args.workers)
