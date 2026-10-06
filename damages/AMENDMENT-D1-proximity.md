# Amendment to run D1: proximity to the displayed anchor as the arm contrast

Registered 2026-10-04, before any cell of agents A12 and A01 was examined.

## What prompted it

The secondary premium — the difference in pull slopes between `dpeer_ng` and
`dtool_ng` — cannot be settled within this design. At the eight-agent panel its
minimum detectable effect is 0.344 against a point estimate of 0.226 and a
benchmark of 0.206. Completing all twelve agents would bring the MDE only to
0.281, and reaching the benchmark would require about 714 decisions, or
twenty-two agents, in a design that has twelve. A paired-difference estimator
was tried and gives no material gain, because the within-pair correlation of
`dev` across arms is 0.53 and differencing removes little of the variance. The
slope premium is therefore closed, and `damages/RESULTS-D1-extension.md` records
it as uninformative rather than negative.

The slope is not the only way to ask whether one attribution moves valuations
more than the other. It asks whether the award moves further per unit of
displacement, which is a derivative estimated across four displacement levels
and is correspondingly noisy. A direct question is available: does the award end
up near the figures that were displayed? That is measured on each observation
rather than across levels, and the matched design makes it a within-pair
contrast, because both arms of an agent-claim pair see identical figures.

Exploring the eight-agent panel on that question returned large differences.
This amendment registers them for confirmation on agents that have not been
examined.

## What was seen before this amendment was written

Everything in `damages/RESULTS-D1.md` and
`damages/RESULTS-D1-extension.md`, plus the following proximity measures
computed on the 128 matched pairs of the eight-agent panel: the award equals the
central displayed figure (peer 0, tool 26); the award equals any displayed
figure (peer 0, tool 26); the award falls inside the displayed band (peer 7,
tool 62); the award is within two percent of the central figure (peer 1, tool
44); and the mean proportional distance from the central figure (peer 0.436,
tool 0.176). The measures other than the exact-match count were not registered
anywhere before being computed. The exact-match count was registered as estimand
3 of `damages/AMENDMENT-D1-extension.md` and was confirmed there.

The choice of these measures is therefore outcome-dependent, and no estimate
computed on the eight-agent panel carries a protected Type I error rate for
them. This amendment does not pretend otherwise. It fixes the measures, the
direction, the test and the sample before the confirming decisions are read.

## Sample

Agents A12 and A01, the next two in the expansion order frozen in
`damages/FREEZE-D1-extension.txt` (A11, A04, A07, A09, A12, A01, A03, A06), each
crossed with all sixteen claims and both primary arms: 64 decisions, 32 matched
pairs. Agents are added whole, so the panel stays exactly balanced on
displacement and on all four case factors.

Six of those 64 cells were already on disk when this amendment was written: four
of A12 and two of A01, collected under the same frozen prompts and the same
frozen manifest. Their contents have never been read and no statistic has been
computed on them; they were excluded from every analysis reported so far, all of
which restricted to the eight complete agents. They are disclosed here rather
than discarded.

Claims, arms, displacement grid, prompts, outcome and clustering are unchanged.
A stop forced by a usage limit is independent of the data.

## Why two agents suffices here, when the slope needed four

The arm contrast is within matched pair. Both arms of a pair see the same
displaced figures, so the contrast does not depend on which
group-to-displacement rotation an agent drew. The registered test is therefore
an exact sign test over discordant pairs, whose reference set is 2 raised to the
number of discordant pairs, not 4 raised to the number of agents. The coarseness
that forced the slope estimand to four new agents does not apply. At
thirty-two pairs the sign test can reach p-values far below 0.05, and at the
observed discordance rate it is expected to.

## Estimands

1. **Primary.** The award falls inside the displayed band, low to high
   inclusive. Predicted to occur more often in `dtool_ng` than in `dpeer_ng`.
   Tested by a two-sided exact sign test on the discordant matched pairs.

2. **Confirmatory.** The mean paired difference in proportional distance from
   the central displayed figure, peer minus tool, estimated as the intercept of
   the paired difference with standard errors clustered on claim. Predicted
   positive, meaning peer-arm awards sit further from the displayed figure.
   Reported with its interval and its minimum detectable effect.

3. **Confirmatory.** The award is within two percent of the central displayed
   figure. Predicted more often in `dtool_ng`. Same sign test.

4. **Replication.** The award equals the central displayed figure exactly.
   Predicted more often in `dtool_ng`. Same sign test. This repeats estimand 3
   of `damages/AMENDMENT-D1-extension.md` on new agents.

The pull slope and the slope premium are reported again on the enlarged panel
for continuity. Neither is a target of this amendment, and the slope premium
remains uninformative rather than negative.

## Decision rules

Estimand 1 is established if the discordant pairs fall in the predicted
direction and the sign test rejects two-sided at 5 percent. If the direction
holds but the test does not reject, the result is reported as directionally
consistent and not statistically decisive, in those words. If the direction
reverses, that is reported plainly as a failure to replicate.

Estimand 2 is established if the paired difference is positive and its interval
excludes zero. An interval containing zero is reported as inconclusive and not
as evidence that the arms are alike. If the interval excludes zero while the
minimum detectable effect exceeds the estimate, the result is reported as
suggestive rather than decisive.

Estimands 3 and 4 follow the rule for estimand 1.

## What this cannot settle

Whether the difference reflects greater trust in a model's output or only
greater willingness to adopt a number presented as a computation. One model
lineage, one additional domain, no human baseline, and no variation in the
realism of the valuation model's provenance. It also cannot settle the slope
premium, which stays closed, so a finding here is a claim about where awards
land relative to the displayed figures and not about sensitivity to
displacement.
