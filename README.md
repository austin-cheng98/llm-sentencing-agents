# Wording Rivals Peers in LLM Judicial Decision-Making
Accepted to SocialAgent: Second Workshop on Large Language Models for Social Reasoning and Simulation

This project tests whether language-model agents follow peer decisions because of social attribution or because numbers in a prompt anchor their responses. It studies fictional criminal sentences and civil-damages awards. The repository contains the decision records, analysis code, collection materials, and figure scripts.

## Design

In the sentencing study, each agent sees three numbers displaced from the midpoint of a fictional case’s guideline range. The same values are attributed to peer sentences or a statistical forecast. Conditions vary the attribution, surrounding wording, and availability of the guideline while holding cases and numbers fixed. The slope relating sentence deviation to number displacement measures numerical pull. The difference between peer and forecast slopes is the peer premium.

The core sentencing file contains 4,214 records, of which 4,206 contain parseable decisions: 1,270 Claude Opus 5, 224 Claude Sonnet 5, 224 Claude Haiku 4.5, 1,248 GPT-6 Luna, and 1,248 GPT-6 Sol decisions. Luna and Sol use the same prompts and case allocations, with extra-high and high reasoning settings, respectively.

## Main findings

For Claude Opus 5, the peer premium is +0.323 under bare wording (p = 0.0002, n = 128) and +0.206 under structure-matched wording (p = 0.005, n = 192). Adding a closing sentence to the peer block lowers its pull by 0.279; the matched forecast hedge changes pull by +0.05 (p = 0.40).

Both GPT-6 runs produce positive premiums. Luna’s structure-matched and bare estimates are +0.220 and +0.256. Sol’s are +0.239 and +0.113. All four estimates have p < 0.001 and n = 832. Sol’s structure-matched interval includes the Opus benchmark; its bare interval falls below the benchmark. Because the two runs use different reasoning settings, their estimate differences do not isolate model identity.

A neutral shared-file follow-up retains the source comparison without telling agents the displayed figures add no information. Across 312 matched pairs, the peer premium is +0.250 (p < 0.001; 95% CI [+0.134, +0.365]).

In the civil-damages extension, peer awards have greater mean proportional distance from the displayed center than forecast awards in the registered Opus 5 confirmation (+0.140, 32 pairs) and GPT-6 Sol replication (+0.093, 159 pairs). The in-band contrast in the Sol run does not reproduce the Opus result.

## Data and reproduction

The sentencing records are in `data/decisions.jsonl`; the selected neutral-wording follow-up is in `runs/R7/`; the Sol sentencing replication is in `runs/R8/`. Civil-damages records and registrations are in `runs/D1/`, `runs/D2/`, and `damages/`. Collection manifests and freeze files record prompt assignments and input hashes.

Install the listed dependencies, then run the analyses and figures from the repository root:

```bash
python -m pip install -r requirements.txt
python analysis/run_all.py
python scripts/damages_analysis.py
python scripts/damages_analysis_ext.py
python scripts/damages_analysis_prox.py
python scripts/damages_analysis_d2.py
python figures/make_all.py
```

The analyses use the released records and make no language-model API calls. The figure scripts write the nine paper figures to `figures/`. The main folders are `analysis/` for estimates, `experiment/` for sentencing protocols and registrations, `damages/` for civil-study materials, and `runs/` for collected responses.

## Scope

The cases and claims are fictional. These experiments measure how model outputs respond to source labels, numerical anchors, wording, and institutional reference points. They do not establish that language models reproduce judicial reasoning or predict real case outcomes.
