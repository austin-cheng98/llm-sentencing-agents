# R6 collection notes

R6 is the expanded GPT-6 Luna run that replaces the original 96-decision R1
Luna run in the reported analysis. The R1 raw records are retained separately
for auditability and are not pooled with R6. R5 was a small pilot and is also
excluded.

## Planned collection

- Model tag: `gpt6` (GPT-6 Luna)
- Judges: P1--P6, S1--S2, H1--H2, G01--G16
- Arms: `peerbare_ng`, `toolbare_ng`, `peermatch_ng`
- Cases: C00--C15 (16 per judge and arm)
- Target: 1,248 decisions
- Prompt source: `experiment/harness.py` generated verbatim for each cell
- One fresh context per cell; one draw per cell

## Audit status

Collection ran from 2026-10-03 01:30 to 02:13 UTC. It produced 1,248 unique
records: 416 per arm, 26 judges per arm, and 16 cases per judge. All replies
parsed successfully. Three initial R6 cells used the collaboration runner; the
remaining cells used fresh local Codex processes with model `gpt-6-luna`,
extra-high reasoning (`xhigh`), and the exact harness prompt. Each process used
a read-only sandbox; no model requested a tool call, and there were no
substantive retries or added cells. The old R1 GPT-6 records were removed from
`data/decisions.jsonl`; the R1 shards remain in the repository for traceability.
