"""
Run the full SDG6-7 DT-network pipeline end to end.

Usage:
    python src/run_pipeline.py            # full run (requires corpus in data/corpus/)
    python src/run_pipeline.py --from-master   # skip extraction+embedding,
                                               # reuse data/outputs/df_master.csv

Stages:
    1. extract_corpus   -> df_documents_full.csv   (needs PDFs; copyrighted, not shipped)
    2. embed_classify   -> df_master.csv, doc_embeddings.npy
    3. network_analysis -> centrality, bridges, coupling
    4. counterfactual   -> Test A / Test B
"""
import argparse

import extract_corpus
import embed_classify
import network_analysis
import counterfactual


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-master", action="store_true",
                    help="reuse existing df_master.csv + doc_embeddings.npy")
    args = ap.parse_args()

    if not args.from_master:
        extract_corpus.build_corpus()
        embed_classify.build_master()

    network_analysis.run()
    counterfactual.run()
    print("\nPipeline complete. See data/outputs/ for results.")


if __name__ == "__main__":
    main()
