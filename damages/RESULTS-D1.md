# Run D1 results: the damages manipulation check

Not written into the paper. This file records what the run found, as registered
in `damages/prereg-damages.md` and amended in
`damages/AMENDMENT-D1-manipulation-check.md`. Produced by
`scripts/damages_analysis.py`; machine-readable output in
`analysis/damages_d1.json`.

Sample: 128 decisions, agents A02, A05, A08 and A10 crossed with sixteen claims
and the two primary arms. No parse failures, no duplicates, exact balance on
displacement and on all four case factors. A further 28 decisions were collected
outside the panel and are excluded from the confirmatory estimate.

## Confirmatory: the pooled pull slope

Specification: `dev` on displacement with the arms pooled, an arm indicator, and
the four case factors; standard errors clustered on claim, sixteen clusters.

| quantity | value |
|---|---|
| pooled slope | +0.277 |
| clustered SE | 0.109 |
| t | +2.54 |
| 95 percent interval, normal | [+0.064, +0.490] |
| 95 percent interval, t on 15 df | [+0.045, +0.509] |
| MDE | 0.305 |
| benchmark, sentencing no-guideline arms | 0.61 |

p-values:

| test | p |
|---|---|
| registered: within-agent permutation, B = 9,999, seed 17 | 0.0301 |
| exact over the 256 rotations the design actually samples | 0.1094 |
| wild cluster bootstrap, the paper's house method | 0.0261 |

With claim fixed effects in place of the four factors the slope is +0.248 (SE
0.122), interval [+0.010, +0.487], p = 0.0486, MDE 0.341.

By the registered decision rule the slope is positive and the interval excludes
zero under both the normal and the t critical value, so the run establishes that
displacement moves valuations in the damages domain.

That conclusion carries one qualification that the amendment did not anticipate.
Displacement is randomized only through the group-to-displacement rotation, four
per agent, so with four agents the randomization set holds 256 allocations and
the smallest attainable two-sided p-value is 0.0039. The exact test over that
set returns 0.109 two-sided and 0.051 one-sided: the observed statistic is
thirteenth from the top of 256. The registered permutation test draws from a
much larger set than the design sampled from. The interval-based rule is met and
the design-exact randomization test is not, so the result is suggestive rather
than decisive, and it should be read that way.

## Descriptive: slopes within each arm

| arm | n | slope | SE | 95 percent interval |
|---|---|---|---|---|
| `dpeer_ng` | 64 | +0.192 | 0.088 | [+0.019, +0.364] |
| `dtool_ng` | 64 | +0.363 | 0.175 | [+0.019, +0.706] |

Mean `dev` is -0.415 in the peer arm and -0.209 in the tool arm, so valuations
sit well below the advisory midpoint in both. Mean `dev` rises monotonically
across the three lower displacement levels, from -0.414 at -0.30 to -0.238 at
+0.15, and is -0.257 at +0.30.

## Secondary: the peer premium

Peer minus tool is -0.171 with a clustered SE of 0.173, interval [-0.511,
+0.169], p = 0.343 by randomization inference. The MDE is 0.485 against a
benchmark of 0.206, so the MDE is more than twice the effect the run would need
to detect. The estimate is uninformative rather than negative, and it is not
interpreted as either a replication or a null. The point estimate happens to be
negative, which would mean more pull from tool attribution than from peer
attribution, the reverse of the sentencing result; the interval is far too wide
to support that reading.

## Exploratory, not registered

Fifteen of the 64 tool-arm valuations land exactly on the central displayed
figure. None of the 64 peer-arm valuations do. The design matches agents and
claims across arms, so these are 64 matched pairs with fifteen discordant on
this outcome, all in the same direction; an exact sign test on the discordant
pairs gives p = 0.00006.

This was not registered and the comparison was found after the confirmatory
estimate, so it is a hypothesis for a future run rather than a finding. It is
also worth noting against the justification text: agents in both arms repeatedly
state that they treated the displayed figures as an anchor and set them aside,
including in several of the fifteen decisions that reproduce the central figure
exactly. Stated reasoning and recorded behaviour should be compared rather than
assumed to agree.

## What this run cannot settle

Whether peer attribution produces more pull than tool attribution in damages.
The limitations of the sentencing design carry over: one model lineage, one
additional domain, no human baseline, and no variation in the realism of the
valuation model's provenance.
