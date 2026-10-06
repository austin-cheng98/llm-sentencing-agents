# Wording Rivals Peers in LLM Judicial Decision-Making

Code, data, and paper materials for a study of how language-model decisions respond to numbers attributed to peers or forecasts. The repository also includes a civil-damages extension. Prompts, registrations, model outputs, and analysis scripts are included.

## Reproduce

Install the Python dependencies and rerun the analyses and figures:

```sh
python -m pip install -r requirements.txt
python analysis/run_all.py
python scripts/reproduce_damages.py
python figures/make_all.py
```

These commands use the released records and do not call a model API. See `experiment/` and `damages/` for protocols, registrations, and freeze records.

To rebuild the paper PDF, install [Tectonic](https://tectonic-typesetting.github.io/) and run:

```sh
cd paper
tectonic -C -k main.tex
```

## Repository contents

- `data/`, `runs/`: released decision records and run manifests
- `experiment/`, `damages/`: study protocols, registrations, and freeze records
- `analysis/`, `figures/`: analysis and figure-generation code
- `cases/`, `scripts/`: case-generation and civil-damages code
- `paper/`: LaTeX source, bibliography, and PDF

## License

MIT. See [LICENSE](LICENSE).
