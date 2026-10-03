# R7 collection status

Collection session: 2026-10-03T15:26:50Z to 2026-10-03T15:46:44Z.

GPT-6 Luna (`gpt-6-luna`) was called in fresh Codex CLI processes at xhigh reasoning effort, with a
read-only sandbox. The frozen manifest in `manifest.jsonl` contains 1,664 cells. The confirmatory
sample is the 312 matched judge-case pairs in steps 0, 1, 2, 5, 6, 7, 8, 10, 11, 12, 13 and 15 for
`peeraccess_ng` and `toolaccess_ng`, fixed before outcomes were inspected; each selected cell was
attempted once, with no replacement draws. All 624 responses in those pairs parsed successfully, and
there were no tool calls. Raw replies, prompt hashes and parse outcomes are in `decisions.jsonl`.

`decisions.jsonl` holds those 624 responses, which are the responses the analysis uses.
`experiment/AMENDMENT-R7-primary-sample.md` is the registration amendment that fixed the sample;
it is reproduced unchanged and describes the wider collection the sample was drawn from.
