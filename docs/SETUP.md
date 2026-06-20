# Setting up the GitHub repository

This repo is ready to publish. Because creating the GitHub repo and pushing
require your authenticated GitHub account, do the following yourself.

## 1. Create the repository on GitHub

- Go to https://github.com/new
- Name: `sdg6-7-dt-network` (or your choice)
- Visibility: **Public**
- Do **not** initialize with a README/license/.gitignore (this folder already
  has them).

## 2. Initialize and push from this folder

From inside `sdg6-7-dt-network/`:

```bash
git init
git add .
git commit -m "Initial commit: SDG6-7 DT network reproducibility package"
git branch -M main
git remote add origin https://github.com/USERNAME/sdg6-7-dt-network.git
git push -u origin main
```

Replace `USERNAME` with your GitHub username.

## 3. Verify what was (and was not) committed

The `.gitignore` keeps the copyrighted corpus and large binaries out. Confirm
before pushing:

```bash
git status --short          # what will be committed
git check-ignore data/corpus/anything.pdf   # should print the path (= ignored)
```

You should see committed: `src/`, `data/anchors/`, `data/outputs/*.csv`,
`figures/*.png`, `notebooks/`, `README.md`, `LICENSE`, `CITATION.cff`,
`requirements.txt`.

You should **not** see: any `.pdf`, `data/corpus/`, `doc_embeddings.npy`,
`df_documents_full.csv`.

## 4. Optional polish after first push

- Update the `repository-code` URL in `CITATION.cff` and the citation badge.
- Add a release tag (`git tag v1.0 && git push --tags`) and, if you want a DOI,
  connect the repo to Zenodo so each release is archived and citable.
- Add the DOI badge to the top of `README.md`.

## Note on the notebook

`notebooks/SDG6-7_REBUILD.ipynb` is ~2.8 MB (it carries cell outputs). That is
fine for GitHub. If you prefer a lighter repo, clear outputs first:

```bash
jupyter nbconvert --clear-output --inplace notebooks/SDG6-7_REBUILD.ipynb
```
