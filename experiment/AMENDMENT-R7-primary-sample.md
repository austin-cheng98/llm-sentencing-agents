# R7 sample-size amendment: balanced primary sample

Issued 2026-10-03T15:23:38+00:00, before outcome analysis. The current response values were not inspected; only completion counts and parse status were used to plan the remaining collection.

## Sample and collection

The original frozen R7 manifest and preregistration remain unchanged. To avoid completing two optional wording arms, the confirmatory target is reduced from 416 to 208 matched judge-case pairs for the neutral shared-file comparison (`peeraccess_ng` versus `toolaccess_ng`). The selected steps are 0, 2, 5, 7, 8, 11, 12, and 15 (C00, C05, C10, C15, C01, C07, C08, C14): four baseline and four main cases, with each of the four case factors balanced within each phase and a full-rank main-effects design. All 26 contexts are retained.

At amendment time, 462 responses were recorded: 115 `peeraccess_ng`, 114 `toolaccess_ng`, 138 `peereqv_ng`, and 95 `tooleqv_ng`; all 462 parsed successfully. In the selected primary sample, 57 responses per arm were already recorded. The collector will attempt each selected primary cell once, with no replacement draws. Existing responses outside the selected steps and all partial explicit-cue responses remain in `runs/R7/decisions.jsonl`; they are excluded from confirmatory analysis. The partial explicit-cue comparison will not be estimated.

## Precision rationale

The reduced target is 208 matched pairs (416 total primary responses), half the original primary sample. Scaling the prior GPT-6 variance calibration by the square root of two gives an approximate t-corrected 80%-power MDE of 0.205, close to the +0.206 benchmark. This is a planning estimate from a different prompt condition, not a guarantee. The smaller sample has wider uncertainty and less power for effects below that benchmark. The target will not be expanded in response to interim outcomes.

The collection and analysis implementation for this amendment has SHA-256 `fe0b8d3eb23e7cf6f9a60e7f30c008e28c2c38db175520915218788f661895b8`.
