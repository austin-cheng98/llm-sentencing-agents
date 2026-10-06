# Civil-damages results across model lineages

This report integrates the Claude Opus 5 D1 study and its preregistered GPT-6
Sol high-reasoning replication, D2. The manuscript reports both in Appendix
`app:damages`. Earlier D1 result memos remain unchanged because their contents
and hashes were frozen; those files describe their status when written.

## Registration and sample history

D1's proximity measures were selected after the initial eight-agent panel had
been examined. That exploratory panel contained 128 matched pairs: in-band
awards were 7/128 under `dpeer_ng` and 62/128 under `dtool_ng`; awards within
two percent of the central figure were 1/128 and 44/128; exact central matches
were 0/128 and 26/128; mean proportional distance from the center was 0.436
and 0.176. The four measures were then registered in
`damages/AMENDMENT-D1-proximity.md` before the two confirming agents, A12 and
A01, were examined. In those 32 pairs, the in-band result was 14/32 versus
26/32 (two-sided exact sign test, p = 0.0042); within-two-percent awards were
10/32 versus 24/32 (p = 0.00052); exact central matches were 2/32 versus 23/32
(p = 9.54e-7). The peer-minus-tool central-distance difference was +0.140
(claim-clustered 95% t interval [0.032, 0.248], MDE 0.142), which the
registered rule classifies as suggestive rather than decisive.

D2 was registered before its first response in
`damages/prereg-D2-gpt6-sol.md`. It used the same 320 D1 cells from ten agents,
all sixteen claims, both primary arms, and prompt hashes matching D1. GPT-6 Sol
at high reasoning returned 319 parseable responses, producing 159 matched
pairs. One `dtool_ng` response for A07, step 3, failed before returning model
output and was not retried. Collection details are in
`runs/D2/collection-notes.md`.

## Matched ten-agent comparison

The D1 column below pools its eight-agent discovery panel and two-agent
confirmation sample. It is descriptive for the proximity measures because
those measures were selected after the first panel was read. D2 is the
registered GPT-6 Sol replication. Differences are peer minus tool; intervals
are 95% claim-clustered t intervals. Binary-outcome p-values are two-sided exact
sign tests over discordant pairs.

| Outcome | Claude Opus 5, D1 (160 pairs) | GPT-6 Sol high, D2 (159 pairs) |
|---|---|---|
| Inside displayed band | Peer 21/160; tool 88/160; difference -0.419 [-0.557, -0.281]; p = 2.17e-18; discordant peer-only/tool-only = 2/69 | Peer 90/159; tool 88/159; difference +0.013 [-0.127, +0.152]; p = 0.871; discordant = 20/18 |
| Distance from central figure | Mean peer 0.392; tool 0.156; difference +0.236 [+0.145, +0.328]; MDE 0.120 | Mean peer 0.274; tool 0.182; difference +0.093 [+0.011, +0.174]; MDE 0.107 |
| Within 2% of central figure | Peer 11/160; tool 68/160; difference -0.356 [-0.485, -0.227]; p = 2.08e-16; discordant = 1/58 | Peer 72/159; tool 73/159; difference -0.006 [-0.101, +0.089]; p = 1.000; discordant = 17/18 |
| Equals central figure | Peer 2/160; tool 49/160; difference -0.294 [-0.390, -0.198]; p = 1.42e-14; discordant = 0/47 | Peer 34/159; tool 43/159; difference -0.057 [-0.152, +0.039]; p = 0.200; discordant = 15/24 |

The primary D2 result does not reproduce D1's large in-band difference: the
observed contrast is small, reverses direction, and is not statistically
decisive. This is not evidence that the arms are equivalent. The central-
distance estimate is positive and its interval excludes zero, but its MDE
exceeds the point estimate, so the registered rule treats it as suggestive
rather than decisive. Neither binary secondary outcome rejects. The strong D1
proximity pattern therefore does not generalize unchanged to this GPT-6 Sol
sample.

## Displacement summaries

The preregistration also requested the frozen pull estimators for continuity.
These are secondary to D2's proximity outcomes. The slope premium is oriented
tool minus peer; all p-values below use the within-agent permutation test.

| Quantity | Claude Opus 5, D1 (n = 320) | GPT-6 Sol high, D2 (n = 319) |
|---|---|---|
| Pooled pull slope | +0.383; 95% z CI [0.185, 0.581]; MDE 0.283; p = 0.0014 | +0.559; 95% z CI [0.344, 0.774]; MDE 0.307; p = 0.0002 |
| Tool-minus-peer slope premium | +0.215; 95% z CI [-0.002, 0.433]; MDE 0.311; p = 0.0712 | +0.232; 95% z CI [0.027, 0.436]; MDE 0.292; p = 0.0341 |

Both runs show a positive pooled response to displacement. The D2 slope premium
has a nominal permutation p-value below 0.05, but its estimate remains below
its MDE; it is not a substitute for the registered proximity outcomes.

## Interpretation and limits

The exact D1 prompts and cell assignments were reused, but model and execution
route changed: D1 used Claude Opus 5 through Claude subagents; D2 used GPT-6 Sol
through Codex CLI. The D1 proximity measures were selected on D1 data, while
D2 was registered before its responses were collected. The D1-D2 comparison is
therefore a registered cross-model replication with a descriptive D1 reference,
not a randomized causal estimate of model identity. The two runs do not show
that the civil-damages proximity result is invariant across model lineages.

## Reproduction

Run `python3 scripts/damages_analysis_d2.py` from the repository root to
recreate `analysis/damages_d2.json`. D2 records remain separate from D1 and
from the core sentencing records in `data/decisions.jsonl`.
