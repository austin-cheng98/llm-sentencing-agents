# Pre-registration: informational equivalence and stated reliability

Frozen before any decision in these arms was collected. The freeze record, with
the SHA-256 of this file and of the two files that generate the prompts and
compute the result, is `experiment/FREEZE-equivalence.txt`.

## The question

The peer premium contrasts two anchor blocks that differ in who the numbers are
attributed to. Nothing in the earlier arms holds constant how much the source
could plausibly know: a bench of judges has seen a case, a fitted model has seen
a table. The premium is therefore consistent with two readings — that attribution
to peers moves the decision, or that peers are taken to hold better information.
The earlier design cannot separate them.

These arms separate them by assertion.

## Arms

Four new arms, all with the advisory range removed (`_ng`), all showing the same
three displaced numbers the existing arms show for the same judge and case, from
the same `delta_table()` in `experiment/harness.py`.

| arm | block |
|---|---|
| `peereqv_ng` | peer header, equivalence sentence, three judge rows |
| `tooleqv_ng` | forecast header, equivalence sentence, three prediction rows |
| `peerrel_ng` | as `peereqv_ng`, plus the reliability sentence |
| `toolrel_ng` | as `tooleqv_ng`, plus the reliability sentence |

The equivalence sentence, identical in all four arms and quoted here as the
harness emits it:

> These figures were produced from the same case file you have been given, and
> from no other information about this defendant or this offense.

The reliability sentence, identical in `peerrel_ng` and `toolrel_ng`:

> In past cases of this type these figures have been close to the sentence
> ultimately imposed.

Within each pair the two prompts differ in exactly two places: the header line,
and the three row labels. Both differences carry attribution and nothing else.
The rendered diffs are in `experiment/prereg-equivalence-diffs.txt`, frozen with
this file.

The phrase "these figures" is slightly stilted applied to sentences a judge
entered. That is deliberate: a phrasing natural to each source would reintroduce
a wording difference, which is the thing being controlled.

## Sample, fixed in advance

Agents P1, P2, P3, P4 on all sixteen cases, in each of the four arms: 256
decisions, 64 per arm. Primary model `opus5`, one draw per cell.

Four agents rather than six because the structure-matched contrast reached a
standard error of 0.079 on six agents and the bare contrast reached 0.047 on
four; four is expected to detect the benchmark below and costs less. **No cell
will be added, and no agent extended, after the primary result is computed.** If
the arm turns out underpowered the result is reported as inconclusive, not as a
null, and not repaired by collecting more.

## Primary test

One test. The premium in the equivalence pair: the coefficient on
displacement × arm in an OLS of deviation on displacement, arm, their product,
and the four case factors, over agents present in both arms, with the
label-swap randomisation null that `analysis/robustness.py:premium` implements
(9,999 draws, seed 17, labels swapped within agent-case cells). Standard errors
cluster on case. Implemented in `analysis/equivalence.py`, frozen with this file.

Benchmark: the structure-matched premium already measured on this model,
**+0.206**. The equivalence blocks are structure-matched, so that is the estimate
they should be read against, not the larger bare-block +0.323.

Decision rule, in the order the script applies it:

1. estimate positive and randomisation p < 0.05 → **confirmed**: the premium
   survives an explicit statement that both sources saw the same case file and
   nothing else, so it is not deference to better information.
2. otherwise, if the minimum detectable effect exceeds +0.206 → **inconclusive**.
3. otherwise, if the upper confidence limit falls below +0.206 → **refuted**:
   equalising stated information shrinks the premium.
4. otherwise → null, but consistent with the benchmark.

## Secondary tests, also fixed in advance

Reported whatever they show, and labelled secondary.

- the premium in the reliability pair, same estimator;
- within each source type, the change in pull from adding the reliability
  sentence: `peerrel_ng` against `peereqv_ng`, and `toolrel_ng` against
  `tooleqv_ng`, same estimator with the sentence rather than the source as the
  contrast.

Nothing else. Any further cut of these decisions is exploratory and will be
called that.

## What will not happen

- No decision will be dropped except by the integrity rule already in
  `analysis/common.py:load`, which drops records that failed to parse and
  deduplicates on (model, arm, judge, step). That rule predates these arms.
- No prompt text will be changed after collection starts. If a prompt is found
  defective the arm is abandoned and reported as abandoned.
- A cell whose reply does not parse is recorded as a parse failure and counted.
  It is not re-drawn.
- The primary test will not be swapped for a secondary one, or for a different
  outcome scale, if it disappoints. The log-ratio and within-case-rank scales
  exist in `analysis/robustness.py` and may be reported, as exploratory.

## Collection

Fresh agent context per decision, the harness prompt as its entire instruction,
reply recorded verbatim, at most five in flight. `experiment/protocol.md` has
the mechanism. Collection shards to `runs/`, and is merged into
`data/decisions.jsonl` only after all 256 cells are attempted.
