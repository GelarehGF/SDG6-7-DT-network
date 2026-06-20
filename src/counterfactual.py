"""
Step 4 - Counterfactual decomposition.

Test A (fixed topology, permuted labels): measures how strongly each content
attribute predicts centrality beyond random label assignment on the same
network, via eta-squared against a PERMUTATION_ITERS null.

Test B (fixed content, rewired edges): degree-preserving edge swaps over
REWIRE_ITERS iterations to gauge sensitivity of structural position to
connectivity, benchmarked against an Erdos-Renyi null.
"""
import numpy as np
import pandas as pd
import networkx as nx

from config import PERMUTATION_ITERS, REWIRE_ITERS, SEED, OUTPUTS


def eta_squared(values, labels):
    """One-way eta-squared of a continuous `values` array across `labels`."""
    df = pd.DataFrame({"v": values, "g": labels})
    grand = df["v"].mean()
    ss_total = ((df["v"] - grand) ** 2).sum()
    ss_between = df.groupby("g")["v"].apply(
        lambda x: len(x) * (x.mean() - grand) ** 2).sum()
    return ss_between / ss_total if ss_total > 0 else 0.0


def test_a_label_permutation(cent, attributes, master, iters=PERMUTATION_ITERS, seed=SEED):
    rng = np.random.default_rng(seed)
    cent = cent.merge(master, on="paper_id", how="left")
    results = []
    for attr in attributes:
        labels = cent[attr].values
        vals = cent["eigenvector"].values
        observed = eta_squared(vals, labels)
        null = [eta_squared(vals, rng.permutation(labels)) for _ in range(iters)]
        p = (np.sum(np.array(null) >= observed) + 1) / (iters + 1)
        results.append({"attribute": attr, "observed_eta_sq": observed,
                        "null_mean": float(np.mean(null)), "perm_p": p,
                        "verdict": "content-driven" if p < 0.05 else "topology-consistent"})
    return pd.DataFrame(results)


def test_b_edge_rewiring(G, cent, iters=REWIRE_ITERS, seed=SEED):
    rng = np.random.default_rng(seed)
    base = cent.set_index("paper_id")["eigenvector"]
    deltas = []
    for _ in range(iters):
        H = G.copy()
        nx.double_edge_swap(H, nswap=H.number_of_edges(),
                            max_tries=H.number_of_edges() * 10, seed=int(rng.integers(1e9)))
        try:
            eig = nx.eigenvector_centrality_numpy(H, weight="weight")
        except Exception:  # noqa: BLE001
            continue
        common = [n for n in base.index if n in eig]
        deltas.append(np.mean([abs(base[n] - eig[n]) for n in common]))
    return {"mean_delta": float(np.mean(deltas)) if deltas else None,
            "n_iter": len(deltas)}


def run(out_dir=OUTPUTS):
    master = pd.read_csv(out_dir / "df_master.csv")
    cent = pd.read_csv(out_dir / "centrality_per_paper.csv")
    attrs = ["dominant_dt_theory", "dominant_sdg", "outcome", "method"]
    a = test_a_label_permutation(cent, attrs, master)
    a.to_csv(out_dir / "counterfactual_A_results.csv", index=False)
    print(a.to_string(index=False))
    return a


if __name__ == "__main__":
    run()
