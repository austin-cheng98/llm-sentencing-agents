# Cascade collection protocol

Execute MECHANICALLY. Never modify prompt text.

This arm is SEQUENTIAL WITHIN A CASE. For each case (step), six agents decide in a fixed
speaking order, and each agent sees the sentences the earlier agents actually gave for that
same case. You must respect the order and record each decision before fetching the next.

For each STEP K in your assigned list:

1. Get the speaking order:
   python3 experiment/harness.py order --run R1 --step K --judges C1,C2,C3,C4,C5,C6

2. For each JUDGE in that order, one at a time, in order:
   a. python3 experiment/harness.py prompt --run R1 --arm cascade_ng --judge JUDGE --step K --judges C1,C2,C3,C4,C5,C6
   b. Spawn ONE subagent (Agent tool), model "opus", subagent_type "general-purpose",
      prompt EXACTLY the text from (a), verbatim, nothing added.
   c. Write the reply VERBATIM to /tmp/casc_K_JUDGE.txt with the Write tool, then:
      python3 experiment/harness.py record --run R1 --arm cascade_ng --judge JUDGE --step K --model opus5 --shard cascade_ng_JUDGE --judges C1,C2,C3,C4,C5,C6 < /tmp/casc_K_JUDGE.txt
   d. Only after (c) prints "ok": true may you fetch the prompt for the NEXT judge.

NEVER fetch a later judge's prompt before the earlier judge is recorded. Doing so would
show that agent an incomplete cascade and corrupt the arm.

Different STEPS are independent. You may not parallelise judges within a step.

On a concurrency error, retry the same single spawn. If a spawn fails with a session or
usage limit, stop and report progress.

FINAL MESSAGE (under 10 lines): steps completed, and the sentence values per step in
speaking order.
