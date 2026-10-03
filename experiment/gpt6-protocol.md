# GPT-6 Luna collection

The sample contains 1,248 decisions: 26 fresh judge contexts, 16 cases, and
three no-guideline arms (`peerbare_ng`, `toolbare_ng`, and `peermatch_ng`).
Each context received one prompt per cell. Prompts came from
`experiment/harness.py`; replies were recorded verbatim in `runs/R6`.

The model was GPT-6 Luna (`gpt-6-luna`). Three cells used the collaboration
runner. The remaining cells used fresh local Codex processes at extra-high
reasoning effort. All 1,248 replies parsed successfully, with no substantive
retries or added cells. Collection counts and dates are in
`runs/R6/collection-notes.md`.

The primary estimate compares `peermatch_ng` with `toolbare_ng`; the secondary
estimate compares `peerbare_ng` with `toolbare_ng`. Both use sentence deviation
from the case midpoint regressed on displayed-number displacement, with
case-clustered uncertainty and label swaps within judge--case pairs.
