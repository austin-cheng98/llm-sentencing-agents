# Wording Rivals Peers in LLM Judicial Decision-Making

This repository contains the released data and code used to regenerate the study's figures. The study examines whether language-model decisions move toward displayed numbers because of numerical anchoring or because those numbers are attributed to peers. The sentencing experiments hold the displayed values constant while varying their attribution and wording. A civil-damages extension compares peer-attributed awards with forecast-attributed awards.

## Reproduce the figures

Use Python with the packages listed in `requirements.txt`. From the repository root, install dependencies and run the analyses before generating the figures:

```sh
python -m pip install -r requirements.txt
python analysis/run_all.py
python scripts/reproduce_damages.py
python figures/make_all.py
```

The first command installs NumPy and Matplotlib. `analysis/run_all.py` recomputes the sentencing-study estimates from the released decisions. `scripts/reproduce_damages.py` recomputes the registered D1 and D2 civil-damages analyses. `figures/make_all.py` then builds all nine figures from the generated analysis files. The scripts stop if a required analysis or figure fails.

The figure scripts write PDF files to `figures/`; selected figures also have PNG versions. The outputs are generated from the released records rather than downloaded. These commands do not call a language-model API, so they do not require model credentials or incur inference costs. Bootstrap and permutation routines use fixed seeds where specified in the analysis code.

Run the commands from the repository root and in the order shown. The analysis scripts read the included records and write their outputs in the repository. Running them again replaces those generated outputs. If a command stops, check that dependencies installed and that the earlier analysis steps completed before rerunning the figure command.

## Figure set

`figures/make_all.py` runs these scripts:

- `fig_forest.py`: peer-premium estimates across model and prompt conditions.
- `fig_sentences.py`: changes associated with the prompt's closing sentences.
- `fig_models.py`: model-level number pull with and without sentencing guidelines.
- `fig_main.py`: decision outcomes across displacements and source attributions.
- `fig_cascade.py`: agreement and copying when agents observe earlier decisions.
- `fig_design.py`: how the displayed numbers are displaced and attributed.
- `fig_confidence.py`: reported confidence and exact adoption of displayed numbers.
- `fig_factors.py`: case factors under guideline and no-guideline conditions.
- `damages_civil.py`: peer-versus-forecast results in the civil-damages extension.

## Data and code

- `data/` contains the main sentencing decisions, repeated draws, cases, and number assignments.
- `runs/R7/` and `runs/R8/` contain the neutral shared-file follow-up and GPT-6 Sol replication records and manifests.
- `runs/D1/` and `runs/D2/` contain civil-damages decisions, manifests, raw replies, and collection logs.
- `cases/claims.json` contains the fictional civil-damages claims used in the extension.
- `experiment/` and `damages/` contain protocols, registrations, amendments, and freeze records that specify the designs and analysis plans.
- `analysis/` contains scripts and generated estimates consumed by the figures.
- `figures/` contains the plotting scripts and generated outputs. `figures/make_all.py` runs the complete figure set.
- `scripts/` contains the civil-damages reproduction and collection utilities.

The collection scripts are included for auditability, but reproducing the figures uses the saved model outputs. It does not repeat data collection. The released records preserve each response together with its run metadata; registrations and freeze files document the planned contrasts and code snapshots. For questions about a particular panel, begin with its script in `figures/`, then follow the input paths to the corresponding analysis output and records.

## License

MIT. See [LICENSE](LICENSE).
