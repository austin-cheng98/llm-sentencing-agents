# R7 protocol amendment: CLI launch failures

Issued 2026-10-03T14:50:55Z, before any R7 model response.

Initial attempts failed before model inference: 1,572 local-state starts and 17 transport starts returned empty output and made no tool calls. A separate smoke call also failed during setup. These were not model decisions and are not included in the released response data.

After the local setup and transport issues were resolved, each model-reaching call was attempted once; returned responses were retained, with no replacements. The original prompts and estimand were unchanged. Later outcome-blind sample amendments are recorded separately.
