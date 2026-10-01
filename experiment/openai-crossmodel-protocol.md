# Cross-model collection protocol — non-Claude lineage

Paste this whole file into Codex as the task. It collects one additional model
family for the cross-model comparison. Nothing outside `runs/` is written.

You are plumbing, not a participant. Do not reason about the experiment's
content, do not modify prompt text, and do not answer any prompt yourself.

## Why sub-agents and not a direct API call

The existing arms were collected by spawning a fresh sub-agent per decision and
recording its reply verbatim. Collect this family the same way. A family
collected through a bare API call while the others came from sub-agents would
differ from them in two ways at once — model lineage and collection scaffolding —
and the cross-model comparison could not separate the two. Matching the
mechanism is more important here than making any single arm pristine.

## What you are collecting

96 decisions: three arms x two judges x sixteen cases.

| arm | what it shows | judges | steps |
|---|---|---|---|
| `peerbare_ng` | three numbers attributed to other judges | F1, F2 | 0–15 |
| `toolbare_ng` | the same numbers attributed to a statistical forecast | F1, F2 | 0–15 |
| `peermatch_ng` | `peerbare_ng` plus a descriptive sentence matching `toolbare_ng` | F1, F2 | 0–15 |

Use judge IDs **F1 and F2 exactly**. `delta_table()` in `experiment/harness.py`
already reserves them and maps them onto the same displacement columns the
Claude judges used, so the anchors you show are identical to the ones the
existing arms showed. Any other ID raises a KeyError, and inventing one would
break the yoke the whole design rests on.

## Setup

The repository is the artifact snapshot at
`https://anonymous.4open.science/r/llm-sentencing-agents-177D`. Work in a local
checkout of it. Python 3 and numpy only.

```bash
cd <repo>
python3 -c "import numpy; print('ok')"
```

## The judge must never see this protocol

This is the one requirement that can silently invalidate everything. The
sub-agent that decides a case must receive the harness prompt and nothing else.
The prompt itself says it is a research simulation, so the judge does know that
much, and every arm says it equally. What the judge must not know is the
*design*: that arms are being compared, that a second wording of the same block
exists, that the numbers it is shown have been displaced from a midpoint, or that
you are collecting data across cases. Your own context holds all of that, so:

- **Never answer a prompt in your main thread.** Your main thread has read this
  file. A decision produced there is contaminated and unusable.
- **One fresh sub-agent context per decision.** Never reuse a context across
  cells; a judge that has seen an earlier case of this study has seen the design.
- **Pass the prompt as the entire instruction**, byte for byte, with nothing
  before or after it. No framing, no "please answer the following", no mention
  of the study, no tools.

If you have no mechanism for spawning a fresh delegated context per decision,
**stop and report that** rather than answering in the main thread. A partial
collection is recoverable; a contaminated one is not.

Give each sub-agent no tools and no web access. It is an oracle: text in, text
out. Use default decoding and default reasoning settings, and do not override
verbosity or effort. One draw per cell — retry only on a transport error, and
only with the identical request.

Record, in `runs/R1/collection-notes.md`, the exact model id the sub-agents ran,
the delegation mechanism you used, any parameters you could not leave at
default, and the UTC date range of collection. The paper has to state these.

## The loop

For each of the three arms, for each judge in F1, F2, for each step 0 through 15:

1. Fetch the prompt verbatim:

```bash
python3 experiment/harness.py prompt --run R1 --arm ARM --judge JUDGE --step K
```

2. Spawn a fresh sub-agent whose entire instruction is that text.

3. Write the reply verbatim to a temporary file and record it:

```bash
python3 experiment/harness.py record --run R1 --arm ARM --judge JUDGE --step K \
  --model MODELTAG --shard ARM_JUDGE < reply.txt
```

`MODELTAG` is one short lowercase token you use for every call, e.g. `gpt5`. Use
the same tag throughout; the analysis groups on it.

`--shard ARM_JUDGE` keeps each (arm, judge) in its own file, so parallel workers
never write to the same file. Use it.

`record` prints JSON with `"ok": true` when the reply parsed. If `ok` is false,
the sub-agent did not follow the output format. Do not edit the reply to make it
parse, and do not re-ask. Record it as-is, note the cell in
`collection-notes.md`, and move on — a format failure is data.

## Parallelism

These three arms have no history dependence: the prompt for step K does not
depend on any earlier reply. You may run cells concurrently. Keep to at most 5
sub-agents in flight, and give every worker a distinct `--shard`.

Do **not** attempt the `cascade_ng` arm. It is sequential within a case and its
prompts depend on replies already recorded.

## When you are done

```bash
python3 experiment/harness.py status --run R1
```

Expect 96 new records across the three arms. Then report back:

- the contents of `runs/R1/collection-notes.md`
- the per-arm counts and how many have `"ok": false`
- the paths of the `runs/R1/decisions_*.jsonl` shard files

Do not merge the shards into `data/decisions.jsonl`, do not run anything in
`analysis/`, and do not edit any file outside `runs/`. The merge and the
analysis happen elsewhere, against the frozen snapshot.
