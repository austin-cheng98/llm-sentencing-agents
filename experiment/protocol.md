# Coordinator protocol

You collect data for a controlled experiment. Execute MECHANICALLY and EXACTLY.
Never modify, summarize, shorten, paraphrase, or add to any prompt text. You are
plumbing, not a participant. Do not reason about the experiment's content.

You are given a SLICE LIST: a set of (ARM, JUDGE) pairs. Work through them in order.

For each (ARM, JUDGE), first find the steps still needed:
   python3 experiment/status.py todo ARM JUDGE
It prints the missing step numbers. Collect ONLY those. If it prints nothing, that
pair is already complete: move to the next one.

For each step K:

1. Fetch the exact prompt:
   python3 experiment/harness.py prompt --run R1 --arm ARM --judge JUDGE --step K

2. Spawn a subagent (Agent tool), model "opus", subagent_type "general-purpose",
   prompt EXACTLY the text from (1): verbatim, character for character, nothing added
   before or after. No framing, no mention of this experiment, no tools.

3. Write the reply VERBATIM to /tmp/r_ARM_JUDGE_K.txt with the Write tool, then:
   python3 experiment/harness.py record --run R1 --arm ARM --judge JUDGE --step K --model opus5 --shard ARM_JUDGE < /tmp/r_ARM_JUDGE_K.txt
   It prints JSON containing "ok": true/false.

## Concurrency — hard rules

Spawn AT MOST 5 subagents at a time. Fetch 5 prompts, spawn exactly 5 Agent calls in
one message, record those 5, then the next batch. NEVER spawn 6 or more at once.

If a spawn fails with a concurrency or rate limit: do NOT stop, do NOT schedule a
background wait, and do NOT end your turn. Immediately retry the SAME step with a
batch of 1. Single spawns almost always succeed because the shared pool drains
continuously. Keep issuing single spawns until capacity returns, then resume batches
of 5. Never use sleep or background timers to pace yourself; just retry.

Do not end your turn until every step in every assigned slice is recorded, or you
have retried a step at batch size 1 at least eight separate times.

If a subagent refuses or returns prose instead of the 5-line format, retry that step
ONCE. If it fails again, record the raw text anyway and note the step.

FINAL MESSAGE (under 12 lines): per (ARM, JUDGE), how many steps recorded ok, plus any
steps that refused or could not be collected. Never paste full prompts or replies.
