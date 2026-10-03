# R6 collection notes

R6 is the GPT-6 Luna sample used in the reported analysis.

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
parsed successfully. Three cells used the collaboration runner; the remaining
cells used fresh local Codex processes with model `gpt-6-luna`, extra-high
reasoning (`xhigh`), and the exact harness prompt. Each process used a
read-only sandbox; no model requested a tool call, and there were no
substantive retries or added cells.
