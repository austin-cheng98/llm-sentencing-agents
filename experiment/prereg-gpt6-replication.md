# Exploratory GPT-6 Luna replication

Registered before collecting R5. This extends the earlier, underpowered GPT-6 collection; it does not replace or alter R1.

## Fixed sample

Collect `peerbare_ng`, `toolbare_ng`, and `peermatch_ng` for P1–P6, S1, S2, H1, and H2 at steps 0–15: 160 decisions per arm, 480 total. Use one fresh GPT-6 Luna sub-agent per cell, one draw per cell, and the frozen `experiment/harness.py` prompt as the entire child instruction. Record raw replies, including format failures, in separate `runs/R5` shards with model tag `gpt6`. Use the harness defaults for decoding and reasoning. No prompt edits, retries for substantive replies, or added cells after results are inspected.

The ten judge IDs are already mapped by `delta_table()` to the existing displacement columns. The primary unit is a judge–case cell, paired across arms. R5 stands alone; R1 records and judge IDs F1/F2 are excluded.

## Estimands and decision criteria

The primary contrast is the structure-matched peer premium: the difference between the `peermatch_ng` and `toolbare_ng` slopes of sentence deviation from the case midpoint on displayed-number displacement. The secondary contrast compares `peerbare_ng` with `toolbare_ng`. Use the frozen estimator in `analysis/robustness.py:premium`: case-clustered standard error and 9,999 within-judge–case label swaps. Report estimates, two-sided randomization p values, 95% confidence intervals, sample sizes, parse failures, and minimum detectable effects (MDE = [1.959963985 + 0.8416212336] × clustered SE).

For precision, compare the primary MDE with the previously observed Opus 5 structure-matched premium of +0.206 and the secondary MDE with the Opus 5 bare-block premium of +0.323. An estimate is deemed adequately powered for its benchmark only if its MDE is no greater than that benchmark. This criterion is evaluated once after the fixed 480-cell collection; no additional cases are added based on the result. Report the point estimate and uncertainty whether or not the criterion is met. This is an exploratory replication, not a confirmatory test of cross-model equivalence.

## Collection and reporting

Follow `experiment/openai-crossmodel-protocol.md` safeguards: no decision in the collector context, no design information in child instructions, one fresh child per cell, default settings, and verbatim raw replies. Record model identity, delegation details, deviations, UTC date range, counts, and failures in `runs/R5/collection-notes.md`. Audit all 480 unique cells before any merge or analysis. Keep R5 separate from `data/decisions.jsonl` until its collection audit is complete.
