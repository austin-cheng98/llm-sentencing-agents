# Amendment 2 to run D1: extension to further agents

Registered 2026-10-03, after the 128-decision confirmatory panel was complete and
its result was computed and read. That ordering is the central fact about this
amendment and determines its structure.

## What prompted it

The first amendment reduced the confirmatory sample to four agents. Displacement
is randomized only through the group-to-displacement rotation, four choices per
agent, so the randomization set holds four raised to the number of agents. At four
agents that is 256 allocations and the smallest attainable two-sided p-value is
1/256, or 0.0039. The registered within-agent permutation test returned 0.030, the
exact test over the 256 rotations returned 0.109, and the observed statistic ranked
thirteenth of 256.

The binding constraint is the number of agents, not the number of decisions. Adding
decisions to the four existing agents cannot enlarge the randomization set, because
each agent contributes one rotation however many claims it sees. Only further
agents can.

## What was seen before this amendment was written

Everything in `damages/RESULTS-D1.md`: the pooled slope, both randomization tests,
the per-arm slopes, the secondary premium, and the exploratory exact-match
comparison. The decision to extend is therefore outcome-dependent, and a pooled
estimate over old and new agents does not carry a protected Type I error rate. This
amendment does not pretend otherwise. It instead specifies an extension whose
primary test is valid despite the ordering.

## Design of the extension

Agents are added whole: sixteen claims by both primary arms, thirty-two decisions
each. A whole agent is exactly balanced on displacement and on all four case
factors by construction, so every stopping point is a balanced panel and a run
halted by compute remains analysable.

The expansion order is fixed here, before any further collection:

    A11, A04, A07, A09, A12, A01, A03, A06

The order is by cells already collected, descending, which is a function of
manifest order. Manifest order was fixed by seed 20261003 before any decision was
collected, so the order is independent of outcomes. Collection stops at the last
complete agent the available compute allows. A stop forced by a usage limit is
independent of the data.

Nothing else changes: the sixteen claims, the two primary arms, the displacement
grid, the prompts, the outcome definition, clustering on claim, and the
randomization-inference procedure are all as frozen.

## Estimands

The registered 128-decision result stands as reported and is not revised,
recomputed, or replaced by anything below.

1. Primary for this extension: the pooled pull slope on the **new agents only**.
   These agents were never inspected, their rotations are independent of the first
   panel's, and the specification was fixed before their first decision was drawn.
   The design-exact randomization test over four raised to the number of new agents
   is a valid test and is the registered p-value for this estimand.

2. The pooled pull slope on **all agents**, as the most precise available summary.
   Reported with the explicit note that the decision to extend followed a result,
   so its p-value is descriptive and its Type I error rate is not protected.

3. New confirmatory estimand, promoted from exploration. In the first panel,
   fifteen of sixty-four tool-arm valuations equalled the central displayed figure
   exactly and none of the sixty-four peer-arm valuations did. The prediction for
   the new agents, fixed here before they are run, is that exact matches to the
   central displayed figure occur in `dtool_ng` and not in `dpeer_ng`. The test is
   an exact sign test on the discordant matched agent-claim pairs, two-sided. This
   is a directional prediction registered in advance on agents not yet drawn, so
   on the new agents it is confirmatory rather than exploratory.

4. The peer premium remains secondary and is reported with its interval and its
   minimum detectable effect, not interpreted as either a replication or a null.

## Decision rules

For estimand 1, displacement is established as moving valuations if the slope is
positive, the interval excludes zero, and the design-exact randomization test
rejects at the two-sided five percent level. An interval containing zero is
reported as inconclusive and not as evidence that displacement has no effect. A
design-exact test that does not reject, alongside an interval that excludes zero,
is reported as suggestive and not as decisive, in those words.

For estimand 3, the prediction is confirmed if the discordant pairs fall in the
predicted direction and the sign test rejects at the two-sided five percent level.
A split in the predicted direction that does not reach that level is reported as
directionally consistent and not statistically decisive.

## What the extension still cannot settle

Whether peer attribution produces more pull than tool attribution in damages; the
premium's minimum detectable effect is reported so readers can see how little any
panel reachable here constrains it. One model lineage, one additional domain, no
human baseline, and no variation in the realism of the valuation model's
provenance.
