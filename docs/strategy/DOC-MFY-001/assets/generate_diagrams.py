"""Generate strategic diagrams for DOC-MFY-001. Outputs to assets/ directory."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc, Circle, Wedge
import numpy as np
import os

OUT = os.path.dirname(os.path.abspath(__file__))
plt.rcParams['font.family'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['font.size'] = 11

# Colors
C = {
    'deep': '#1a1a2e', 'navy': '#16213e', 'teal': '#0f3460',
    'red': '#e94560', 'gold': '#f0a500', 'green': '#2d9c6b',
    'blue': '#3a7ca5', 'purple': '#6b2fa0', 'pink': '#d4756b',
    'light': '#e8e8e8', 'white': '#ffffff', 'grey': '#888888',
    'orange': '#e8a87c', 'dark_green': '#1a5c3a',
    'cyan': '#4ecdc4', 'magenta': '#c44dff',
}

# ── Fig 1: Non-Code Asset Stack ────────────────────────────
def fig1_asset_stack():
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    layers = [
        (0.5, 0.2, "代码层 (CODE)", "DSP 算子 · CLI · API · 控制台", C['grey'], 0.7),
        (0.5, 1.9, "数据层 (DATA)", "10 PHYS + 7 ENG 实验 · MRS 参考统计 · 工艺存储器", C['blue'], 0.75),
        (0.5, 3.6, "模型层 (MODEL)", "B 矩阵 · T_EFFECTS · DeepSeek 情绪映射 · 在线校准", C['teal'], 0.8),
        (0.5, 5.3, "工艺层 (CRAFT)", "8 情绪原型 · 15 参数工艺链 · 禁忌症 · 缺陷分类", C['purple'], 0.85),
        (0.5, 7.0, "理论层 (THEORY)", "5 维波场 · 18 参数诊断 · PHYS 守恒定理", C['red'], 0.9),
        (0.5, 8.5, "硬件层 (HARDWARE)", "GPU 服务器 · 声学测量 · 专用 DSP (路线图)", C['dark_green'], 0.92),
    ]

    for x, y, title, desc, color, alpha in layers:
        box = FancyBboxPatch((x, y), 9.0, 1.2, boxstyle="round,pad=0.08",
                             facecolor=color, edgecolor='white', linewidth=1.5, alpha=alpha, zorder=2)
        ax.add_patch(box)
        ax.text(x + 4.5, y + 0.7, title, ha='center', va='center', fontsize=14, fontweight='bold', color='white', zorder=3)
        ax.text(x + 4.5, y + 0.25, desc, ha='center', va='center', fontsize=9, color='#dddddd', zorder=3)

    # Arrows showing asset flow
    for i in range(len(layers) - 1):
        y_from = layers[i][1] + 0.6
        y_to = layers[i+1][1] + 0.6
        ax.annotate('', xy=(5.5, y_to), xytext=(5.5, y_from),
                    arrowprops=dict(arrowstyle='->', color=C['gold'], lw=2.5, connectionstyle='arc3,rad=0'))

    # Right side annotation
    ax.text(9.8, 5.0, '复制\n难度\n递增', ha='center', va='center', fontsize=12,
            fontweight='bold', color=C['gold'], rotation=90,
            bbox=dict(boxstyle='round', facecolor=C['deep'], edgecolor=C['gold'], alpha=0.9))

    ax.text(5.0, 9.8, 'Moodify 非代码化资产栈', ha='center', va='center', fontsize=18,
            fontweight='bold', color=C['deep'])
    ax.text(5.0, 9.35, '每一层都是代码层之上的增量壁垒', ha='center', va='center', fontsize=11, color=C['grey'])

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, '01_asset_stack.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)


# ── Fig 2: Experiment Flywheel ──────────────────────────────
def fig2_experiment_flywheel():
    fig, ax = plt.subplots(1, 1, figsize=(11, 10))
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.axis('off')
    ax.set_aspect('equal')

    steps = [
        ("① 假设形成", "理论驱动\n或异常驱动", C['red']),
        ("② 实验设计", "控制变量\n测量协议", C['orange']),
        ("③ 数据采集", "处理前后\n多维度测量", C['gold']),
        ("④ 公式/模型\n更新", "B 矩阵修正\n规则更新", C['green']),
        ("⑤ 代码实现", "新处理策略\n编码", C['cyan']),
        ("⑥ 上线验证", "在线校准\n三评委评估", C['blue']),
        ("⑦ 新假设", "来自验证中\n发现的异常", C['purple']),
    ]

    n = len(steps)
    radius = 4.2
    node_radius = 1.1

    for i, (title, desc, color) in enumerate(steps):
        angle = 2 * np.pi * i / n - np.pi / 2
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)

        circle = Circle((x, y), node_radius, facecolor=color, edgecolor='white', linewidth=2, alpha=0.9, zorder=2)
        ax.add_patch(circle)
        ax.text(x, y + 0.2, title, ha='center', va='center', fontsize=11, fontweight='bold', color='white', zorder=3)
        ax.text(x, y - 0.35, desc, ha='center', va='center', fontsize=8, color='#eeeeee', zorder=3)

    # Arrows between nodes
    for i in range(n):
        angle_from = 2 * np.pi * i / n - np.pi / 2
        angle_to = 2 * np.pi * (i + 1) / n - np.pi / 2
        x_from = (radius - node_radius - 0.15) * np.cos(angle_from)
        y_from = (radius - node_radius - 0.15) * np.sin(angle_from)
        x_to = (radius - node_radius - 0.15) * np.cos(angle_to)
        y_to = (radius - node_radius - 0.15) * np.sin(angle_to)

        ax.annotate('', xy=(x_to, y_to), xytext=(x_from, y_from),
                    arrowprops=dict(arrowstyle='->', color=C['deep'], lw=3,
                                   connectionstyle=f'arc3,rad={0.40 if i%2==0 else 0.35}'))

    # Center text
    center = Circle((0, 0), 1.3, facecolor=C['deep'], edgecolor=C['gold'], linewidth=2.5, zorder=2)
    ax.add_patch(center)
    ax.text(0, 0.15, "实验飞轮", ha='center', va='center', fontsize=16, fontweight='bold', color='white', zorder=3)
    ax.text(0, -0.35, "每次完整旋转\n产出 3 类资产", ha='center', va='center', fontsize=9, color=C['gold'], zorder=3)

    # Legend boxes for asset types
    for j, (label, x_pos, color) in enumerate([
        ("可量化: 数据点, B 矩阵", -5.5, C['green']),
        ("半量化: 规则, 风险模型", 0, C['orange']),
        ("非量化: 听感经验, 判断", 5.5, C['purple']),
    ]):
        ax.text(x_pos, -5.3, label, ha='center', va='center', fontsize=9,
                bbox=dict(boxstyle='round', facecolor=color, alpha=0.3, edgecolor=color))

    ax.text(0, 5.8, 'Moodify 声学实验飞轮 — 核心代谢机制', ha='center', va='center',
            fontsize=16, fontweight='bold', color=C['deep'])

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, '02_experiment_flywheel.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)


# ── Fig 3: Expansion Path ───────────────────────────────────
def fig3_expansion_path():
    fig, ax = plt.subplots(1, 1, figsize=(14, 6))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6)
    ax.axis('off')

    ax.text(7, 5.8, 'Moodify 模型层与硬件层扩张路径', ha='center', va='center',
            fontsize=16, fontweight='bold', color=C['deep'])

    # Timeline
    ax.plot([1.5, 12.5], [4.5, 4.5], 'k-', lw=2, color=C['grey'])
    for t, label in [(2.5, '当前'), (6, '近期 (1-18 月)'), (10.5, '远期 (18+ 月)')]:
        ax.plot([t, t], [4.3, 4.7], 'k-', lw=2, color=C['grey'])
        ax.text(t, 4.15, label, ha='center', fontsize=10, color=C['grey'])

    # Model layer
    ax.text(0.5, 3.3, '模型层', fontsize=13, fontweight='bold', color=C['deep'], rotation=90, va='center')

    models = [
        (2.5, 3.5, "M1: 参数映射\nT_EFFECTS", C['blue'], 0.7),
        (2.5, 2.6, "M2: 代理模型\nB 矩阵", C['teal'], 0.75),
        (6, 3.5, "M3: AI 判断\nDeepSeek + 三评委", C['purple'], 0.8),
        (6, 2.6, "M2+: 非线性代理\n岭回归 + 核方法", C['teal'], 0.8),
        (10.5, 3.5, "M4: 专用声学模型\n微调小模型", C['red'], 0.9),
        (10.5, 2.6, "M3+: 自动化评判\nAI 评委替代人工", C['purple'], 0.85),
    ]
    for x, y, label, color, alpha in models:
        box = FancyBboxPatch((x-1.0, y-0.35), 2.0, 0.7, boxstyle="round,pad=0.05",
                             facecolor=color, edgecolor='white', linewidth=1.2, alpha=alpha, zorder=2)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=9, color='white', fontweight='bold', zorder=3)

    # Hardware layer
    ax.text(0.5, 1.2, '硬件层', fontsize=13, fontweight='bold', color=C['deep'], rotation=90, va='center')

    hardwares = [
        (2.5, 1.5, "通用 GPU\nRTX 4060 + 3×云服务器", C['green'], 0.7),
        (6, 1.5, "专用推理\nA100/H100 GPU 集群", C['dark_green'], 0.78),
        (10.5, 1.5, "定制芯片\n专用声学处理 ASIC", C['dark_green'], 0.9),
        (10.5, 0.6, "声学测量硬件\n标定麦克风 + 消声室", C['orange'], 0.85),
    ]
    for x, y, label, color, alpha in hardwares:
        box = FancyBboxPatch((x-1.15, y-0.35), 2.3, 0.7, boxstyle="round,pad=0.05",
                             facecolor=color, edgecolor='white', linewidth=1.2, alpha=alpha, zorder=2)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=9, color='white', fontweight='bold', zorder=3)

    # Growth arrows
    ax.annotate('', xy=(3.6, 4.5), xytext=(1.2, 4.5),
                arrowprops=dict(arrowstyle='->', color=C['gold'], lw=2.5))
    ax.annotate('', xy=(8.4, 4.5), xytext=(4.4, 4.5),
                arrowprops=dict(arrowstyle='->', color=C['gold'], lw=2.5))
    ax.annotate('', xy=(11.8, 4.5), xytext=(7.4, 4.5),
                arrowprops=dict(arrowstyle='->', color=C['gold'], lw=2.5))

    # Moat depth indicator
    ax.text(13.2, 3.3, '护城河\n深度\n递增', ha='center', va='center', fontsize=10,
            fontweight='bold', color=C['gold'],
            bbox=dict(boxstyle='round', facecolor=C['deep'], edgecolor=C['gold'], alpha=0.9))

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, '03_expansion_path.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)


# ── Fig 4: Competition Hierarchy ────────────────────────────
def fig4_competition_hierarchy():
    fig, ax = plt.subplots(1, 1, figsize=(11, 8))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8)
    ax.axis('off')

    ax.text(5.5, 7.7, 'Moodify 竞争层级模型 — 五层升维压制', ha='center', va='center',
            fontsize=16, fontweight='bold', color=C['deep'])

    levels = [
        (0.5, 5.8, "L5 生态层", "文档·数据·模型·硬件闭环", C['red'], "不存在", "终极目标"),
        (0.5, 4.5, "L4 实验层", "自我校正·自我进化", C['purple'], "稀缺", "在线校准 + 飞轮"),
        (0.5, 3.2, "L3 知识层", "情绪原型·工艺链·禁忌症", C['teal'], "少数", "8 情绪 × 15 参数"),
        (0.5, 1.9, "L2 诊断层", "18 参数波场诊断", C['blue'], "Ozone, LANDR", "竞品 3-5 参数"),
        (0.5, 0.6, "L1 功能层", "EQ·压缩·混响·限制器", C['green'], "任何会写代码的人", "已完成 v0.1"),
    ]

    for x, y, title, desc, color, competitor, moodify_status in levels:
        box = FancyBboxPatch((x, y), 9.5, 1.0, boxstyle="round,pad=0.06",
                             facecolor=color, edgecolor='white', linewidth=1.5, alpha=0.85, zorder=2)
        ax.add_patch(box)
        ax.text(x + 0.3, y + 0.65, title, fontsize=13, fontweight='bold', color='white', zorder=3)
        ax.text(x + 0.3, y + 0.25, desc, fontsize=10, color='#dddddd', zorder=3)
        ax.text(x + 5.5, y + 0.65, f"竞品: {competitor}", fontsize=9, color='white', ha='center', zorder=3,
                bbox=dict(boxstyle='round', facecolor='black', alpha=0.3))
        ax.text(x + 8.5, y + 0.65, moodify_status, fontsize=9, color=C['gold'], ha='center', fontweight='bold', zorder=3)

    # Downward arrows showing "dimensional suppression"
    for i in range(len(levels) - 1):
        y_from = levels[i][1] + 0.3
        y_to = levels[i+1][1] + 0.7
        ax.annotate('', xy=(5.5, y_to), xytext=(5.5, y_from),
                    arrowprops=dict(arrowstyle='->', color=C['gold'], lw=3))
        ax.text(6.8, (y_from + y_to) / 2, '压制 ↓', fontsize=8, color=C['gold'], fontweight='bold')

    # Right side: competitive moat
    for i, (_, y, _, _, color, _, _) in enumerate(levels):
        moat_width = 0.4 + i * 0.25
        ax.text(10.5, y + 0.5, f'壁垒\n{moat_width:.1f}x', ha='center', va='center', fontsize=9,
                color='white', fontweight='bold',
                bbox=dict(boxstyle='circle', facecolor=color, edgecolor=C['gold'], linewidth=1.5))

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, '04_competition_hierarchy.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)


# ── Fig 5: Knowledge Layer Classification ───────────────────
def fig5_knowledge_layers():
    fig, ax = plt.subplots(1, 1, figsize=(11, 6.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6.5)
    ax.axis('off')

    ax.text(5.5, 6.3, 'Moodify 知识体系四层分类', ha='center', va='center',
            fontsize=16, fontweight='bold', color=C['deep'])

    knowledge = [
        (0.5, 4.6, "L1 完全可编码", "公式 · 算法 · 规则 · 频段定义",
         C['green'], "高——AI 可直接学习", "频段定义、FFT 参数、诊断规则"),
        (0.5, 3.2, "L2 半可编码", "参数范围 · 约束 · 禁忌症",
         C['blue'], "中——边界条件是经验性的", "情绪目标向量、禁忌症表、风险阈值"),
        (0.5, 1.8, "L3 隐性知识", "听觉判断 · 审美标准 · 听感描述",
         C['purple'], "低——人类专家独有", "L4/E1/E2 主观评分、'温暖的混响'"),
        (0.5, 0.4, "L4 元知识", "实验方法论 · 知识创造过程",
         C['red'], "极低——嵌入组织惯例", "实验设计方法、校准策略、失效分析"),
    ]

    for x, y, title, desc, color, risk, example in knowledge:
        box = FancyBboxPatch((x, y), 7.5, 1.1, boxstyle="round,pad=0.06",
                             facecolor=color, edgecolor='white', linewidth=1.5, alpha=0.85, zorder=2)
        ax.add_patch(box)
        ax.text(x + 0.3, y + 0.7, title, fontsize=13, fontweight='bold', color='white', zorder=3)
        ax.text(x + 0.3, y + 0.3, desc, fontsize=10, color='#dddddd', zorder=3)
        ax.text(x + 6.0, y + 0.7, f'复制风险: {risk}', fontsize=9, color=C['gold'], ha='center', zorder=3)
        ax.text(x + 9.8, y + 0.55, example, fontsize=8, color=C['grey'], ha='center', zorder=3)

    # Arrow showing knowledge depth
    ax.annotate('', xy=(10.5, 0.3), xytext=(10.5, 5.8),
                arrowprops=dict(arrowstyle='->', color=C['gold'], lw=2.5))
    ax.text(10.5, 3.1, '知识\n深度\n递增', ha='center', va='center', fontsize=10,
            fontweight='bold', color=C['gold'], rotation=90)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, '05_knowledge_layers.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    fig1_asset_stack()
    fig2_experiment_flywheel()
    fig3_expansion_path()
    fig4_competition_hierarchy()
    fig5_knowledge_layers()
    print(f"Generated 5 diagrams in {OUT}/")
