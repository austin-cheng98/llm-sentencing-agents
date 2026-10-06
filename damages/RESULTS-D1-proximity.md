# Results: proximity confirmation, damages run D1

Not written into the paper.

Registered in `damages/AMENDMENT-D1-proximity.md`, frozen by
`damages/FREEZE-D1-proximity.txt` before any cell of the two confirming agents
was examined. Analysis script `scripts/damages_analysis_prox.py`, output
`analysis/damages_d1_prox.json`.

## What was being settled

The slope premium could not be settled. At the eight-agent panel its minimum
detectable effect was 0.344 against a point estimate of 0.226 and a benchmark of
0.206; completing all twelve agents would reach only 0.281, and reaching the
benchmark would need about 714 decisions, or twenty-two agents, in a design that
has twelve. `damages/RESULTS-D1-extension.md` records it as uninformative rather
than negative, and this amendment does not reopen it.

The amendment instead tests a different channel. The slope asks whether the
award moves more per unit of displacement, a derivative estimated from noise.
Proximity asks whether the award lands near the figure that was shown, measured
on each observation directly. The arm contrast is within matched pair: both arms
of an agent-claim pair see the identical displaced figures, so the contrast does
not depend on which group-to-displacement rotation the agent drew. The
registered test is an exact sign test over discordant pairs, with reference set
2 raised to the number of discordant pairs, and the 4^k rotation floor that
governs the displacement estimands does not apply to it. Two confirming agents
therefore suffice where the slope needed four.

## Sample

A12 and A01, the next two agents in the frozen expansion order: 64 decisions,
32 matched pairs, 16 claim clusters. Six of those 64 cells were already on disk
when the amendment was written, four of A12 and two of A01; their contents had
not been read and no statistic had been computed on them. Both agents are
complete, so the sample is exactly balanced on displacement and on all four case
factors.

## Estimand 1, primary: the award falls inside the displayed band

`dpeer_ng` 14 of 32, `dtool_ng` 26 of 32. Twelve pairs concordant and inside,
two peer-only, fourteen tool-only, sixteen discordant. Two-sided exact sign test
p = 0.0042.

Direction holds and the test rejects. Confirmed.

## Estimand 2, confirmatory: proportional distance from the central figure

Mean distance `dpeer_ng` 0.2170, `dtool_ng` 0.0770. Paired difference, peer minus
tool, estimated as the intercept of the within-pair difference with standard
errors clustered on claim: +0.1400, clustered se 0.0507, t = +2.76, G = 16.
95 percent interval on the normal [+0.0407, +0.2393], on t with 15 degrees of
freedom [+0.0320, +0.2480]. MDE 0.1420.

The interval excludes zero while the minimum detectable effect, 0.1420, exceeds
the estimate, 0.1400. Under the registered rule this is suggestive rather than
decisive.

## Estimand 3, confirmatory: the award falls within two percent of the central figure

`dpeer_ng` 10 of 32, `dtool_ng` 24 of 32. Nine concordant, one peer-only, fifteen
tool-only, sixteen discordant. Two-sided exact sign test p = 0.00052.

Direction holds and the test rejects. Confirmed.

## Estimand 4, replication: the award equals the central figure exactly

`dpeer_ng` 2 of 32, `dtool_ng` 23 of 32. Two concordant, no peer-only, twenty-one
tool-only, twenty-one discordant. Two-sided exact sign test p = 9.5e-07, which is
the smallest value attainable at twenty-one discordant pairs.

Direction holds and the test rejects. This replicates estimand 3 of the extension
amendment, which found 0 of 64 against 11 of 64 on the previous new agents, on a
sample that was not inspected before the test was registered.

## How the confirming agents differ from the exploratory panel

The levels moved substantially; the ordering did not.

| measure | panel peer | panel tool | confirming peer | confirming tool |
|---|---|---|---|---|
| inside the displayed band | 7/128 | 62/128 | 14/32 | 26/32 |
| within two percent of central | 1/128 | 44/128 | 10/32 | 24/32 |
| equals central exactly | 0/128 | 26/128 | 2/32 | 23/32 |
| mean distance from central | 0.436 | 0.176 | 0.217 | 0.077 |

The peer arm of the confirming agents lands inside the band far more often than
the panel's peer arm did, and produced the study's first two exact peer matches.
The paired gap in proportional distance is correspondingly about half the size
the panel suggested: +0.140 here against +0.260 there. The exploratory panel
therefore overstated the magnitude of the gap, which is the expected consequence
of selecting the measures on it. The direction is the same in every one of the
four estimands, and three of the four reject on a sample chosen before the
measures were applied to it.

## Continuity: the displacement estimands on the enlarged panel

Reported for continuity only. Neither is a target of this amendment, and neither
carries a protected error rate at this panel size, because the decision to extend
followed from reading earlier results.

Ten agents, n = 320, G = 16. Pull slope +0.383, clustered se 0.101, t = +3.80,
95 percent interval [+0.185, +0.581], MDE 0.283, p from the within-agent
permutation 0.0014.

Premium +0.215, clustered se 0.111, t = +1.94, 95 percent interval on the normal
[-0.002, +0.433], on t with 15 degrees of freedom [-0.022, +0.452], MDE 0.311,
p from the within-agent permutation 0.0712.

The premium's sign reversed between panels: it was -0.226 at eight agents and is
+0.215 at ten, with intervals that both contain zero and minimum detectable
effects, 0.344 and 0.311, that exceed the benchmark of 0.206 and both point
estimates. The estimator is not merely imprecise, it is sign-unstable at this
sample size. That is further reason to leave the slope premium as uninformative
rather than negative, in those words, and not to read a direction into it.

## What this cannot settle

The measures were found by exploring the eight-agent panel, and the amendment
says so. Confirmation on two fresh agents protects the error rate of the four
registered tests; it does not make the measures the ones that would have been
chosen in advance.

The result distinguishes where an award lands relative to a displayed figure. It
does not distinguish trust in the label from willingness to adopt a number that
arrives already computed. One model lineage, one additional domain, no human
baseline, and no variation in the valuation model's stated provenance realism.
The slope premium stays closed.
