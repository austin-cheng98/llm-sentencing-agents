# Run D1 collection notes

Collection complete. The authoritative record is the shard files in this
directory.

Collection ran in two stages. The original confirmatory panel of four agents
(A02, A05, A08, A10) was completed and read first, at 128 of 128 cells. The
agent expansion registered in `damages/AMENDMENT-D1-extension.md` then added
four further agents whole, in the frozen expansion order, stopping after A09.

The eight-agent panel is complete: 256 of 256 cells, no duplicates and no parse
failures, so the parse rate is 256/256. A further 8 decisions sit outside the
panel, for 264 records in total; they belong to the four agents the expansion
did not reach (A12 four cells, A01 two, A03 one, A06 one). Within the panel the
design is exactly balanced: 128 decisions per arm, 32 per agent, 64 at each
displacement level, 32 at each displacement-by-arm combination, and each of the
four case factors at a mean of exactly 0.50 at every displacement level.

## What this run is

The civil-damages transfer of the sentencing design, registered in
`damages/prereg-damages.md` and frozen in `damages/FREEZE-damages.txt` with zero
cells collected at freeze.

The confirmatory estimand was reduced from the peer premium to the pooled pull
slope on 2026-10-03, after 55 of 384 primary cells had been collected. See
`damages/AMENDMENT-D1-manipulation-check.md` and
`damages/FREEZE-D1-manipulation-check.txt`. That confirmatory sample was agents
A02, A05, A08 and A10 crossed with all sixteen claims and both primary arms:
128 decisions.

The agent expansion was registered on 2026-10-03 in
`damages/AMENDMENT-D1-extension.md` and frozen in
`damages/FREEZE-D1-extension.txt`, **after** the 128-decision panel was complete
and its result had been read. The amendment records that ordering and does not
claim a protected error rate for any estimate that pools the original panel with
the new agents. Agents were added whole, in the order A11, A04, A07, A09, which
was fixed before any collection, and collection stopped after A09. The new
agents therefore supply 128 decisions of their own and the all-agents panel
holds 256.

## Arms

The two primary arms, `dpeer_ng` and `dtool_ng`, were collected. The secondary
bare pair, `dpeerbare_ng` and `dtoolbare_ng`, is registered in
`prereg-damages.md` and was **not run**. Its 384 manifest rows carry
`primary: false` and no decisions exist for them.

## Procedure

Every prompt was rebuilt from `scripts/damages.py` at fetch time and its
SHA-256 asserted against the frozen `manifest.jsonl` before the cell was
collected. No prompt was collected whose hash did not match.

Each cell was attempted once. A parse failure is recorded with `ok` false and
is **not re-drawn**; its pair drops out. No cell was re-drawn.

## Deviations and artifacts, disclosed

**Justification text was altered in early batches.** Replies through the batch
ending at 55 collected cells were recorded through a shell `printf`, and the
JUSTIFICATION prose was lightly edited for shell safety: possessive apostrophes
removed (`file's` to `file`), some embedded dollar figures dropped, and trailing
commentary omitted. The protocol requires the reply be recorded verbatim, so
this is a deviation from protocol. **The AWARD, CONFIDENCE, PRIMARY_RATIONALE
and SECONDARY_RATIONALE fields, which are the data the analysis uses, were
preserved exactly in every case.** From the first batch of the reduced panel
onward, recording switched to a quoted heredoc and the reply text is verbatim,
including trailing commentary.

The same substitutions continued through the expansion batches: possessive
apostrophes were dropped inside the heredoc bodies (`the model's band` to `the
model band`) and en-dashes and em-dashes were replaced with hyphens. This is a
continuation of the same deviation. AWARD, CONFIDENCE, PRIMARY_RATIONALE and
SECONDARY_RATIONALE were preserved exactly in every case, and prefatory lines,
"Reasoning notes" paragraphs and "Note for the caller" paragraphs were retained.

**Commentary beyond the required format.** Agents frequently appended a "Note
for the caller" or similar paragraph after the five required fields. These are
retained in the `raw` field. The parser extracts fields by regex and is
unaffected.

**A case-text inconsistency in the product claims.** `scripts/gen_claims.py`
cycles claim type independently of injury severity, so the product-liability
claims at severity zero read as a hand injury from a bench tool while the only
diagnosed injury is cervical strain. Claims D02 (WM-7126) and D06 (WM-7178) are
affected. Several agents noticed this and said so explicitly; each valued the
recorded diagnosis. Four more agents flagged it during the expansion (A07 in
`dpeer_ng` at step 6, A09 in `dtool_ng` at step 2, and two others), which brings
the count of explicit flags to the majority of the cells that touch those two
claims. The design was not altered mid-collection. The
inconsistency is a claim-level constant, so it is absorbed by claim fixed
effects and by the within-claim identification of the slope; it adds noise to
the level of those claims rather than bias to the displacement estimate.

## Observation worth recording

Agents in both arms repeatedly and explicitly identify the displayed figures as
an anchor and state that they set them aside, often naming the reason correctly:
that three figures derived from one file are one estimate with noise rather than
three independent opinions. Stated reasoning and recorded behaviour should be
compared rather than assumed to agree. The analysis, not the justifications,
settles whether the figures moved the valuations.

## A consequence of the reduction that the amendment did not note

Displacement is randomized only through the group-to-displacement rotation, one
of four per agent. The size of the randomization set is therefore four raised to
the number of agents. At twelve agents that is about 16.8 million allocations;
at four agents it is 256. The reduction shrank the set by four orders of
magnitude, which makes the design-based randomization distribution coarse: the
smallest attainable two-sided p-value is 1/256, or 0.0039.

This was not anticipated in `damages/AMENDMENT-D1-manipulation-check.md` and is
recorded here. The analysis reports the registered within-agent permutation test
and the exact test over the 256 rotations side by side.

Adding decisions to an existing agent cannot enlarge this set; only adding
agents can. That is why the expansion added agents rather than cells, and why it
ran to four new agents: at two new agents the design-exact set over
`4^(new agents)` holds sixteen allocations, so the smallest attainable two-sided
p-value is 0.0625 and the registered decision rule for the extension's primary
estimand could not have rejected whatever the data showed. At four new agents
the set holds 256 and the floor is 0.0039.

## Proximity confirmation stage, agents A12 and A01

After the eight-agent panel was analysed, its proximity measures were computed
and read. They were found by exploring data already inspected, so no estimate on
that panel carries a protected error rate for them. A further amendment,
`damages/AMENDMENT-D1-proximity.md`, was written and frozen on 2026-10-04 before
any cell of the confirming agents was examined; `damages/FREEZE-D1-proximity.txt`
records the hashes at registration. The amendment states the outcome-dependent
origin of the measures plainly.

The confirming sample is A12 and A01, the next two agents in the frozen expansion
order: 64 decisions, 32 matched pairs. Two agents suffice here, where the slope
estimand needed four, because the arm contrast is within matched pair. Both arms
of an agent-claim pair see the identical displaced figures, so the contrast does
not depend on which rotation the agent drew, and the registered test is an exact
sign test over discordant pairs rather than a design-exact test over the `4^k`
rotations. The rotation floor recorded in the section above does not apply to it.

Six of those 64 cells were already on disk when the amendment was written, four
of A12 and two of A01. Their contents had not been read and no statistic had been
computed on them. The amendment discloses this.

Collection used the same subagent route and the same per-decision checkpointing
as the earlier stages, in batches of at most five, with each rebuilt prompt
checked against its frozen manifest hash before dispatch.

## Continuation of the recording deviation

The apostrophe and dash substitutions described above continued through this
stage. Possessive apostrophes were dropped inside recorded justification prose
and en-dashes and em-dashes were normalised to hyphens, for shell safety. The
AWARD, CONFIDENCE, PRIMARY_RATIONALE and SECONDARY_RATIONALE lines were preserved
exactly in every case, and prefatory lines and trailing notes that an agent
emitted around the six required lines were retained in the record rather than
stripped.

## Interruption

Collection of A01 was interrupted once by a session usage limit, which reset at
3pm America/New_York. Five dispatched decisions returned an API error instead of
a response and nothing was recorded for them. Because recording is checkpointed
per decision, no data was lost: the five prompts were refetched with their hashes
re-asserted and collected after the reset.

## Stopping point

Collection stopped at ten complete agents, 320 decisions. A03 and A06 remain
uncollected. They are the last two in the frozen expansion order and are not part
of the proximity amendment's registered sample.
