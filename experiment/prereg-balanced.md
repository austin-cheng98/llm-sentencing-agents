# Pre-registration — structure-matched premium on the smaller models

## Question

The structure-matched premium exists only on Opus 5. `peermatch_ng` adds to the
peer block a descriptive sentence matching the one `toolbare_ng` carries, so the
two blocks differ in attribution and not in length or register. Reviewer qnHK
objected that the paper's conclusions are stronger than its cross-model
evidence, and they are right in a specific way: the premium is measured on three
models with bare blocks, but the preferred, structure-matched estimate is
measured on one. This collects the missing cell.

## Arms and sample, fixed in advance

`peermatch_ng` on `sonnet5` (judges S1, S2) and on `haiku45` (judges H1, H2),
all sixteen cases, one draw per cell. 64 decisions, 32 per model.

`delta_table()` already reserves S1, S2, H1, H2 and maps them onto the same
displacement columns the existing `peerbare_ng` and `toolbare_ng` records for
those models used, so the anchors shown are identical to the ones those arms
showed. The comparison partner, `toolbare_ng`, is already collected at 32 per
model and is not re-collected or altered.

No cell will be added and no judge extended after the estimate is computed. At
32 against 32 this arm is smaller than the Opus contrast and will very likely be
underpowered against the +0.206 Opus estimate. That is the honest state of the
evidence and the reason for the arm: the paper currently has no structure-matched
number at all for these models. An underpowered estimate is reported as
underpowered, with its MDE, and is not repaired by collecting more.

## Estimator

Unchanged and already written: `analysis/crossmodel.py` and
`analysis/robustness.py:premium`, the difference in the slope of `dev` on
`delta` between arms, 9,999 randomization draws, labels swapped within
agent-case cells, standard errors clustered on case. `analysis/power.py` reports
the MDE for every contrast including these.

## What will not happen

No prompt text changes after collection starts. Parse failures are recorded as
data, not re-drawn. The existing Opus estimate is not revised in light of these.
Decoding and reasoning settings stay at default; one draw per cell.
