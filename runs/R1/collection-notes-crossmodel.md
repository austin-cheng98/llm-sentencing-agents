# Collection notes: cross-model completion stage

Registered by `experiment/AMENDMENT-crossmodel-completion.md` (Haiku route) and
`experiment/AMENDMENT-crossmodel-sonnet.md` (Sonnet route). Prompt hashes frozen
in `runs/R1/manifest-crossmodel-completion.jsonl` before any cell was collected.

## Sample

128 cells: the second cross-model agent (H2, S2) on `peerdelta`, `peerdelta_ng`,
`tooldelta`, `tooldelta_ng`, all sixteen cases, one draw per cell. 64 per model.
All 128 were attempted. Every dispatch rebuilt its prompt with the frozen harness
and asserted the SHA-256 against the manifest before the prompt was sent; no
dispatch was sent whose hash did not match.

Realized usable cells:

| arm | sonnet5 (S2) | haiku45 (H2) |
| --- | --- | --- |
| peerdelta | 16 | 16 |
| peerdelta_ng | 16 | 13 |
| tooldelta | 16 | 14 |
| tooldelta_ng | 16 | 14 |
| total | 64 | 57 |

Sonnet reached the registered 64 of 64. Haiku returned 57 decisions and 7
refusals. On the seven shared cross-model arms this brings `sonnet5` to 224, the
ceiling the design permits, and `haiku45` to 216 of a possible 224.

## Order

Sonnet first, all four arms, in batches of at most five cells. Haiku second, in
the arm order `peerdelta`, `peerdelta_ng`, `tooldelta`, `tooldelta_ng`, steps
ascending within each arm. No cell was collected twice and no cell was re-drawn.

## Model identity

Both routes were asked to state their identity before any cell of their stage was
collected.

- Sonnet: an agent definition pinned by model id, which returned
  `NAME: Claude Sonnet 5` and `ID: claude-sonnet-5`. That id matches the model the
  existing `sonnet5` cells were drawn from, so the completed and original cells
  sit in one arm.
- Haiku: the general subagent route with the model set to Haiku, which returned
  `Claude Haiku 4.5` and `claude-haiku-4-5-20251001`, matching the existing
  `haiku45` cells.

As recorded in both amendments, the `model` field written into each record is a
label supplied to the record command, not provenance returned by the API. The
harness has no field for a returned model id, and adding one would change a
frozen file. The identity checks above are the evidence for the labels, and they
are identities the models reported about themselves.

## Refusals

Seven Haiku cells returned a refusal to answer rather than a decision. Each is
recorded with `ok: false` and its raw refusal text, and none was re-drawn, as the
registration requires. They are excluded from the estimates by the same `ok`
filter every other analysis in the project uses.

| arm | step | case |
| --- | --- | --- |
| peerdelta_ng | 1 | C03 |
| peerdelta_ng | 3 | C06 |
| peerdelta_ng | 10 | C04 |
| tooldelta | 8 | C01 |
| tooldelta | 13 | C11 |
| tooldelta_ng | 0 | C00 |
| tooldelta_ng | 11 | C07 |

Separately, one earlier Haiku cell outside this stage, `peermatch_ng` H2 step 1
(C03), is recorded `ok: false` for a format failure rather than a refusal: the
reply gave the sentence, confidence and both rationales as prose instead of the
six labelled lines, and it was not re-drawn. It is the eighth non-usable record
in the merged file, and it is why `haiku45` reaches 216 rather than 217 on the
seven shared arms.

`experiment/AMENDMENT-crossmodel-sonnet.md` says "One Haiku cell" refused. That
was the count when that amendment was frozen, before the remaining Haiku cells
were collected. The frozen file was not edited. Seven is the final count, and it
is the number the paper reports.

The refusals come from the subagent wrapper's own system prompt, not from the
model's judgment about sentencing: the wrapper is a general coding agent, and the
refusal texts object to the no-tools instruction and to the research framing
rather than to the case. The Sonnet route, an agent definition with no tools,
refused none of its 64 dispatches. The wrapper was deliberately not changed
part-way through the Haiku arm: swapping the instrument to reduce the refusal
rate, after the refusals had been seen, is the kind of outcome-dependent change
the registration forbids.

Two consequences are worth stating plainly. First, `haiku45` reaches 216 rather
than 224 on the shared arms, and `peerdelta_ng` has 13 rather than 16 usable
Haiku cells in the completion stage. Second, the refusals are not spread evenly
across cases, and the wrapper saw the case text, so whether a cell refused may not
be independent of case content. That is a selection concern about which Haiku
cells are missing, not a demonstrated bias in the cells that remain. It is not
something the realized sample can settle.

## Response form

Three returned decisions were not bare six-line blocks.

- `peerdelta` S2 step 12 and `tooldelta_ng` S2 step 1 wrapped the six lines in a
  short sentence of surrounding prose. Both were recorded verbatim, including the
  wrapper, and both parsed.
- `tooldelta_ng` H2 step 5 was first handed back as a prose summary of the
  decision rather than the formatted lines. The agent was asked once to reproduce
  its answer verbatim and returned the six lines, which agree with the summary it
  had already given (68 months, confidence 7, PROPORTIONALITY / DETERRENCE). The
  verbatim block is what is recorded. No decision was requested a second time and
  no sentence was changed.

One further cell, `tooldelta_ng` H2 step 0, ended without delivering a report at
all. It was asked once to deliver what it had produced, and returned a refusal,
which is the text recorded for that cell.

## Deviations

Apostrophes and dashes inside JUSTIFICATION prose are recorded as typed by the
agent except where a character had to be substituted for shell safety; the
substitutions are confined to punctuation and never change a sentence, a number
or a rationale word.
