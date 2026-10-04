# GPT-6-sol replication

Collect the same balanced three-arm design as the GPT-6 Luna run: 26 judge labels
(`P1`–`P6`, `S1`–`S2`, `H1`–`H2`, `G01`–`G16`), 16 fixed cases, and
`peerbare_ng`, `toolbare_ng`, and `peermatch_ng` (1,248 cells total). Use the
same harness-generated prompt, case text, numbers, displacement assignment, and
one fresh model context per cell. The fixed prompt manifest records a hash for
each cell. Request order is shuffled with seed `20261004`; run at most five
calls concurrently.

Use `gpt-6-sol` at high reasoning effort in a read-only sandbox. Use the Codex
CLI defaults for all other settings. Pass the harness prompt verbatim, with no
extra task wording. Attempt every cell once. Retry only a call that returns no
model output, at most once; retain all attempts and all format failures. Add no
cells after inspecting responses. Store this as run `R8`, separate from and
without replacing the GPT-6 Luna records.

The primary contrast is `peermatch_ng` versus `toolbare_ng`; the secondary is
`peerbare_ng` versus `toolbare_ng`. Apply the existing case-clustered estimator
and 9,999 within-judge–case label swaps. Report both GPT-6 runs side by side.
The requested high reasoning effort differs from Luna's recorded `xhigh`
setting and will be reported as such.
