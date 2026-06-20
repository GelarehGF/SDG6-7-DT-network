"""
Step 3 - Network construction, centrality, bridges, and coupling metrics.

Builds the paper-similarity network from doc_embeddings.npy, restricts to the
largest connected component, and computes:
  - eigenvector / betweenness centrality (and the SDG6 vs SDG7 comparison)
  - cross-domain contacts and structural bridges
  - structural coupling components (density, dependency, centrality overlap)
"""
import numpy as np
import pandas as pd
import networkx as nx
from scipy.stats import ks_2samp, mannwhitneyu
from sklearn.metrics.pairwise import cosine_similarity

from config import SIMILARITY_THRESHOLD, BRIDGE_TOP_PCT, OUTPUTS


def build_network(embeddings, paper_ids, threshold=SIMILARITY_THRESHOLD):
    sim = cosine_similarity(embeddings)
    G = nx.Graph()
    G.add_nodes_from(paper_ids)
    n = len(paper_ids)
    for i in range(n):
        for j in range(i + 1, n):
            if sim[i, j] >= threshold:
                G.add_edge(paper_ids[i], paper_ids[j], weight=float(sim[i, j]))
    return G


def largest_component(G):
    if G.number_of_edges() == 0:
        return G.copy()
    nodes = max(nx.connected_components(G), key=len)
    return G.subgraph(nodes).copy()


def centrality_table(G, master):
    eig = nx.eigenvector_centrality_numpy(G, weight="weight")
    bet = nx.betweenness_centrality(G, weight="weight")
    dom = master.set_index("paper_id")["dominant_sdg"].to_dict()
    rows = [{"paper_id": n, "eigenvector": eig[n], "betweenness": bet[n],
             "dominant_sdg": dom.get(n)} for n in G.nodes()]
    return pd.DataFrame(rows)


def centrality_asymmetry(cent):
    a = cent[cent["dominant_sdg"] == "SDG6_Water"]["eigenvector"]
    b = cent[cent["dominant_sdg"] == "SDG7_Energy"]["eigenvector"]
    ks = ks_2samp(a, b)
    mw = mannwhitneyu(a, b, alternative="two-sided")
    return {"ks_stat": ks.statistic, "ks_p": ks.pvalue,
            "mw_u": mw.statistic, "mw_p": mw.pvalue,
            "n_sdg6": len(a), "n_sdg7": len(b),
            "mean_sdg6": a.mean(), "mean_sdg7": b.mean()}


def identify_bridges(G, cent, top_pct=BRIDGE_TOP_PCT):
    dom = cent.set_index("paper_id")["dominant_sdg"].to_dict()
    cross = [n for n in G.nodes()
             if any(dom.get(nb) != dom.get(n) for nb in G.neighbors(n))]
    bet = cent.set_index("paper_id")["betweenness"]
    if not cross:
        return [], cross
    cutoff = bet.loc[cross].quantile(1 - top_pct)
    bridges = [n for n in cross if bet[n] >= cutoff]
    return bridges, cross


def coupling_components(G, cent):
    dom = cent.set_index("paper_id")["dominant_sdg"].to_dict()
    density = nx.density(G)
    cross_w = sum(d["weight"] for u, v, d in G.edges(data=True) if dom.get(u) != dom.get(v))
    within_w = sum(d["weight"] for u, v, d in G.edges(data=True) if dom.get(u) == dom.get(v))
    n_cross = sum(1 for u, v in G.edges() if dom.get(u) != dom.get(v))
    n_within = sum(1 for u, v in G.edges() if dom.get(u) == dom.get(v))
    cross_mean = (cross_w / n_cross) if n_cross else 0.0
    within_mean = (within_w / n_within) if n_within else 1e-9
    dependency = cross_mean / within_mean
    # centrality overlap: rank correlation of the two domains' centrality profiles
    overlap = cent.groupby("dominant_sdg")["eigenvector"].mean().min() / \
        max(cent.groupby("dominant_sdg")["eigenvector"].mean().max(), 1e-9)
    return {"edge_density": density, "dependency": dependency,
            "centrality_overlap": overlap}


def run(out_dir=OUTPUTS):
    master = pd.read_csv(out_dir / "df_master.csv")
    emb = np.load(out_dir / "doc_embeddings.npy")
    pids = master["paper_id"].tolist()

    G = largest_component(build_network(emb, pids))
    cent = centrality_table(G, master)
    cent.to_csv(out_dir / "centrality_per_paper.csv", index=False)

    asym = centrality_asymmetry(cent)
    pd.DataFrame([asym]).to_csv(out_dir / "centrality_test_results.csv", index=False)

    bridges, cross = identify_bridges(G, cent)
    coup = coupling_components(G, cent)
    print(f"LCC: {G.number_of_nodes()} nodes / {G.number_of_edges()} edges")
    print(f"Cross-domain contacts: {len(cross)} | Structural bridges: {len(bridges)}")
    print(f"Coupling: {coup}")
    print(f"Centrality asymmetry: {asym}")
    return G, cent, bridges, coup


if __name__ == "__main__":
    run()
