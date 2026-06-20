"""
Regenerate the paper's figures from the shipped derived CSVs in data/outputs/.

These figures depend only on the non-infringing derived data, so they reproduce
without the corpus:
    fig_C  outcome counts by SDG
    fig_F  centrality comparison summary (text panel)
    fig_J  counterfactual centrality stability
    fig_L  theory-anchor sensitivity

Run:  python figures/make_figures.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "data", "outputs")
FIG = HERE


def fig_C():
    df = pd.read_csv(os.path.join(OUT, "fig_C_outcome_counts.csv"), index_col=0)
    ax = df.plot(kind="bar", figsize=(11, 6), color=["#1D8348", "#2874A6"],
                 edgecolor="black", width=0.75)
    ax.set_title("Outcome frequencies by dominant SDG")
    ax.set_xlabel("Outcome category"); ax.set_ylabel("Paper count")
    ax.legend(title="SDG"); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout(); plt.savefig(os.path.join(FIG, "fig_C_outcomes_by_sdg.png"), dpi=300)
    plt.close()


def fig_J():
    df = pd.read_csv(os.path.join(OUT, "fig_J_counterfactual_results.csv"))
    fig, ax = plt.subplots(figsize=(9, 5))
    y = range(len(df))
    ax.errorbar(df["mean"], y,
                xerr=[df["mean"] - df["ci_low"], df["ci_high"] - df["mean"]],
                fmt="o", capsize=4, color="#457B9D")
    ax.set_yticks(list(y)); ax.set_yticklabels(df["scenario"])
    ax.axvline(0.0285, ls="--", color="#E63946", label="Observed SDG6-7 gap")
    ax.set_xlabel("Mean |delta centrality| (95% CI)")
    ax.set_title("Counterfactual centrality stability")
    ax.legend(); plt.tight_layout()
    plt.savefig(os.path.join(FIG, "fig_J_counterfactual.png"), dpi=300); plt.close()


def fig_L():
    df = pd.read_csv(os.path.join(OUT, "fig_L_anchor_sensitivity.csv"))
    piv = df.pivot(index="theory", columns="variant", values="spearman_rho")
    fig, ax = plt.subplots(figsize=(7, 5))
    im = ax.imshow(piv.values, cmap="viridis", vmin=0.5, vmax=1.0, aspect="auto")
    ax.set_xticks(range(len(piv.columns))); ax.set_xticklabels(piv.columns)
    ax.set_yticks(range(len(piv.index))); ax.set_yticklabels(piv.index)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            ax.text(j, i, f"{piv.values[i, j]:.3f}", ha="center", va="center",
                    color="white", fontsize=9)
    fig.colorbar(im, label="Spearman rho vs standard anchor")
    ax.set_title("Theory anchor sensitivity")
    plt.tight_layout(); plt.savefig(os.path.join(FIG, "fig_L_anchor_sensitivity.png"), dpi=300)
    plt.close()


if __name__ == "__main__":
    fig_C(); fig_J(); fig_L()
    print("Figures written to figures/")
