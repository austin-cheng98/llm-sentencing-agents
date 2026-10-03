# R5 collection notes — excluded pilot

- UTC date: 2026-10-03.
- Model: `gpt-6-luna` selected explicitly in `collaboration.spawn_agent`; records carry the `gpt6` tag.
- Delegation: one fresh child context per decision, `fork_turns: none`, with the harness prompt as the complete message. The collaboration interface did not expose controls to disable child tools or set decoding/reasoning parameters; no such parameters were overridden.
- Collected: 5 `peermatch_ng` decisions for P1, steps 0–4; all 5 parsed successfully. Raw replies are in `decisions.peermatch_ng_P1.jsonl`.
- Deviation: the preregistration planned 480 R5 decisions. The study plan changed during collection to a separate larger R6 run. Two cells had already been dispatched when the stop request arrived, so R5 ended at 5 rather than 3 cells. R5 is an incomplete pilot and is excluded from all reported pooled estimates.
