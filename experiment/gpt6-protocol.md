# GPT-6 Luna collection

The sample contains 1,248 decisions: 26 fresh judge contexts, 16 cases, and
three no-guideline arms (`peerbare_ng`, `toolbare_ng`, and `peermatch_ng`).
Each context received one prompt per cell. Prompts came from
`experiment/harness.py`, and replies were recorded verbatim; the records are in
`data/decisions.jsonl` under model tag `gpt6`.

The model was GPT-6 Luna (`gpt-6-luna`). Collection ran from 2026-10-03 01:30
to 02:13 UTC and produced 1,248 unique records: 416 per arm, 26 judges per arm,
and 16 cases per judge. Three cells used the collaboration runner; the rest used
fresh local Codex processes at extra-high reasoning effort (`xhigh`) with the
exact harness prompt, each in a read-only sandbox. No model requested a tool
call. All 1,248 replies parsed successfully, with no substantive retries and no
added cells.

The primary estimate compares `peermatch_ng` with `toolbare_ng`; the secondary
estimate compares `peerbare_ng` with `toolbare_ng`. Both use sentence deviation
from the case midpoint regressed on displayed-number displacement, with
case-clustered uncertainty and label swaps within judge--case pairs.
