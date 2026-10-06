# Results of the agent expansion, run D1

Not written into the paper. This file records what the expansion found, on the
terms the amendment set.

The expansion is registered in `damages/AMENDMENT-D1-extension.md` and frozen in
`damages/FREEZE-D1-extension.txt`. It was registered after the 128-decision
panel was complete and its result had been read. Four agents were added whole,
in the frozen expansion order A11, A04, A07, A09, and collection stopped there.
The analysis is `scripts/damages_analysis_ext.py`, writing
`analysis/damages_d1_ext.json`. `scripts/damages_analysis.py` and
`analysis/damages_d1.json` are frozen and were not modified; the extension
analysis imports their estimators unchanged.

## Why four new agents and not two

Displacement is randomized only through the group-to-displacement rotation, one
of four per agent, so the randomization set holds four raised to the number of
agents. The amendment registered the design-exact test over `4^(new agents)` as
the p-value for the primary estimand. At two new agents that set holds sixteen
allocations and the smallest attainable two-sided p-value is 0.0625, so the
registered decision rule could not have rejected whatever the data showed. At
four new agents the set holds 256 and the floor is 0.0039. Adding decisions to
an existing agent cannot enlarge the set; only adding agents can.

## Estimand 1, the primary: pooled pull slope on the new agents only

These four agents were never inspected before the amendment was registered,
their rotations are independent of the original panel's, and the specification
was fixed before the first new draw.

| quantity | value |
|---|---|
| pooled slope | +0.384 |
| clustered SE | 0.088 |
| t | +4.34 |
| 95% CI, normal | [+0.211, +0.557] |
| 95% CI, t on 15 df | [+0.196, +0.572] |
| MDE | 0.248 |
| benchmark (sentencing, no guideline) | 0.61 |
| n | 128 |
| G (clusters) | 16 |

p-values: **design-exact over the 256 rotations = 0.0195, the registered
p-value**; within-agent permutation (B = 9,999, seed 17) = 0.0012; wild cluster
bootstrap = 0.0008.

The registered decision rule for this estimand requires a positive slope, an
interval excluding zero, and a design-exact rejection at the two-sided 5 percent
level. All three hold. The estimand is established on its own terms.

**The claim-fixed-effects specification qualifies this.** With claim fixed
effects in place of the four case factors the slope is +0.386 (SE 0.103, 95% CI
[+0.184, +0.587], MDE 0.288), so the interval still excludes zero, but the
design-exact p-value is 0.0586 and does not reject at 5 percent. On the
amendment's own language that specification is suggestive and not decisive. The
registered specification is the one with the four factors as linear controls,
which is what the sentencing pull slope uses, and the headline result stands on
it; the fixed-effects result is reported because it sits on the other side of
the threshold and the reader should see that.

For comparison, the original 128-decision panel gave +0.277 (SE 0.109) with a
design-exact p of 0.1094, which was recorded in `damages/RESULTS-D1.md` as
suggestive rather than decisive. The new agents give a larger slope with a
smaller standard error, and their design-exact test rejects.

## Estimand 2: pooled slope on all eight agents

| quantity | value |
|---|---|
| pooled slope | +0.330 |
| clustered SE | 0.101 |
| t | +3.27 |
| 95% CI, normal | [+0.132, +0.528] |
| 95% CI, t on 15 df | [+0.115, +0.546] |
| MDE | 0.283 |
| n | 256 |

Within-agent permutation p = 0.0051; wild cluster bootstrap p = 0.0057. With
claim fixed effects the slope is +0.330 (SE 0.103, CI [+0.128, +0.533],
p = 0.0055).

This is the most precise summary of the collected decisions. The decision to
extend followed reading the original panel's result, so this estimate does not
carry a protected Type I error rate and its p-values are descriptive. The
design-exact set here holds 4^8 = 65,536 allocations and was not enumerated.

## Estimand 3, confirmatory: exact matches to the central displayed figure

Registered as a prediction that exact matches occur in `dtool_ng` and not in
`dpeer_ng`, tested by a two-sided exact sign test on the discordant matched
agent-claim pairs. On the new agents:

| | value |
|---|---|
| `dpeer_ng` exact matches | 0 of 64 |
| `dtool_ng` exact matches | 11 of 64 |
| matched pairs | 64 |
| both arms | 0 |
| peer only | 0 |
| tool only | 11 |
| exact two-sided sign test | p = 0.000977 |

The discordant pairs fall entirely in the predicted direction and the test
rejects at 5 percent, so the estimand is confirmed. The eleven matches are
(`dtool_ng`, A04, 11, $258,000), (A07, 6, $70,100), (A09, 0, $42,000),
(A09, 3, $64,600), (A09, 6, $107,200), (A09, 7, $123,500), (A09, 9, $358,800),
(A09, 11, $349,000), (A11, 4, $52,500), (A11, 11, $212,400),
(A11, 15, $436,400).

Across all eight agents, descriptively: 0 of 128 in `dpeer_ng` and 26 of 128 in
`dtool_ng`, 26 discordant pairs, sign-test p below 1e-6.

This was the one exploratory observation in `damages/RESULTS-D1.md` that the
amendment promoted to a confirmatory test on never-inspected agents, and it
replicated. A valuation that equals the displayed central figure to the dollar
is a different behaviour from a valuation that merely sits near it, and it
appears only when the figures are attributed to a model.

## Estimand 4, secondary: the peer premium

| sample | peer minus tool | SE | 95% CI | p | MDE |
|---|---|---|---|---|---|
| new agents | -0.280 | 0.145 | [-0.565, +0.005] | 0.0728 within-agent, 0.0977 design-exact | 0.407 |
| all agents | -0.226 | 0.123 | [-0.466, +0.015] | 0.0821 within-agent | 0.344 |

The benchmark is 0.206, the structure-matched sentencing premium. The MDE
exceeds the benchmark in both samples, so neither is a test the benchmark could
have passed. Reported with its interval and its MDE, and not interpreted as
either a replication or a null. The interval is wide and sits mostly below zero,
which is the direction opposite to the sentencing result, but a sign read off an
interval that contains zero in a sample whose MDE is twice the benchmark is not
a finding.

The per-arm slopes are descriptive: on the new agents `dpeer_ng` is +0.244
(SE 0.094) and `dtool_ng` is +0.524 (SE 0.117); across all agents `dpeer_ng` is
+0.218 (SE 0.081) and `dtool_ng` is +0.443 (SE 0.148).

## Spread, for the record

Residual sd with claim fixed effects, arm, displacement and the interaction, all
agents: 0.2057. sd(dev) = 0.3288. mean(dev) = -0.3054. Valuations sit well below
the advisory midpoint on average in both arms, and the pull estimate is a
within-claim slope, not a level.

## What this run still cannot settle

Whether peer attribution produces more pull than tool attribution in the damages
domain. One model lineage, one additional domain, no human baseline, and no
variation in the realism of the valuation model's provenance. The all-agents
estimate is the most precise number here and is also the one whose error rate is
not protected; the protected number is the new-agents-only estimate, and it is
the one that should be quoted if either is.
