# Amendment to the damages prereg (run D1): reduction to a manipulation check

Registered: 2026-10-03, after 55 of 384 primary cells had been collected and
before any estimate of the peer premium was computed.

## What changes

The confirmatory estimand for run D1 changes from the **peer premium** (the
difference in pull slopes between `dpeer_ng` and `dtool_ng`) to the **pooled pull
slope** (the slope of `dev` on `delta` with the two primary arms pooled).

The confirmatory sample changes from 12 agents x 16 claims x 2 arms (384
decisions) to **4 agents x 16 claims x 2 arms (128 decisions)**, on agents
A02, A05, A08 and A10.

The peer premium becomes a secondary, descriptive quantity. It is reported with
its interval and its minimum detectable effect, and it is not interpreted as
either a replication or a null.

Nothing else changes. The claims, the arms, the displacement grid, the prompts,
the outcome definition, the clustering, and the randomization-inference
procedure are as registered in `prereg-damages.md` and frozen in
`FREEZE-damages.txt`.

## Why

Two reasons, in order of weight.

**The registered design is underpowered for the premium.** The residual spread of
`dev` in this domain, estimated from the first 55 decisions after absorbing
claim, arm, displacement and the displacement-by-arm interaction, is 0.211.
The comparable figure in the sentencing study is about 0.160. Required sample
size scales with the square of that quantity. Projecting forward, a premium
estimate would need roughly 584 decisions to bring its minimum detectable effect
to or below the registered 0.206 benchmark; the 95% interval on the projection
runs from 386 to 985 decisions. At the registered 384 the projected minimum
detectable effect is about 0.254, above the benchmark. By the decision rule in
`prereg-damages.md` that outcome is inconclusive whatever the point estimate, so
completing the registered run as specified would not have answered the question
it was registered to answer.

**Compute.** The account this run is collected on moved to a plan whose rolling
limit admits on the order of one hundred decisions of this kind per window. The
registered 384, let alone the 584 the projection calls for, is not reachable.

The pooled pull slope is a different and much better determined quantity. At 128
decisions its projected minimum detectable effect is 0.220, against a
structure-matched sentencing benchmark of 0.61 (the pooled pull slope in the
no-guideline sentencing arms, `pullPeerN` and `pullToolN`, both 0.61). The
reduced run is therefore well powered for the question it now asks.

## What was and was not inspected before this amendment

Only the residual variance was computed, as a nuisance quantity for the power
projection above. The premium, the per-arm slopes, and the pooled slope were not
estimated, and no outcome-dependent quantity entered the choice to amend.

## Why these four agents

The displacement table assigns each agent all four displacement levels across
four claims each, and the four claims at each level are constructed so that every
one of the four case factors sums to two. Any whole agent crossed with all
sixteen claims is therefore exactly balanced on its own: four claims per
displacement level, and every factor at exactly 0.5 at every level. A subset of
whole agents inherits that balance exactly, so the reduced design retains the
orthogonality of displacement to the case factors that the full design was built
for. This was verified directly rather than assumed.

A subsample taken instead as a prefix of the shuffled manifest does not have this
property. The first 128 manifest tasks run 36 / 31 / 24 / 37 across the four
displacement levels, and documentation completeness reaches 0.67 at one
displacement level against 0.39 at another. That subsample was rejected for that
reason.

A02, A05, A08 and A10 are the four agents with the most cells already collected,
which reuses 27 of the 55 decisions in hand and leaves 101 to collect. Coverage
was determined by a manifest order fixed by seed 20261003 before any collection
began, so the choice of panel is independent of any outcome.

## The 28 off-panel decisions

Twenty-eight of the 55 decisions already collected fall on the eight agents
outside the panel. They remain in `runs/D1/decisions.*.jsonl` and in the release.
They are outside the confirmatory sample and are not pooled into the pooled-slope
estimate. They are available for description and for the secondary premium
estimate.

## Estimator

Outcome `dev = (award - mid) / mid`. The pooled pull slope is the coefficient on
`delta` in a regression of `dev` on `delta` with the two primary arms pooled,
standard errors clustered on claim, and p-values from randomization inference
with B = 9,999 and seed 17, permuting the displacement allocation within agent.
Minimum detectable effect is 2.8015852185999996 times the clustered standard
error.

## Decision rules

The run establishes that displacement moves valuations in this domain if the
pooled slope is positive and its interval excludes zero. It fails to establish it
if the interval contains zero. An interval containing zero is reported as
inconclusive and not as evidence that displacement has no effect.

## What this run cannot settle

It cannot settle whether peer attribution produces more pull than tool
attribution in the damages domain. That is the question the original registration
asked, and the reduced run is not powered for it. The secondary premium estimate
is reported with its minimum detectable effect so that readers can see how little
it constrains. The run also leaves in place the limitations already registered:
one model lineage, one additional domain, no human baseline, and no variation in
the realism of the valuation model's provenance.
