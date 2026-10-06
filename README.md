# Wording Rivals Peers in LLM Judicial Decision-Making
Austin L. Cheng

Accepted to SocialAgent: Second Workshop on Large Language Models for Social Reasoning and Simulation @ NeurIPS 2026.

This project studies why language-model agents move toward numbers shown in a prompt. When an agent sees another agent's decision, its response could reflect social influence, numerical anchoring, or both. The experiments separate these explanations by holding the displayed numbers constant while changing whether they are attributed to peers or to a statistical forecast.

## Study design

The main experiment uses procedurally generated fictional criminal-sentencing cases. For each case, three numbers are displaced by assigned amounts from the midpoint of its sentencing guideline. Paired prompt conditions show the same numbers but describe their source differently. Some conditions also vary surrounding language or omit the guideline.

For each condition, the analysis estimates a dose-response slope: how much the agent's sentence shifts as the displayed numbers move. This slope measures numerical pull. The difference between peer-attributed and forecast-attributed slopes is the peer premium. Because the numbers and their displacement are yoked across conditions, this contrast isolates the change associated with source attribution from the pull of the numbers themselves.

The study also examines sequential decisions, where agents can see predecessors' sentences, and a separate civil-damages task. The civil task uses fictional claims and compares peer-attributed awards with forecast-attributed valuations. Its outcome is the mean proportional distance of the award from the displayed center. These tasks measure responses to controlled prompts; they do not evaluate judicial accuracy or show that language models reproduce human judicial reasoning.

## Main findings

With the sentencing guideline omitted, Claude Opus 5 shows a peer premium of +0.32 under bare prompts and +0.21 under structure-matched prompts. GPT-6 Luna and GPT-6 Sol also show positive structure-matched premiums under identical prompts and case allocations. Removing the guideline increases numerical pull across the three Claude models. A routine instruction to decide independently reduces the premium for Opus 5, but not for the two smaller Claude models, showing that measured peer effects depend on prompt wording and model.

In the civil-damages extension, the peer-minus-forecast difference in proportional distance from the displayed center is +0.140 for Claude Opus 5 and +0.093 for GPT-6 Sol. The extension carries the source comparison into a separate legal domain while retaining fictional cases and controlled numerical inputs.

## Materials

The repository includes 4,086 core sentencing decision records, repeated draws, prompts, cases, and model outputs. Civil-damages decisions and their collection records are stored separately. Study protocols, pre-registrations, amendments, and freeze records document the planned conditions and analyses.

- `data/`: core decisions, repeated draws, and sentencing-case inputs
- `runs/`: model records, manifests, and collection logs for the follow-up and civil-damages tasks
- `experiment/`, `damages/`: protocols, pre-registrations, amendments, and freeze records
- `analysis/`: estimators and saved analysis outputs
- `figures/`: plotting code and generated figures
- `cases/`, `scripts/`: case-generation and civil-damages utilities

The source code and analysis outputs are provided so readers can inspect how the reported contrasts were constructed from the released responses. Reproducing the reported findings does not require collecting new model responses. The figures summarize the sentencing and civil-damages comparisons.

## License

MIT License — see [LICENSE](LICENSE) for details.
