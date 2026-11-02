#!/usr/bin/env python3
"""Publication figures for the memory-utilization-gap study.

Data below are the coded rates from coding.csv (all 1,339 outputs annotated;
see codebook.md). Rerun after any re-coding: python3 figures.py
Outputs to figures/.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)

SURFACE = "#fcfcfb"; INK = "#0b0b0b"; SEC = "#52514e"; MUT = "#898781"
GRID = "#e1e0d9"; BASE = "#c3c2b7"
BLUE = "#2a78d6"; ORANGE = "#eb6834"; GREEN = "#008300"; MAGENTA = "#e87ba4"; YELLOW = "#eda100"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans"],
    "text.color": INK, "axes.edgecolor": BASE, "axes.labelcolor": SEC,
    "xtick.color": MUT, "ytick.color": MUT, "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})

COND_LABELS = ["L0\nformal\nno info", "L0c\ncasual\nno info", "L1\nformal\nmemory",
               "L1c\ncasual\nmemory", "L2\nmemory +\npersonalize instr.", "L4\nexplicit\ndemand"]

# ---- Figure 1: canonical-trope survival across all six conditions ----------
# Each concept gets its own categorical slot; the two stratum-B controls
# (circuits, packets) are deliberately gray reference lines.
AQUA = "#1baf7a"; VIOLET = "#4a3aa7"; RED = "#e34948"
data = [
    ("gradient descent (foggy hiker)",   [100, 100, 100, 100, 100, 100], BLUE),
    ("path dependence (QWERTY)",         [100, 100, 100, 100, 100, 100], GREEN),
    ("circuits (water pipes) [control]", [100, 100, 100, 100, 100, 100], "#b5b4ad"),
    ("packets (postal mail) [control]",  [100, 100, 100, 80, 100, 100],  "#8f8e88"),
    ("regression to mean (sports slump)",[95, 100, 80, 90, 80, 5],       ORANGE),
    ("feedback loops (thermostat/AC)",   [10, 45, 10, 50, 0, 30],        VIOLET),
    ("p-values (courtroom)",             [5, 45, 5, 40, 20, 0],          AQUA),
    ("deadlock (four-way stop)",         [20, 10, 15, 35, 35, 35],       RED),
    ("MLE (hot-and-cold)",               [0, 5, 0, 10, 0, 0],            YELLOW),
    ("cond. probability (Monty Hall)",   [0, 5, 0, 0, 5, 0],             MAGENTA),
]
x = list(range(6))
fig, ax = plt.subplots(figsize=(12.0, 5.8), dpi=200)
dodge = {"path dependence (QWERTY)": 2.2, "circuits (water pipes) [control]": 1.1,
         "gradient descent (foggy hiker)": 0.0, "MLE (hot-and-cold)": 1.0,
         "cond. probability (Monty Hall)": -1.0}
label_y = {}
for name, ys, color in data:
    d = dodge.get(name, 0.0)
    yy = [v + d for v in ys]
    control = "[control]" in name
    ax.plot(x, yy, color=color, linewidth=1.5 if control else 2.0,
            zorder=2 if control else 3, marker="o", markersize=2.6 if control else 3.6,
            markerfacecolor=color, markeredgecolor=SURFACE, markeredgewidth=0.6,
            linestyle="--" if control else "-")
    label_y[name] = (yy[-1], color)

GAP = 5.8
order = sorted(label_y.items(), key=lambda kv: -kv[1][0])
slots = []
for i, (name, (y, c)) in enumerate(order):
    slots.append(y if i == 0 else min(y, slots[i - 1] - GAP))
if slots and slots[-1] < -4.0:
    slots[-1] = -4.0
    for i in range(len(slots) - 2, -1, -1):
        slots[i] = max(slots[i], slots[i + 1] + GAP)
for (name, (y, color)), yy in zip(order, slots):
    ax.plot([5.08, 5.22], [yy, yy], color=color, linewidth=2.6, clip_on=False,
            solid_capstyle="round")
    ax.annotate(name, xy=(5, y), xytext=(5.28, yy), fontsize=8.2, color=SEC,
                va="center", annotation_clip=False)

ax.set_xlim(-0.15, 6.9); ax.set_ylim(-6, 106)
ax.set_xticks(x); ax.set_xticklabels(COND_LABELS, fontsize=7.8)
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=8.2)
ax.grid(axis="y", color=GRID, linewidth=0.7)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color(BASE)
ax.set_title("Deeply conventionalized analogies survive every condition; weak ones drift",
             fontsize=12, fontweight="bold", color=INK, loc="left", pad=14)
ax.text(0, 1.015, "Share of generations where the canonical analogy carries the explanation · 20 runs/cell · 2 models pooled · all 1,339 outputs coded",
        transform=ax.transAxes, fontsize=7.8, color=MUT, va="bottom")
fig.subplots_adjust(right=0.72, left=0.05, top=0.85, bottom=0.15)
fig.savefig(OUT / "fig1_trope_survival.png")
plt.close(fig)

# ---- Figure 3: provenance composition across all six conditions ------------
PROV_COLORS = {"universal": BLUE, "regional": GREEN, "anglo-marked": YELLOW, "other-marked": MAGENTA}
mix = {
    "L0 · formal, no info":             {"universal": 64, "regional": 27, "anglo-marked": 8, "other-marked": 0},
    "L0c · casual, no info":            {"universal": 70, "regional": 23, "anglo-marked": 6, "other-marked": 0},
    "L1 · formal + memory":             {"universal": 66, "regional": 27, "anglo-marked": 5, "other-marked": 0},
    "L1c · casual + memory":            {"universal": 70, "regional": 22, "anglo-marked": 6, "other-marked": 1},
    "L2 · memory + personalize instr.": {"universal": 69, "regional": 23, "anglo-marked": 6, "other-marked": 1},
    "L4 · explicit demand":             {"universal": 22, "regional": 4, "anglo-marked": 0, "other-marked": 73},
}
fig, ax = plt.subplots(figsize=(9.4, 4.8), dpi=200)
ypos = [5, 4, 3, 2, 1, 0]
for y, (cond, m) in zip(ypos, mix.items()):
    left = 0
    for prov in ("universal", "regional", "anglo-marked", "other-marked"):
        v = m[prov]
        if v == 0:
            continue
        ax.barh(y, v, left=left, height=0.58, color=PROV_COLORS[prov],
                edgecolor=SURFACE, linewidth=2)
        if v >= 5:
            ax.text(left + v / 2, y, f"{v}%", ha="center", va="center", fontsize=8.4,
                    color="#ffffff" if prov in ("universal", "regional") else INK)
        left += v
ax.set_yticks(ypos); ax.set_yticklabels(list(mix.keys()), fontsize=8.8, color=SEC)
ax.set_xlim(0, 100); ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=8.2)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color(BASE)
handles = [plt.Rectangle((0, 0), 1, 1, color=PROV_COLORS[p]) for p in PROV_COLORS]
ax.legend(handles, ["universal", "regional/globalized", "Anglo-marked", "Chinese-specific"],
          loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=4, frameon=False, fontsize=8.4)
ax.set_title("No memory condition moves the analogy mix; explicit demand inverts it",
             fontsize=12, fontweight="bold", color=INK, loc="left", pad=13)
ax.text(0, 1.03, "Cultural provenance of the load-bearing analogy · 220 responses/condition, coded · Chinese-specific is 0-2/220 in every memory condition",
        transform=ax.transAxes, fontsize=7.6, color=MUT, va="bottom")
fig.subplots_adjust(left=0.245, right=0.98, top=0.82, bottom=0.18)
fig.savefig(OUT / "fig3_provenance_mix.png")
plt.close(fig)
print("wrote", ", ".join(sorted(p.name for p in OUT.glob("*.png"))))
