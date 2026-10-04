# Wording rivals peers in LLM judicial decision-making

Code and data for an experiment on how LLM agents respond to numbers attributed to peers. The effect varies with prompt wording and model.

Agents sentence procedurally generated cases. Each agent sees three numbers displaced from the case's correct guideline midpoint by an allocated amount. Arms differ in how the numbers are described and in the surrounding sentences; the displayed numbers are identical across arms.

The displacement is orthogonal to every case factor. The slope of an agent's sentence on the displacement measures how far the agent follows the numbers. We call that slope *pull*. Regression to the mean cannot produce it. When two arms show identical numbers under different attributions, the difference in their slopes is the *peer premium*.

The core dataset contains 4,086 decision records over five models: 1,270 on Claude Opus 5, 160 on Claude Sonnet 5, 160 on Claude Haiku 4.5, 1,248 on GPT-6 Luna, and 1,248 on GPT-6 Sol. Of these, 4,085 contain a parseable sentence. The separate GPT-6 Luna follow-up adds 624 decisions to its primary analysis.

## The result

These nine estimates compare peer attribution with a statistical forecast over identical numbers while the guideline is removed:

| Condition | Model | Premium | p | n |
| --- | --- | ---: | ---: | ---: |
| Bare blocks | Opus 5 | +0.32 | 0.0002 | 128 |
| Structure-matched blocks | Opus 5 | +0.21 | 0.005 | 192 |
| With the original closing lines | Opus 5 | −0.01 | 0.94 | 128 |
| Bare blocks | Haiku 4.5 | +0.12 | 0.036 | 64 |
| Bare blocks | Sonnet 5 | +0.02 | 0.89 | 64 |
| Structure-matched blocks | GPT-6 Luna | +0.22 | <0.001 | 832 |
| Bare blocks | GPT-6 Luna | +0.26 | <0.001 | 832 |
| Structure-matched blocks | GPT-6 Sol | +0.24 | <0.001 | 832 |
| Bare blocks | GPT-6 Sol | +0.11 | <0.001 | 832 |

Both GPT-6 runs use identical prompts, cases, displayed numbers, and displacement assignments. Their structure-matched premiums are similar; the Sol bare-block estimate is smaller than Luna's. Luna used extra-high reasoning and Sol high reasoning, so this difference does not isolate model identity.

## What the wording costs

Adding one closing sentence to the peer block, with the numbers held identical, costs 0.28 of pull (p = 0.002). Two paraphrases cost 0.33 (p < 0.001) and 0.20 (p = 0.016). The instruction, rather than the exact wording, accounts for the change. The matching hedge added to the forecast block leaves pull where it was: +0.05 (p = 0.40).

A premium is a difference of pulls. A sentence added to one block therefore enters with that block's sign, and the three effects account for the premium observed with both sentences in place:

```
Δ_orig = Δ_bare + c_peer − c_fcst = 0.32 + (−0.28) − (0.05) = −0.01
```

## What the revision arms say

**Informational equivalence and stated reliability.** `peereqv_ng` and `tooleqv_ng` carry one identical sentence asserting that both sources saw the same case file and nothing else. `peerrel_ng` and `toolrel_ng` state a matched accuracy figure for each source. Both pairs were pre-registered, hashed and frozen before collection (`experiment/prereg-equivalence.md`, `experiment/FREEZE-equivalence.txt`).

| Pair | Premium | p | 95% CI | MDE | n |
| --- | ---: | ---: | --- | ---: | ---: |
| Informational equivalence | −0.005 | 0.973 | [−0.247, +0.238] | 0.347 | 128 |
| Stated reliability | +0.001 | 0.995 | [−0.272, +0.274] | 0.390 | 128 |

The intervals and MDEs make these results inconclusive rather than null. The registered criterion is each arm's minimum detectable effect, MDE = (z₀.₉₇₅ + z₀.₈₀)·SE ≈ 2.80·SE. This is the premium the arm would reject the null for at 80% power. Both MDEs sit well above the +0.206 benchmark these arms were built to test, and both intervals contain it. The registration forbids extending an arm after seeing its estimate, so these are the results the arms provide.

The equivalence sentence changes how agents use the numbers. It removes an inferential channel, but it also reduces the use of the numbers themselves. Exact reproduction of a displayed number falls by roughly two thirds, the share of sentences landing outside the span of the three displayed numbers rises to 80–84%, and the dispersion of the outcome rises (`analysis/robustness.py`). Agents give the reason without prompting in both arms.

**The structure-matched premium on the smaller models.** `experiment/prereg-balanced.md` and `experiment/FREEZE-balanced.txt` fill the missing cell: the preferred, structure-matched estimate on Sonnet 5 and Haiku 4.5.

| Model | Contrast | Premium | p | 95% CI | MDE | n |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| Sonnet 5 | Structure-matched | −0.14 | 0.48 | [−0.577, +0.293] | 0.622 | 64 |
| Sonnet 5 | Bare | +0.02 | 0.89 | [−0.383, +0.433] | 0.583 | 64 |
| Haiku 4.5 | Structure-matched | −0.01 | 0.89 | [−0.165, +0.141] | 0.219 | 63 |
| Haiku 4.5 | Bare | +0.12 | 0.036 | [−0.009, +0.251] | 0.186 | 64 |

Sonnet 5 is uninformative rather than negative: its MDE is about three times the benchmark, so the arm could not detect the effect it was designed to test. Haiku 4.5 is not a clean null either. Its structure-matched interval lies below the benchmark, but its MDE of 0.219 marginally exceeds the 0.206 it was powered against. By the pre-registered criterion, the arm falls just short. The result is suggestive rather than decisive. The difference between Haiku's bare and structure-matched cells was not pre-registered as a cross-model claim, so we do not report it as one.

**A second lineage.** The GPT-6 Luna sample contains 1,248 decisions across three arms and 26 fresh judge contexts. Collection details are in `experiment/gpt6-protocol.md`.

| Contrast | Premium | p | 95% CI | MDE | Claude benchmark | n |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| Structure-matched | +0.22 | <0.001 | [+0.125, +0.316] | 0.136 | +0.206 | 832 |
| Bare | +0.26 | <0.001 | [+0.159, +0.353] | 0.138 | +0.323 | 832 |

Both estimates are positive and their intervals contain the corresponding Claude benchmark. Their MDEs are below the benchmark values; the intervals still describe uncertainty about cross-model differences rather than prove equivalence.

**Neutral shared-file follow-up.** The explicit same-file sentence above leaves the peer premium inconclusive and reduces number use. A new GPT-6 Luna comparison uses a neutral sentence saying both sources reviewed the case file, without telling the agent the figures add no information. Before examining outcomes, we fixed a balanced subset of 12 cases across all 26 contexts, for 312 matched pairs. The peer premium is +0.250 (randomization p < 0.001; 95% CI [+0.134, +0.365]; MDE 0.161), against the +0.206 benchmark. Number use is higher under peer attribution: slopes are 0.911 versus 0.661; exact matches are 50.6% versus 15.4%; sentences outside the displayed range are 23.1% versus 71.8%. The interval includes the benchmark, so the result supports a positive peer premium under neutral wording but does not establish that its size differs from the earlier estimate.

`runs/R7/decisions.jsonl` contains all 924 recorded responses: the 624 responses in the balanced neutral shared-file sample used by the primary estimate, 67 additional neutral shared-file responses outside the selected steps, and 233 partial explicit-cue responses. The latter 300 records are retained in the raw archive and excluded from confirmatory analysis. The frozen manifest in `runs/R7/manifest.jsonl` records the full 1,664-cell plan.

## The live cascade

Allowing agents to observe one another produces exact copying as well as graded following. In a cascade where six agents decide the same case and each sees its predecessors' actual sentences, 71% of decisions reproduce a predecessor's sentence exactly and five of sixteen cases end unanimous, against a floor of 48% from shuffling independent agents into pseudo speaking orders.

The placebo floor determines which slope we report. `analysis/cascade.py` runs the shuffled placebo under both specifications. Without case fixed effects it returns +0.75, close to the +1.00 observed, so most of the plain slope is floor. With case fixed effects it returns −0.97, the negative sign Angrist (2014) predicts when case dummies place predecessors' outcomes on both sides of a within-case comparison, against +0.55 observed. We report the fixed-effect slope as primary because it clears its own floor by a wide margin.

## What replicates

The surrounding structure recurs across conditions and models. Removing the advisory guideline raises pull in all three Claude models, by 0.36 on Haiku 4.5 to 0.63 on Sonnet 5. Numbers presented as meaningless docketing records, when the prompt calls them irrelevant, move agents by only 0.07.

Removing the guideline also widens between-agent disagreement, from 0.029 to 0.286. That comparison uses different agents across arms, three with the guideline and four without, and it depends on one of those four. Leaving each agent out in turn gives 0.074 to 0.327. The direction holds, but the magnitude does not, so we do not quote a fold-change. `analysis/dispersion.py` computes both figures.

## Round numbers and the confidence scale

Across 3,807 parseable sentences, agents use 93 distinct values; 65% are divisible by six and 42% by twelve. Exact matches to a displayed value occur in 29% of decisions. The rate is 40% when at least one displayed number is divisible by six and 18% when none is, so exact matching alone does not establish copying.

The premium is less affected because both arms see identical numbers; 16.7% of shown values are divisible by six. In Opus 5 records where no shown number is divisible by six, the bare premium is 0.35 (p = 0.007, n = 64) and the structure-matched premium is 0.19 (p = 0.238, n = 96), close to the full-sample estimates of 0.32 and 0.21. The smaller matched sample reduces precision.

Reported confidence does not support the same check. Agents use 4 of its ten values, with 98% a six or a seven. Figure 7 pools Opus 5, Sonnet 5, and Haiku 4.5 as Claude and Luna with Sol as GPT-6 across three shared unguided arms. The pull-confidence correlation across Claude's three pooled arm means (r = −0.93) is descriptive, not a calibrated measure; GPT-6 is shown outside the fitted line. This pooling is for descriptive confidence and exact-adoption comparisons; peer-premium estimates remain model-specific.

## Layout

```
cases/generate.py               builds the 16 factorial vignettes and the decision sequence
experiment/harness.py           builds prompts, parses and records decisions
experiment/status.py            which cells of an arm are still missing
experiment/protocol.md          the collection protocol given to each data-collection worker
experiment/cascade-protocol.md  the sequential protocol for the live-cascade arm
experiment/gpt6-protocol.md              collection details for the GPT-6 Luna sample
experiment/prereg-gpt6-luna.md             registration for the GPT-6 Luna sample
experiment/prereg-gpt6-sol-replication.md registration and collection plan for GPT-6 Sol
experiment/collect_gpt6_sol.py             frozen GPT-6 Sol collector and audit
experiment/FREEZE-gpt6-sol.txt             input and prompt-manifest hashes for R8
experiment/prompts.txt                     prompts shared by the matched GPT-6 runs
experiment/prereg-equivalence.md          pre-registration, equivalence and reliability arms
experiment/prereg-r7-source-access.md    registration for the neutral shared-file follow-up
experiment/AMENDMENT-R7-*.md              launch and outcome-blind sample amendments
experiment/r7_source_access.py            collect and analyze the R7 follow-up
experiment/prereg-equivalence-diffs.txt   the exact prompt deltas those arms introduce
experiment/prereg-balanced.md             pre-registration, structure-matched small-model cells
experiment/FREEZE-*.txt                   original SHA-256 freeze records
experiment/FREEZE-VERIFICATION.md          status of frozen and amended code hashes
experiment/frozen/harness-balanced-equivalence.py
                                             source snapshot used by two freezes
experiment/RELEASE-CODE-CHECKSUMS.txt      hashes for current released analysis code

analysis/common.py        loading, OLS, cluster-robust covariance, wild cluster bootstrap
analysis/anchoring.py     pull by arm, the peer premium, the guideline effect
analysis/inference.py     the yoked contrasts, three clustering units, placebo floors
analysis/trailer.py       the closing-sentence contrasts and the per-model breakdown
analysis/randomization.py inference by permuting the displacement allocation
analysis/framing.py       the three attributions, and behavior with no numbers shown
analysis/memory.py        arms where agents see a summary of their own past decisions
analysis/crossmodel.py    the same estimates per agent model
analysis/cascade.py       the live cascade: herding, position effects, convergence
analysis/dispersion.py    between-agent spread, and how far it rests on any one agent
analysis/confidence.py    reported confidence and exact adoption, arm by arm
analysis/robustness.py    round numbers, displacement magnitude, log and rank rescaling
analysis/equivalence.py   the informational-equivalence and stated-reliability arms
analysis/balanced.py      the structure-matched premium on the smaller models
analysis/crosslineage.py  the second lineage against the Claude benchmarks
analysis/power.py         minimum detectable effect per contrast
analysis/integrity.py     verifies the yoke held and the design stayed balanced
analysis/run_all.py       runs every analysis in order
analysis/out_*.json       what each analysis writes; the figures read these

figures/figstyle.py       shared plotting style
figures/fig_forest.py     nine estimates of one quantity
figures/fig_sentences.py  what each closing sentence costs, numbers held identical
figures/fig_models.py     pull per model, guideline present and removed
figures/fig_main.py       pull against displacement, by attribution
figures/fig_cascade.py    convergence and the collapse of disagreement
figures/fig_design.py     the displaced anchors and the two labels
figures/fig_confidence.py confidence against pull, and exact adoption
figures/fig_factors.py    the legal content of the cases, with and without a guideline
figures/make_all.py       rebuilds all eight

data/decisions.jsonl      4,086 decision records, one JSON object each, with raw model output
data/repeats.jsonl        the cells collected twice, used for the decoding-noise floor
data/cases.json            the 16 vignettes
data/sequence.json        the displacement allocation
runs/R7/                   source-access follow-up manifest, responses, and notes
runs/R8/                   GPT-6 Sol manifest, attempts, decisions, and audit
analysis/out_r7_source_access.json        primary follow-up estimates
```

## Reproducing

```
pip install -r requirements.txt
python analysis/run_all.py
python figures/make_all.py
```

Core decision records and model replies are in `data/decisions.jsonl`; the 68 cells drawn twice are
in `data/repeats.jsonl` with both draws. The R7 source-access follow-up and the frozen R8 Sol
manifest, attempt log, and decisions are retained in their run directories.

The GPT-6 Luna sample registration and collection details are in
`experiment/prereg-gpt6-luna.md` and `experiment/gpt6-protocol.md`. The R8 GPT-6 Sol collection
plan is in `experiment/prereg-gpt6-sol-replication.md`. The R7 sample-selection
amendments are in `experiment/AMENDMENT-R7-primary-sample.md` and
`experiment/AMENDMENT-R7-power-target.md`.

`run_all.py` reads the core decisions and `runs/R7/decisions.jsonl`, recomputes the reported estimates and LaTeX macros, and calls no model. The bootstrap and permutation steps use fixed seeds, so the numbers are stable across runs.

`make_all.py` then rebuilds all eight figures from the JSON that step wrote; run it second.

Rebuilding the case set:

```
python cases/generate.py
```

The generator asserts its invariants. It refuses to emit a design in which the advisory range correlates with a discretionary factor, in which offense types are unbalanced against any factor, or in which the two case blocks differ in composition.

Freeze records preserve the code and design hashes as registered. Later amendments may supersede a frozen hash; see `experiment/FREEZE-VERIFICATION.md` for the status of each reported mismatch. Verify the current released analysis code with:

```
shasum -a 256 -c experiment/RELEASE-CODE-CHECKSUMS.txt
```

## Collecting new decisions

The harness never calls a model. It prints a prompt and accepts raw text back:

```
python experiment/harness.py prompt --run R1 --arm peerbare_ng --judge P1 --step 5
python experiment/harness.py record --run R1 --arm peerbare_ng --judge P1 --step 5 \
    --model opus5 --shard peerbare_ng_P1 < reply.txt
```

The harness keeps model access external, so a run can be replayed, audited, or re-scored without querying anything. `experiment/protocol.md` is the instruction sheet used to drive the loop. Every arm here, including the second lineage, was collected in a fresh model context per decision and recorded verbatim. The collection scaffolding is therefore consistent across arms.

## Data fields

Each record carries the arm, agent, model, case identifier, the four case factors, the advisory range, the displacement applied, the numbers shown, the parsed sentence and rationale, and the model's verbatim reply. Records are keyed by `(model, arm, judge, step)`.

`dev` is the outcome used throughout: the sentence's proportional deviation from the case's guideline midpoint, which puts cases with different ranges on one scale.

## Noise floors

`analysis/inference.py` reports three noise floors, and they are not interchangeable.

- **Design null.** Swapping the arm label within an agent-by-case cell gives the exact null for a yoked contrast. Its 95th percentile runs from 0.12 to 0.18 depending on the contrast, and each contrast is read against its own.
- **Between-agent floor.** Splitting one arm's agents in half gives a 95th percentile of 0.264 over 44 splits. That bounds a between-agent comparison. These contrasts do not cross agents.
- **Decoding noise.** Repeat draws on a byte-identical prompt differ by a within-cell standard deviation of 0.064, over the cells in `data/repeats.jsonl`.

Contrasts keep only agents present in both arms, so every cell is paired and the label-swap null matches the estimator. The second lineage carries no label-swap null, and the figure draws its two rows without a design-null band.
