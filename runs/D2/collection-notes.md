# D2 collection notes

D2 is the separate GPT-6 Sol high-reasoning replication registered in
`damages/prereg-D2-gpt6-sol.md` and frozen in
`damages/FREEZE-D2-gpt6-sol.txt`. Collection used Codex CLI 0.160.0 from
2026-10-04 20:25:01 to 20:41:03 UTC, with up to five fresh ephemeral contexts
in flight. Each context received one D1-matched prompt on stdin, in a read-only
sandbox, with model `gpt-6-sol` and reasoning effort `high`.

The manifest contains 320 cells: ten complete D1 agents, sixteen claims, and
the two primary arms. All 320 rendered prompt hashes matched their D1 manifest
entries. The collection produced 319 final replies, all 319 parseable, and one
no-response failure: task 261 (`dtool_ng`, A07, step 3; CLI exit code 1). It was
not retried. The resulting records contain 160 `dpeer_ng` and 159 `dtool_ng`
responses, yielding 159 complete matched pairs. No tool-use events were
recorded.

Full final replies are in `raw/`; structured records are in the
`decisions.*.jsonl` shards; task-level attempt summaries are in `logs/` and
`attempts.jsonl`. D2 remains separate from D1 and has not been merged into
`data/decisions.jsonl`.

The prompt, cases, manifest, registration, collector, and referenced D1 analysis
inputs are checksum-verified in `damages/FREEZE-D2-gpt6-sol.txt`. D1 used a
Claude Opus subagent route, while D2 used the Codex CLI route; this
provider-specific difference is disclosed in the registration.
