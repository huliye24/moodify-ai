"""Generate diagram assets for DOC-MFY-003 project charter."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
plt.rcParams["font.family"] = "Microsoft YaHei"
plt.rcParams["font.size"] = 10

# ── Colour palette ──────────────────────────────────────────────
C = {
    "p0": "#DC3545", "p1": "#FD7E14", "p2": "#0D6EFD",
    "in": "#198754", "out": "#6C757D", "pool": "#6F42C1",
    "phase": ["#0D6EFD", "#198754", "#FD7E14", "#6F42C1", "#DC3545", "#20C997"],
    "bg": "#F8F9FA", "edge": "#DEE2E6", "text": "#212529",
    "white": "#FFFFFF",
}


def save(fig, name):
    path = OUT_DIR / name
    fig.savefig(str(path), dpi=150, bbox_inches="tight", facecolor=C["white"], edgecolor="none")
    plt.close(fig)
    print(f"  -> {path}")


# ═══════════════════════════════════════════════════════════════
# 1. scope_diagram.png — Range boundary (concentric rings)
# ═══════════════════════════════════════════════════════════════
def draw_scope():
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.set_aspect("equal")
    ax.axis("off")

    # ── Rings ──
    for r, color, label, alpha in [
        (5.0, C["in"], "In Scope (v0.4)", 0.18),
        (3.4, C["pool"], "Candidate Pool (v0.5+)", 0.12),
        (1.8, C["p0"], "P0 — 阻塞发布", 0.25),
    ]:
        circle = plt.Circle((0, 0), r, facecolor=color, edgecolor=color, alpha=alpha, lw=2, ls="--")
        ax.add_patch(circle)
        if r < 5.0:
            ax.annotate(label, (0, r + 0.22), ha="center", va="bottom", fontsize=8.5, color=color, fontweight="bold")

    # ── Out-of-scope outer ring label ──
    ax.annotate("Out of Scope", (5.6, 0), ha="center", va="center", fontsize=9,
                color=C["out"], fontweight="bold", rotation=0)

    # ── P0 items ──
    p0_items = [
        (0, 1.0, "ACU-001\nSchroeder"),
        (-1.0, 0.0, "ACU-002\nRBJ EQ"),
        (1.0, 0.0, "ACU-003\nHPSS"),
    ]
    for x, y, label in p0_items:
        ax.text(x, y, label, ha="center", va="center", fontsize=7.5, fontweight="bold",
                color=C["white"],
                bbox=dict(boxstyle="round,pad=0.3", facecolor=C["p0"], alpha=0.9, edgecolor="none"))

    # ── P1 items ──
    p1_items = [
        (-1.8, 2.2, "ACU-004\n7频段"),
        (1.8, 2.2, "ACU-005\nTrue Peak"),
        (0.0, 2.8, "ACU-006\n感知尺度"),
    ]
    for x, y, label in p1_items:
        ax.text(x, y, label, ha="center", va="center", fontsize=7, fontweight="bold",
                color=C["white"],
                bbox=dict(boxstyle="round,pad=0.25", facecolor=C["p1"], alpha=0.9, edgecolor="none"))

    # ── P2 items ──
    p2_items = [
        (-2.5, -1.8, "ACU-007\n掩蔽"),
        (2.5, -1.8, "ACU-008\nF0"),
        (-2.5, 0.0, "ACU-009\nChroma"),
        (2.5, 0.0, "ACU-010\nMRS"),
    ]
    for x, y, label in p2_items:
        ax.text(x, y, label, ha="center", va="center", fontsize=6.5, fontweight="bold",
                color=C["white"],
                bbox=dict(boxstyle="round,pad=0.2", facecolor=C["p2"], alpha=0.85, edgecolor="none"))

    # ── Title ──
    ax.set_title("DOC-MFY-003 v0.4 Scope Boundary", fontsize=13, fontweight="bold", color=C["text"], pad=12)
    ax.text(0, -5.6, "荣景文川（深圳）科技有限公司  |  2026-07-02", ha="center", fontsize=7.5, color=C["out"])

    # ── Legend ──
    legend_elements = [
        mpatches.Patch(color=C["p0"], alpha=0.8, label="P0 — 阻塞发布 (3 items)"),
        mpatches.Patch(color=C["p1"], alpha=0.8, label="P1 — 必须完成 (3 items)"),
        mpatches.Patch(color=C["p2"], alpha=0.8, label="P2 — 条件合入 (4 items)"),
        mpatches.Patch(color=C["pool"], alpha=0.4, label="候选池 v0.5+ (8 items)"),
        mpatches.Patch(color=C["out"], alpha=0.3, label="Out of Scope (12 items)"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=7, framealpha=0.9, edgecolor=C["edge"])

    save(fig, "scope_diagram.png")


# ═══════════════════════════════════════════════════════════════
# 2. priority_matrix.png — AEP priority x category matrix
# ═══════════════════════════════════════════════════════════════
def draw_priority():
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # ── Grid ──
    categories = ["声学修复", "感知基础", "音乐智能", "评估鲁棒"]
    priorities = ["P0\n阻塞发布", "P1\n必须完成", "P2\n条件合入"]
    cat_x = [1.2, 3.6, 6.0, 8.4]
    pri_y = [4.5, 2.7, 0.9]

    # Axes labels
    ax.text(5, 5.6, "任务类别 →", ha="center", fontsize=10, fontweight="bold", color=C["text"])
    ax.text(0.15, 3.0, "优\n先\n级", ha="center", va="center", fontsize=9, fontweight="bold",
            color=C["text"], rotation=0)

    for i, cat in enumerate(categories):
        ax.text(cat_x[i], 5.35, cat, ha="center", fontsize=9, fontweight="bold", color=C["text"])

    for j, pri in enumerate(priorities):
        ax.text(0.45, pri_y[j], pri, ha="center", va="center", fontsize=8, fontweight="bold", color=C["text"])

    # ── Task placement ──
    tasks = [
        # (cat_idx, pri_idx, label, ...)
        (0, 0, "ACU-002\nRBJ EQ\n■"),
        (0, 0, "ACU-001\nSchroeder\n■"),
        (0, 0, "ACU-003\nHPSS残差\n■"),
        (0, 1, "ACU-004\n7频段\n▲"),
        (0, 1, "ACU-005\nTrue Peak\n▲"),
        (1, 1, "ACU-006\n感知尺度\n▲"),
        (1, 2, "ACU-007\n掩蔽模型\n●"),
        (2, 2, "ACU-008\nF0音高\n●"),
        (2, 2, "ACU-009\nChroma\n●"),
        (3, 2, "ACU-010\nMRS鲁棒\n●"),
    ]

    color_map = {"P0": C["p0"], "P1": C["p1"], "P2": C["p2"]}
    p_labels = ["P0", "P0", "P0", "P1", "P1", "P1", "P2", "P2", "P2", "P2"]

    # stagger within same cell
    offsets = {}
    for ci, pi, label, *_ in tasks:
        key = (ci, pi)
        offsets[key] = offsets.get(key, 0) + 1

    used_offsets = {}
    for ci, pi, label in tasks:
        key = (ci, pi)
        used_offsets[key] = used_offsets.get(key, 0)
        n = offsets[key]
        idx = used_offsets[key]
        used_offsets[key] += 1

        x_base = cat_x[ci]
        y_base = pri_y[pi]
        # arrange horizontally within cell
        x = x_base + (idx - (n - 1) / 2) * 0.55
        y = y_base

        p = p_labels[["ACU-001", "ACU-002", "ACU-003", "ACU-004", "ACU-005", "ACU-006",
                        "ACU-007", "ACU-008", "ACU-009", "ACU-010"].index(label.split("\n")[0])]

        ax.text(x, y, label, ha="center", va="center", fontsize=6.5, fontweight="bold",
                color=C["white"],
                bbox=dict(boxstyle="round,pad=0.3", facecolor=color_map[p], alpha=0.9, edgecolor="none"))

    # ── Draw category boxes ──
    for cx in cat_x:
        ax.axvline(cx + 1.0, 0.2, 5.2, color=C["edge"], lw=1, ls="--")
    for py in pri_y:
        ax.axhline(py + 0.7, 0.5, 9.5, color=C["edge"], lw=1, ls="--")

    ax.set_title("AEP-ACU-001~010 Priority × Category Matrix", fontsize=13, fontweight="bold", color=C["text"], pad=10)
    ax.text(5, 0.0, "荣景文川（深圳）科技有限公司  |  2026-07-02", ha="center", fontsize=7.5, color=C["out"])

    legend_elements = [
        mpatches.Patch(color=C["p0"], alpha=0.8, label="P0 (3)"),
        mpatches.Patch(color=C["p1"], alpha=0.8, label="P1 (3)"),
        mpatches.Patch(color=C["p2"], alpha=0.8, label="P2 (4)"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=7.5, framealpha=0.9, edgecolor=C["edge"])

    save(fig, "priority_matrix.png")


# ═══════════════════════════════════════════════════════════════
# 3. cadence_diagram.png — 6-phase release Gantt
# ═══════════════════════════════════════════════════════════════
def draw_cadence():
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 9)
    ax.axis("off")

    phases = [
        ("P0: 章程签核", 0, 0.5, C["phase"][0], "Founder/CTO 审阅批准\nGATE-09"),
        ("P1: P0 修复", 0.5, 2.5, C["phase"][1], "ACU-001/002/003\n验收 MUST 通过"),
        ("P2: P1 补完", 2.5, 7.5, C["phase"][2], "ACU-004/005/006\n验收 MUST 通过"),
        ("P3: 回归测试", 7.5, 8.5, C["phase"][3], "全量 pytest + MRS 回归\nGATE-03~06"),
        ("P4: P2 判断", 8.5, 9.5, C["phase"][4], "P2 合入/推迟决定\n硬截止 Day 9 15:00"),
        ("P5: 封口归档", 9.5, 10.5, C["phase"][5], "DOCX/PDF + git tag\nGATE-01~09 全通过"),
    ]

    milestones = [
        ("M1\n签核", 0.5, 8.2),
        ("M2\nP0完成", 2.5, 8.2),
        ("M3\nP1完成", 7.5, 8.2),
        ("M4\n回归通过", 8.5, 8.2),
        ("M5\nP2判断", 9.5, 8.2),
        ("M6\n封口", 10.5, 8.2),
    ]

    # ── Phase bars ──
    for i, (name, start, end, color, desc) in enumerate(phases):
        width = end - start
        y = 7 - i * 1.0
        rect = FancyBboxPatch((start, y - 0.3), width, 0.75, boxstyle="round,pad=0.08",
                               facecolor=color, edgecolor="white", alpha=0.85, lw=1.5)
        ax.add_patch(rect)
        ax.text(start + width / 2, y + 0.08, name, ha="center", va="center", fontsize=9.5,
                fontweight="bold", color=C["white"])

        # Description right of bar
        if width < 1.5:
            ax.text(end + 0.15, y + 0.08, desc, ha="left", va="center", fontsize=7, color=C["text"])
        else:
            ax.text(start + width / 2, y - 0.1, desc, ha="center", va="top", fontsize=6.5,
                    color=C["white"], alpha=0.85)

    # ── Freeze gates ──
    freezes = [
        (0.5, "F-\nINPUT", C["phase"][0]),
        (2.5, "F-\nP0", C["phase"][1]),
        (7.5, "F-\nP1", C["phase"][2]),
        (8.5, "F-\nMRS", C["phase"][3]),
        (10.5, "F-\nRELEASE", C["phase"][5]),
    ]
    for x, label, color in freezes:
        ax.plot([x, x], [0.3, 6.9], color=color, lw=2, ls="--", alpha=0.6)
        ax.text(x, 0.1, label, ha="center", va="top", fontsize=6.5, fontweight="bold", color=color)

    # ── Milestones (diamonds at top) ──
    for label, x, y in milestones:
        ax.plot(x, y, "D", markersize=8, color=C["p1"], markeredgecolor="white", markeredgewidth=1)
        ax.text(x, y - 0.55, label, ha="center", fontsize=6.5, fontweight="bold", color=C["p1"])

    # ── Day axis ──
    for d in range(12):
        ax.axvline(d, 0.35, 6.75, color=C["edge"], lw=0.5, ls=":")
        if d < 11:
            ax.text(d + 0.5, 6.95, f"Day {d}", ha="center", fontsize=7, color=C["out"])

    ax.set_title("v0.4 Release Cadence — 6 Phases / 10.5 Days", fontsize=13, fontweight="bold", color=C["text"], pad=8)
    ax.text(5, -0.2, "荣景文川（深圳）科技有限公司  |  2026-07-02  |  v0.4 封口目标: 2026-07-15",
            ha="center", fontsize=7.5, color=C["out"])

    save(fig, "cadence_diagram.png")


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating DOC-MFY-003 assets...")
    draw_scope()
    draw_priority()
    draw_cadence()
    print("Done.")
