# Collection notes — R1

- **Model ID:** The Codex session identified itself as GPT-6, but the `collaboration.spawn_agent` interface did not expose the inherited child model's exact backend identifier. The records therefore use the requested model tag `gpt6`; the exact child model ID could not be verified.
- **Delegation:** A collection driver used `collaboration.spawn_agent` to create one fresh child context per decision (`fork_turns: none`). Each child received the verbatim harness prompt, preceded by the user-requested instruction: “Do not use tools or access the web.” No child model or reasoning overrides were supplied; they inherited the default settings. The tool interface did not allow disabling tools or web access, so this instruction was prompt-level only.
- **Collection dates (UTC):** 2026-09-30 through 2026-10-01.
- **Record tag:** `gpt6` on all 96 records.
- **Format failures:** None; the harness accepted all 96 records.
- **Audit note:** The first count audit found `peerbare_ng/F2/1` missing. It was collected in a fresh child context and recorded before collection continued. Final shard counts are 16 records per judge for each target arm, covering steps 0–15.
