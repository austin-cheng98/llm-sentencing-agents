# Amendment — completing the cross-model displacement cells

## Relation to the existing registration

`experiment/prereg-balanced.md` registered the structure-matched arm on the two
smaller models and closed with a commitment this amendment overrides:

> An underpowered estimate is reported as underpowered, with its MDE, and is not
> repaired by collecting more.

That commitment is set aside here, and the reason is known in advance: the
underpowered estimates have been computed and read. The decision to collect more
therefore follows from the outcome, and no estimate computed on the enlarged
sample carries a protected error rate. The registered 32-against-32 estimate is
reported unchanged beside the enlarged one, and the enlarged one is labelled as
outcome-dependent wherever it appears. This amendment does not revise the
original estimate and does not withdraw it.

## What is incomplete

The cross-model arms are not internally balanced. `peerbare_ng`, `peermatch_ng`
and `toolbare_ng` carry both cross-model agents, 32 decisions each per model. The
four displacement arms carry only the first agent, 16 decisions each:

| arm | S1 | S2 | H1 | H2 |
|---|---|---|---|---|
| `peerbare_ng` | 16 | 16 | 16 | 16 |
| `peermatch_ng` | 16 | 16 | 16 | 16 |
| `toolbare_ng` | 16 | 16 | 16 | 16 |
| `peerdelta` | 16 | 0 | 16 | 0 |
| `peerdelta_ng` | 16 | 0 | 16 | 0 |
| `tooldelta` | 16 | 0 | 16 | 0 |
| `tooldelta_ng` | 16 | 0 | 16 | 0 |

Each model therefore stands at 160 decisions, and four of its seven arms rest on
one agent rather than two. A one-agent arm admits no between-agent contrast and
its cluster-robust errors rest on a single column of the displacement table.

## Sample, fixed in advance

The second cross-model agent on the four displacement arms, all sixteen cases,
one draw per cell: 64 decisions per model, 128 in total. This brings every arm of
both models to 32 and both models to 224.

No agent is added. `delta_table()` reserves exactly two cross-model columns per
model, `alias = {"S1": 0, "S2": 1, "H1": 0, "H2": 1, ...}`, mapping S1 and H1
onto P1's displacements and S2 and H2 onto P2's. 224 is the ceiling the design
permits without altering that table. The Opus contrast draws on six columns and
576 decisions on these arms, so the cross-model samples remain smaller than the
Opus sample by a factor the design fixes, and the completed arms are still
expected to be underpowered against the +0.206 Opus estimate. The reason to
complete them is balance, not power: it removes the one-agent arms and makes the
seven arms of each model mutually comparable at equal n.

The anchors shown are the ones the design already assigns. S2 and H2 inherit P2's
displacement column, so the yoke stays exact and the prompts are the ones the
frozen harness builds. No prompt text changes.

## Model identity

Haiku is collected on Claude Haiku 4.5, `claude-haiku-4-5-20251001`, the model
already recorded under the `haiku45` label. The identity matches.

Sonnet is not collected under this amendment. The collection route available in
this session serves Claude Sonnet 5.5, `claude-sonnet-5-5`, and the existing
cells are labelled `sonnet5`. Adding 5.5 decisions to a `sonnet5` arm would mix
two model versions inside one arm, and the resulting cross-model comparison would
not be the comparison the paper reports. The 64 Sonnet cells stay uncollected
until the version is pinned. If they are later collected on Sonnet 5.5 rather
than Sonnet 5, they are recorded under a separate model label and reported as a
third model, not merged.

As in every earlier stage, the `model` field is a label supplied to the record
command and not provenance returned by the API. The harness has no field for a
returned model id, and hardening that would require changing a frozen file, so it
is a change for a later run and not a retrofit to this one.

## Estimator

Unchanged and already written. `analysis/crossmodel.py` for the per-model
estimates, `analysis/robustness.py:premium` for the difference in the slope of
`dev` on `delta` between arms, 9,999 randomization draws with labels swapped
within agent-case cells, standard errors clustered on case, and
`analysis/power.py` for the minimum detectable effect of every contrast. No
estimator, clustering choice or seed is altered.

## What will not happen

No prompt text changes after collection starts. Parse failures are recorded as
data and are not re-drawn. No cell is added and no agent extended after the
estimates are computed. The Opus estimates are not revised in light of these. The
displacement grid, the case set and the sequence are untouched. Decoding and
reasoning settings stay at default, one draw per cell.
