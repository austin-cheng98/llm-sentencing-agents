# GPT-6 Luna source-access follow-up

This fixed-sample follow-up tests whether a neutral statement that both sources saw the case file preserves number use better than the earlier sentence saying they had no other information. It is a new GPT-6 Luna experiment; it does not alter the earlier registered result or test Claude.

## Design

Use 26 fresh GPT-6 Luna contexts, 16 cases, and four arms (1,664 decisions; 416 per arm). Each judge-case cell receives all four prompts in separate ephemeral contexts, with the same displayed numbers across arms. The source label (peer judges or statistical forecast) is crossed with the source-access sentence:

| Arms | Shared sentence |
| --- | --- |
| `peeraccess_ng`, `toolaccess_ng` | “Both sources are described as having reviewed the case file shown here.” |
| `peereqv_ng`, `tooleqv_ng` | “These figures were produced from the same case file you have been given, and from no other information about this defendant or this offense.” |

The peer and forecast blocks keep the same headers, descriptive sentence, and three rows in every arm. Only attribution and the shared sentence vary. All prompts omit the advisory range. Each cell is attempted once. Format failures and infrastructure failures remain in the record; no cell is retried or added after collection begins.

The contexts are P1–P6, S1–S2, H1–H2, and G01–G16, using the existing displacement allocation. The call order is shuffled with seed 20261003. Run at most five calls concurrently. Each call receives only its rendered decision prompt in a fresh `gpt-6-luna` Codex process, at `xhigh` reasoning effort, with a read-only sandbox.

## Analysis

The primary estimand is the peer premium under the neutral shared-file sentence: the peer-minus-forecast difference in the slope of sentence deviation from the case midpoint on displayed-number displacement, controlling for the four case factors. Use the case-clustered standard error and 9,999 label swaps within judge-case pairs (seed 17) for a two-sided randomization p-value. Report a 95% interval using a t critical value with 15 degrees of freedom and an 80%-power MDE of `(t[.975,15] + z[.80]) × SE`. Compare the MDE with the previously reported +0.206 structure-matched estimate. An MDE above +0.206 is inconclusive; estimates and intervals are reported regardless.

Secondary, descriptive results are the same premium under the explicit no-other-information sentence, the two source-specific number-use slopes under each sentence, exact matches to displayed numbers, and sentences outside the displayed range. No secondary result changes the primary conclusion.

The target of 26 contexts follows the prior GPT-6 Luna sample: for the same 16 cases and matched source contrast, its case-clustered SE was 0.0487 (t-corrected 80%-power MDE 0.145). This is a variance calibration from a different prompt condition, not a guarantee of the new condition's precision. Under that calibration, the design has approximately 80% power for effects of 0.145; the +0.206 benchmark is larger.
