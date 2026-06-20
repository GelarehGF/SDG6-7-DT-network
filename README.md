# Digital Transformation and SDG 6/7: Attribute-Augmented Network Analysis

Reproducibility package for the paper **"Digital Transformation and Sustainable
Development Goals 6 and 7: An Attribute-Augmented Network Analysis of Knowledge
Structure, Cross-Domain Coupling, and Counterfactual Decomposition."**

This repository contains the pipeline, theory/SDG anchors, derived label data,
and figure-generation code needed to reproduce the analysis. The source corpus
(peer-reviewed PDFs) is **not** distributed, as those articles are copyrighted;
the pipeline regenerates all derived data from a local corpus you provide.

---

## What this analysis does

It treats the DT-SDG 6/7 literature as a **paper-level semantic similarity
network** and asks how that network is structurally organised. Each paper is
embedded with `all-MiniLM-L6-v2`; papers above a cosine-similarity threshold are
linked; nodes are annotated with descriptive attributes (dominant theory, SDG
domain, outcome, technology). The pipeline then measures centrality asymmetry
between the two SDG domains, identifies cross-domain structural bridges, and runs
a **counterfactual decomposition** that separates content-driven from
topology-driven structural effects.

Headline findings (reproduced in `data/outputs/`):

- The network is fragmented and asymmetric: SDG 7 (energy) forms a dense central
  core while SDG 6 (water) is dispersed toward the periphery.
- SDG 7 papers have significantly higher centrality (Mann-Whitney p &approx; 5e-8;
  KS p &approx; 6e-9), and this survives balanced subsampling, so it is not a
  corpus-size artefact.
- Cross-domain integration is carried by a small set of structurally peripheral,
  theoretically diverse bridge papers; the dominant TOE framework does **not**
  appear among full-network bridges.
- Counterfactual Test A shows all four content attributes predict centrality
  beyond a label-permutation null, with SDG domain strongest.

---

## Repository layout

```
sdg6-7-dt-network/
|-- src/                     Pipeline (modular, importable)
|   |-- config.py            Thresholds, paths, anchor location, constants
|   |-- extract_corpus.py    Step 1: PDF -> section text (V7 regex)
|   |-- embed_classify.py    Step 2: embeddings + theory/SDG similarity + master
|   |-- network_analysis.py  Step 3: network, centrality, bridges, coupling
|   |-- counterfactual.py    Step 4: Test A (label perm) / Test B (rewiring)
|   |-- run_pipeline.py      Orchestrator
|-- data/
|   |-- anchors/anchors.json Theory + SDG anchor texts (the only "model inputs")
|   |-- outputs/             Derived, non-infringing results (shipped)
|   |   |-- df_master.csv               per-paper theory/SDG/outcome labels
|   |   |-- fig_F_test_results.csv      centrality KS / Mann-Whitney
|   |   |-- fig_J_counterfactual_results.csv
|   |   |-- fig_C_outcome_counts.csv
|   |   |-- fig_L_anchor_sensitivity.csv
|   |-- corpus/              <-- PUT YOUR PDFs HERE (gitignored, not shipped)
|-- figures/                 Generated figures
|-- notebooks/
|   |-- SDG6-7_REBUILD.ipynb  Original Colab pipeline (reference)
|-- requirements.txt
|-- LICENSE                  MIT
|-- CITATION.cff
```

---

## Reproducing the results

### Option A - from the shipped master table (no corpus needed)

The derived `df_master.csv` and figure CSVs are included, so you can regenerate
the network, bridge, and counterfactual results directly:

```bash
pip install -r requirements.txt
cd src
python run_pipeline.py --from-master
```

> Note: `--from-master` reuses `data/outputs/df_master.csv`. The network step
> also needs `doc_embeddings.npy`; if you only have the master labels, run the
> full pipeline (Option B) once to generate embeddings, or place a precomputed
> `doc_embeddings.npy` in `data/outputs/`.

### Option B - full pipeline from your own corpus

1. Place the source PDFs in `data/corpus/` (filenames like `SDG6-001.pdf`,
   `SDG7-001.pdf`).
2. Run:

```bash
pip install -r requirements.txt
cd src
python run_pipeline.py
```

This extracts sections, embeds, classifies, builds the network, and runs the
counterfactual tests, writing everything to `data/outputs/`.

---

## Configuration

All knobs live in `src/config.py`:

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `SIMILARITY_THRESHOLD` | 0.65 | edge cutoff for the paper network |
| `BRIDGE_TOP_PCT` | 0.10 | top-betweenness fraction defining a structural bridge |
| `PERMUTATION_ITERS` | 500 | Test A null iterations |
| `REWIRE_ITERS` | 30 | Test B degree-preserving swap iterations |
| `MODEL_NAME` | all-MiniLM-L6-v2 | embedding model |

Robustness across thresholds 0.55-0.75 is reported in the paper; change
`SIMILARITY_THRESHOLD` to reproduce the sensitivity sweep.

---

## Data and copyright

The `data/corpus/` directory is intentionally empty and gitignored. The articles
analysed are copyrighted and cannot be redistributed here. What **is** shipped is
fully derived, non-reproducible-to-source data: similarity scores, dominant-label
assignments, and aggregate counts. These do not contain article text.

---

## Citing

If you use this code or data, please cite the paper (see `CITATION.cff`):

> Farhadian, G., Saeedi M. & Ha J. (2026). Digital Transformation and Sustainable
> Development Goals 6 and 7: An Attribute-Augmented Network Analysis of Knowledge
> Structure, Cross-Domain Coupling, and Counterfactual Decomposition.

## License

Code is released under the MIT License (see `LICENSE`).
