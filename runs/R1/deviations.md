# Deviations from `experiment/openai-crossmodel-protocol.md` — R1 (gpt6)

Recorded on merge, from `runs/R1/collection-notes.md` and from checks run against
the frozen harness. Nothing here was repaired after the fact; the records are as
collected.

## 1. The prompt was not the entire instruction

The protocol requires the prompt be passed "byte for byte, with nothing before or
after it." The collecting session prefixed each child's instruction with
`Do not use tools or access the web.` The Claude-lineage arms carried no such
prefix. So the cross-lineage contrast differs from the Claude arms in the model
family **and** in one line of instruction, and the two cannot be separated.

The prefix says nothing about the design — not that arms are compared, not that
the displayed numbers are displaced, not that data is being collected — so the
blinding requirement that the protocol calls load-bearing is intact. But a
reader is entitled to know the arms were not instruction-identical.

## 2. The model identity is self-reported, not verified

The collecting session reported itself as GPT-6; the spawn interface never
exposed the child's backend model identifier. All 96 records carry the tag
`gpt6` because that tag was requested, not because it was confirmed. Any claim
about *which* non-Claude model this is rests on the collecting session's own
report.

## 3. The no-tools instruction was unenforceable

The interface offered no way to disable tools or web access, so the instruction
was prompt-level only. Whether any child used a tool is unknown.

## 4. One cell was collected twice over

A count audit found `peerbare_ng/F2` step 1 missing. It was collected in a fresh
child context and recorded before collection continued. This is a re-draw of a
cell that produced no record, not a re-draw of a recorded answer.

## What was verified here

- 96 records, 16 steps (0-15) in each of the six arm x judge cells, no gaps.
- Record schema identical, key for key, to `data/decisions.jsonl`.
- For every record, the three anchor values and the block header match what the
  frozen `harness.py` generates for that `(arm, judge, step)`. The displayed
  numbers are the same ones the Claude judges saw.
- `dev` recomputes exactly as `(sentence - mid) / mid` in all 96 records.
- `ok` is true in all 96; no parse failures.
