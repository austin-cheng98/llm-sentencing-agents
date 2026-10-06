# Pre-registration: GPT-6 Sol replication of the damages study

Registered 2026-10-04, before any GPT-6 Sol response is collected. D2 is a
separate model replication of the completed D1 primary-arm sample. It does not
alter D1.

## Fixed sample and prompts

Collect the same 320 primary-arm cells observed in D1: agents A02, A05, A08,
A10, A11, A04, A07, A09, A12, and A01; all 16 claims; and arms `dpeer_ng` and
`dtool_ng`. This gives 160 matched agent-claim pairs. The two partial D1 cells
from A03 and A06 are excluded, as are the uncollected bare arms.

Every prompt is rebuilt with the frozen `scripts/damages.py` and `cases/claims.json`.
Its SHA-256 must match the corresponding D1 manifest entry. This holds claim
wording, arm, displayed numbers, displacement, formatting, and the model's
instruction exactly constant across D1 and D2. The D2 task order is the D1
manifest order restricted to these cells.

## Collection

Use `gpt-6-sol` at reasoning effort `high`. Run one fresh, ephemeral Codex CLI
context per cell in a read-only sandbox. The rendered study prompt is the entire
user prompt, with no added framing. Use the CLI's default decoding settings; do
not use tools, browse, or consult other cells. Record each final reply verbatim
and retain the prompt hash, model, effort, and call status. Each cell gets one
model-reaching attempt; do not replace a refusal, malformed reply, or other
substantive response. A call that fails before returning a model response is
recorded as a collection failure and is not silently replaced.

The controlled input is the exact D1 prompt and cell assignment. The requested
model and reasoning effort change. The provider-specific execution route also
differs from D1's Claude subagent route and is recorded as a limitation of this
cross-model comparison.

## Outcomes

The primary outcome is whether an award falls inside the displayed band,
inclusive. Compare the two arms within matched pairs using a two-sided exact
sign test on discordant pairs; the predicted direction is more in-band awards
under `dtool_ng`.

The prespecified secondary outcomes are: proportional distance from the central
displayed figure (paired difference, peer minus tool, with claim-clustered
uncertainty); whether the award is within two percent of the central figure; and
whether it equals that figure exactly. The latter two use the same exact paired
sign test. Report all four outcomes and their sample counts, including
discordant-pair counts and parse failures.

For continuity, also report the pooled pull slope and the peer-minus-tool slope
premium using the frozen D1 outcome and estimator definitions. These are
secondary summaries and do not replace or redefine the proximity outcomes.
No interim outcome analysis, sample expansion, or paper edit is part of this
run.
