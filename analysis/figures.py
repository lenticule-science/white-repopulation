"""Draw the paper's figures from the same records `reproduce.py` checks.

Each figure is a single series on one axis, drawn as a byte-reproducible SVG
(fixed hash salt, no creation date) so a rebuild produces identical files.
The data behind every mark is also printed as a table in the manuscript and
written to `data/derived/`, so no reading depends on the figure alone.

Run `python -m analysis.figures` from the repository root.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("svg")
import matplotlib.pyplot as plt  # noqa: E402

from analysis.reproduce import (  # noqa: E402
    BIRTH_SERIES,
    DECADES,
    MIGRATION_SERIES,
    SENSITIVITY_RATES,
    BirthReconstruction,
    load,
    percent,
)

FIGURES = Path(__file__).resolve().parent.parent / "figures"

SERIES = "#2a78d6"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"

plt.rcParams.update(
    {
        "svg.hashsalt": "white-repopulation",
        "svg.fonttype": "none",
        "font.family": "sans-serif",
        "font.size": 9,
        "axes.edgecolor": BASELINE,
        "axes.labelcolor": INK_SECONDARY,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
    }
)


def _axes(title: str, ylabel: str):
    figure, axes = plt.subplots(figsize=(6.0, 3.2), dpi=100)
    axes.set_title(title, loc="left", color=INK, fontsize=10, fontweight="bold")
    axes.set_ylabel(ylabel)
    axes.yaxis.grid(True, color=GRID, linewidth=0.6)
    axes.set_axisbelow(True)
    axes.tick_params(axis="both", length=0)
    return figure, axes


def _save(figure, name: str) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / name
    figure.tight_layout()
    figure.savefig(path, format="svg", metadata={"Date": None, "Creator": "white-repopulation analysis.figures"})
    plt.close(figure)
    return path


def captive_birth_share() -> Path:
    births = BirthReconstruction.from_record(load(BIRTH_SERIES))
    labels = [f"{start}s" for start, _ in DECADES]
    shares = [float(percent(c, t, 4)) for c, t in zip(births.captive_by_decade, births.all_by_decade)]

    # The 1790s denominator is assumed; show the share across the 45-65 per-thousand range.
    low_high = [
        float(percent(births.captive_by_decade[0], BirthReconstruction.assumed_1790s_births(births.mean_population_1790s, rate), 4))
        for rate in (max(SENSITIVITY_RATES), min(SENSITIVITY_RATES))
    ]

    figure, axes = _axes("Births into slavery as a share of U.S. births", "Percent of estimated births")
    bars = axes.bar(labels, shares, width=0.62, color=SERIES, edgecolor="white", linewidth=2)
    bars[0].set_hatch("////")
    bars[0].set_facecolor("white")
    bars[0].set_edgecolor(SERIES)
    axes.vlines(0, low_high[0], low_high[1], color=INK_SECONDARY, linewidth=1.2)
    axes.annotate(
        "1790s denominator assumed\n(crude birth rate 45–65 per 1,000)",
        xy=(0, low_high[1]), xytext=(0.55, 21.2), color=INK_SECONDARY, fontsize=8,
        arrowprops={"arrowstyle": "-", "color": MUTED, "linewidth": 0.6},
    )
    for index in (1, len(shares) - 1):
        axes.text(index, shares[index] + 0.35, f"{shares[index]:.1f}%", ha="center", color=INK, fontsize=8)
    axes.set_ylim(0, 24)
    return _save(figure, "captive-birth-share-by-decade.svg")


def migration_share() -> Path:
    record = load(MIGRATION_SERIES)
    labels = [f"{row['start_year']}–{str(row['end_year'])[2:]}" for row in record["intervals"]]
    shares = [row["net_migration_share_total_growth_pct"] for row in record["intervals"]]

    figure, axes = _axes("Net migration as a share of U.S. population growth", "Percent of growth")
    axes.bar(labels, shares, width=0.62, color=SERIES, edgecolor="white", linewidth=2)
    for index in (0, len(shares) - 1):
        axes.text(index, shares[index] + 0.8, f"{shares[index]:.1f}%", ha="center", color=INK, fontsize=8)
    axes.axhline(50, color=MUTED, linewidth=0.8, linestyle=(0, (3, 3)))
    axes.text(len(shares) - 0.6, 51, "half of growth", ha="right", color=INK_SECONDARY, fontsize=8)
    axes.set_ylim(0, 60)
    return _save(figure, "net-migration-share-of-growth.svg")


def main() -> None:
    for path in (captive_birth_share(), migration_share()):
        print(path.relative_to(FIGURES.parent))


if __name__ == "__main__":
    main()
