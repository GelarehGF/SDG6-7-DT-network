"""
Step 2 - Embeddings, theory/SDG similarity, and master table.

Encodes corpus text with all-MiniLM-L6-v2, computes cosine similarity against
the theory and SDG anchors (data/anchors/anchors.json), detects method/outcome
keywords, and writes df_master.csv + doc_embeddings.npy.
"""
import json
import os

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import (ANCHORS_FILE, MODEL_NAME, OUTPUTS, METHOD_KEYWORDS,
                    OUTCOME_KEYWORDS)


def detect_keyword(text, keywords):
    t = (text or "").lower()
    return next((k for k in keywords if k in t), "unknown")


def detect_all_keywords(text, keywords):
    t = (text or "").lower()
    return [k for k in keywords if k in t]


def build_master(documents_csv=None, out_dir=OUTPUTS):
    documents_csv = documents_csv or (out_dir / "df_documents_full.csv")
    df = pd.read_csv(documents_csv)

    anchors = json.load(open(ANCHORS_FILE, encoding="utf-8"))
    theory_texts = anchors["dt_theory_anchors"]
    sdg_texts = anchors["sdg_anchors"]

    model = SentenceTransformer(MODEL_NAME)
    doc_emb = model.encode(df["text"].tolist(), normalize_embeddings=True)
    theory_emb = model.encode(list(theory_texts.values()), normalize_embeddings=True)
    sdg_emb = model.encode(list(sdg_texts.values()), normalize_embeddings=True)

    # Theory similarity
    t_labels = list(theory_texts.keys())
    df_theory = pd.DataFrame(cosine_similarity(doc_emb, theory_emb), columns=t_labels)
    df_theory.insert(0, "paper_id", df["paper_id"].values)
    df_theory["dominant_dt_theory"] = df_theory[t_labels].idxmax(axis=1)

    # SDG similarity
    s_labels = list(sdg_texts.keys())
    df_sdg = pd.DataFrame(cosine_similarity(doc_emb, sdg_emb), columns=s_labels)
    df_sdg.insert(0, "paper_id", df["paper_id"].values)
    df_sdg["dominant_sdg"] = df_sdg[s_labels].idxmax(axis=1)
    df_sdg["sdg_margin"] = df_sdg["SDG6_Water"] - df_sdg["SDG7_Energy"]

    # Master table
    master = df_theory.merge(df_sdg, on="paper_id")
    master["method"] = df["methodology"].apply(lambda x: detect_keyword(x, METHOD_KEYWORDS))
    master["outcome"] = df["text"].apply(lambda x: detect_keyword(x, OUTCOME_KEYWORDS))
    master["outcomes_all"] = df["text"].apply(
        lambda x: "|".join(detect_all_keywords(x, OUTCOME_KEYWORDS)))

    os.makedirs(out_dir, exist_ok=True)
    df_theory.to_csv(out_dir / "df_theory_similarity.csv", index=False)
    df_sdg.to_csv(out_dir / "df_sdg_similarity.csv", index=False)
    master.to_csv(out_dir / "df_master.csv", index=False)
    np.save(out_dir / "doc_embeddings.npy", doc_emb)
    print(f"Wrote df_master.csv {master.shape} and doc_embeddings.npy {doc_emb.shape}")
    return master, doc_emb


if __name__ == "__main__":
    build_master()
