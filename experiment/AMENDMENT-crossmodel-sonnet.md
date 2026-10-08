# Amendment: Sonnet collection route for the cross-model completion stage

## Relation to the existing registration

`experiment/AMENDMENT-crossmodel-completion.md` registered 128 cells: the second
cross-model agent on `peerdelta`, `peerdelta_ng`, `tooldelta` and `tooldelta_ng`,
all sixteen cases, one draw per cell, 64 per model. Its "Model identity" section
recorded that the 64 Haiku cells were collected on `claude-haiku-4-5-20251001`
and that the 64 Sonnet cells were not collected, because the only available route
served `claude-sonnet-5-5` while the existing `sonnet5` cells were drawn from
Claude Sonnet 5, and mixing two versions inside one arm would not be the
comparison the paper reports.

A route serving `claude-sonnet-5` became available after that amendment was
frozen. This amendment records that the 64 Sonnet cells are now collected on
that route, under the `sonnet5` label, as the original amendment registered them.

Nothing about the registered sample changes. The arms, the agent, the sixteen
cases, the one draw per cell, the prompts and the estimator are the ones already
registered. The 128 prompt hashes in
`runs/R1/manifest-crossmodel-completion.jsonl` were frozen before any cell of
this stage was collected and are unchanged; each Sonnet dispatch asserts its
rebuilt prompt against that file before it is sent, as the Haiku dispatches did.

The expansion remains outcome-dependent for the reason given in the original
amendment: the underpowered 32-against-32 estimates had already been read when
the decision to complete the arms was taken. No estimate on the enlarged sample
carries a protected error rate. The registered 32-against-32 estimate is
reported unchanged beside the enlarged one and is labelled outcome-dependent
wherever it appears.

## Model identity

The route is an agent definition pinned by model id. Asked to state its identity
before any cell was collected, it returned `NAME: Claude Sonnet 5` and
`ID: claude-sonnet-5`. That id matches the model the existing `sonnet5` cells
were drawn from, so the completed cells and the original cells sit in one arm.

As in the original amendment, the `model` field written into each record is a
label supplied to the record command, not provenance returned by the API. The
harness has no field for a returned model id, and adding one would change a
frozen file. The identity check above is the evidence for the label, and it is
an identity the model reported about itself.

## Parse failures

One Haiku cell of this stage, `peerdelta_ng` step 1, returned a refusal to answer
rather than a decision. It is recorded with `ok: false` and its raw text, as the
original amendment requires: parse failures are recorded as data and are not
re-drawn. It is excluded from the estimates by the same `ok` filter every other
analysis in the project uses, and the count is reported.

## What will not happen

No prompt text changes after collection starts. No cell is added and no agent is
extended after the estimates are computed. The Opus estimates are not revised.
The displacement grid, the case set and the sequence are untouched. Decoding and
reasoning settings stay at default, one draw per cell. 224 per model remains the
ceiling the design permits, for the reason recorded in the original amendment.
