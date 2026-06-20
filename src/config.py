"""Configuration and constants for the SDG6-7 DT network pipeline."""
from pathlib import Path

SEED = 42

# Embedding model (Sentence-Transformers)
MODEL_NAME = "all-MiniLM-L6-v2"

# Similarity threshold for the paper-similarity network.
# Robustness is evaluated across 0.55-0.75 (see src/robustness.py).
SIMILARITY_THRESHOLD = 0.65

# Bridge definition: a structural bridge is a cross-domain contact whose
# betweenness centrality falls in the top BRIDGE_TOP_PCT of the distribution.
BRIDGE_TOP_PCT = 0.10

# Counterfactual settings
PERMUTATION_ITERS = 500      # Test A: fixed-topology label permutation
REWIRE_ITERS = 30            # Test B: fixed-content degree-preserving rewiring

# Keyword vocabularies for method / outcome detection (computed from text)
METHOD_KEYWORDS = ["regression", "sem", "case study", "survey", "experiment",
                   "qualitative", "mixed method", "interview", "review", "simulation"]
OUTCOME_KEYWORDS = ["access", "efficiency", "governance", "sustainability",
                    "resilience", "productivity", "quality", "equity", "inequality"]

# Paths (relative to repo root)
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA = REPO_ROOT / "data"
ANCHORS_FILE = DATA / "anchors" / "anchors.json"
CORPUS_DIR = DATA / "corpus"          # local-only; gitignored (copyrighted PDFs)
OUTPUTS = DATA / "outputs"
FIGURES = REPO_ROOT / "figures"
