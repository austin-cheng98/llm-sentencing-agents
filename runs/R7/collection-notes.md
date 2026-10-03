# R7 collection status

Collection session: 2026-10-03T15:26:50Z to 2026-10-03T15:46:44Z.

GPT-6 Luna (`gpt-6-luna`) was called in fresh Codex CLI processes at xhigh reasoning effort, with a
read-only sandbox. The frozen manifest in `manifest.jsonl` contains 1,664 cells. The confirmatory
sample is the 312 matched judge-case pairs in steps 0, 1, 2, 5, 6, 7, 8, 10, 11, 12, 13 and 15 for
`peeraccess_ng` and `toolaccess_ng`, fixed before outcomes were inspected; each selected cell was
attempted once, with no replacement draws. All 624 responses in those pairs parsed successfully, and
there were no tool calls. Raw replies, prompt hashes and parse outcomes are in `decisions.jsonl`.

`decisions.jsonl` retains all 924 recorded responses: the 624 fixed-sample responses used by the confirmatory analysis, 67 additional neutral shared-file responses outside the selected steps, and 233 partial explicit-cue responses. The latter 300 responses are excluded from confirmatory analysis. `experiment/AMENDMENT-R7-primary-sample.md` and `experiment/AMENDMENT-R7-power-target.md` document the sample selection and amendment.
