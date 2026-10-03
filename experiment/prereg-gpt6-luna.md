# GPT-6 Luna sample

## Fixed sample

Collect `peerbare_ng`, `toolbare_ng`, and `peermatch_ng` for 26 fresh judge IDs:
P1--P6, S1--S2, H1--H2, and G01--G16, at steps 0--15. This is 1,248
judge--case decisions (26 judges x 3 arms x 16 cases). Use one fresh GPT-6 Luna
context per cell, one draw per cell, and the frozen `experiment/harness.py`
prompt as the entire child instruction. Contexts may be launched through the
collaboration runner or an isolated local Codex process; both are fresh model
contexts. Record raw replies, including format failures, in
`data/decisions.jsonl` under run `R6` and model tag `gpt6`. Use the harness defaults for
decoding and reasoning. Do not add cells after inspecting results.

The judge IDs reuse the fixed displacement columns through `delta_table()`; this
keeps the case design and displayed-number assignment unchanged. The primary
unit is a judge--case cell, paired across arms.

## Estimands and reporting

The primary contrast is the structure-matched peer premium: the difference
between the `peermatch_ng` and `toolbare_ng` slopes of sentence deviation from
the case midpoint on displayed-number displacement. The secondary contrast
compares `peerbare_ng` with `toolbare_ng`. Use the frozen estimator in
`analysis/robustness.py:premium`: case-clustered standard error and 9,999
within-judge--case label swaps. Report estimates, two-sided randomization p
values, 95% confidence intervals, sample sizes, parse failures, and minimum
detectable effects (MDE = [1.959963985 + 0.8416212336] x clustered SE).

For precision, compare the primary MDE with the Opus 5 structure-matched
premium of +0.206 and the secondary MDE with the Opus 5 bare-block premium of
+0.323. Report the point estimate and uncertainty regardless of whether the
MDE is below its benchmark. This sample estimates the registered contrasts; it does not establish cross-model
equivalence by itself.

## Collection and audit

Follow `experiment/gpt6-protocol.md`: no decision in the collector context, no
design information in child instructions, one fresh child per cell, default
settings, and verbatim raw replies. Collection details are reported there. Audit
all 1,248 cells before regenerating analyses.
