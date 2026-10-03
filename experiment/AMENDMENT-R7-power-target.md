# R7 sample-size amendment: power target

Issued 2026-10-03T15:26:13Z, before outcome analysis. This amendment supersedes the 208-pair target in `AMENDMENT-R7-primary-sample.md`; the original preregistration and both amendments remain in the record.

The target is 312 matched judge-case pairs (624 decisions) for the neutral shared-file contrast, across all 26 contexts. Use steps 0, 1, 2, 5, 6, 7, 8, 10, 11, 12, 13, and 15: six baseline and six main cases, with each of the four case factors balanced within each phase and a full-rank main-effects design. Each selected cell is attempted once; no replacement draws or outcome-based sample expansion.

At this amendment, 487 R7 responses had been recorded. The selected sample held 97 `peeraccess_ng` and 90 `toolaccess_ng` responses; all parsed successfully. The 25 responses generated during the initial 208-pair continuation are retained. No outcome values were examined. The remaining explicit-cue arms (138 `peereqv_ng`, 95 `tooleqv_ng`) stay in the raw data but will not be analyzed because collection was stopped before their planned sample was complete. Responses outside the selected steps also remain in the raw file and are excluded from the primary analysis.

The prior GPT-6 variance calibration (SE 0.0487 at 416 pairs) projects SE 0.0562 and a t-corrected 80%-power MDE of 0.167 at 312 pairs. Under that calibration, estimated power for the +0.206 benchmark is about 93%. This is a planning projection from a different prompt condition; report the completed sample's uncertainty and MDE, and treat a larger observed MDE as inconclusive.

Collection and analysis implementation SHA-256: `02511c96e161b0a4e7ab2063915f8a951764512ba586f75d2d5a9602bb7584b6`. This amended code hash supersedes the collector hash in the original freeze; the original prompt, manifest, and input hashes remain unchanged.
