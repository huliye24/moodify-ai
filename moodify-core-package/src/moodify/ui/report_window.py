"""The Moodify report window — a native display surface for 0.2 reports.

Run standalone against a persisted report:

    python -m moodify.ui.report_window <path/to/report.json>

``build_report_view_model`` is pure and testable; ``launch`` owns the only
tkinter surface so headless environments never instantiate Tk. The window
renders the same facts as report.md/report.html — no new judgment, no new
measurement, no plan execution.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import matplotlib.figure

_WINDOW_TITLE = "Moodify — 听觉报告"

_BOUNDARY_LABELS = {
    "layer1_measurement": "L1 测量",
    "layer2_comparison": "L2 对比",
    "layer3_musical_judgment": "L3 音乐判断",
    "layer4_production_judgment": "L4 制作判断",
    "layer5_cultural_judgment": "L5 文化判断",
}


def build_report_view_model(report: dict[str, Any]) -> dict[str, Any]:
    """Map a 0.2 report.json onto widget-ready data (pure, no tkinter)."""
    source = report.get("source") or {}
    technical = report.get("technical_state") or {}
    case = report.get("case") or {}
    plan = report.get("plan") or {}
    boundary = report.get("judgment_boundary") or {}
    provenance = report.get("provenance") or {}
    calibration = provenance.get("judgment_calibration") or {}

    measurements = [
        {
            "id": m.get("id", "?"),
            "value": _format_value(m.get("value")),
            "unit": m.get("unit", ""),
            "status": m.get("status", "?"),
            "group": m.get("group", ""),
        }
        for m in report.get("measurements") or []
    ]
    findings = [
        {
            "severity": f.get("severity", "?"),
            "code": f.get("code", "?"),
            "message": f.get("message", ""),
            "calibration_status": f.get("calibration_status"),
        }
        for f in report.get("findings") or []
    ]
    return {
        "title": _WINDOW_TITLE,
        "source_name": source.get("name", "?"),
        "duration_s": source.get("duration_s"),
        "channels": source.get("channels"),
        "sample_rate": source.get("sample_rate"),
        "case_id": case.get("case_id", "?"),
        "overall": technical.get("overall", "?"),
        "workflow_decision": technical.get("workflow_decision", "?"),
        "protocol": report.get("protocol", "?"),
        "generated_at": report.get("generated_at", "?"),
        "measurements": measurements,
        "findings": findings,
        "plan_status": plan.get("status", "?"),
        "plan_nodes": [
            {"operator": n.get("operator", "?"), "reason": n.get("reason", "")}
            for n in plan.get("nodes") or []
        ],
        "plan_notes": list(plan.get("notes") or []),
        "plan_next_actions": list(plan.get("next_actions") or []),
        "boundary": [
            {"layer": label, "state": boundary.get(key, "?")}
            for key, label in _BOUNDARY_LABELS.items()
        ],
        "calibration_summary": {
            "calibrated": calibration.get("calibrated"),
            "default_uncalibrated": calibration.get("default_uncalibrated"),
            "note": calibration.get("note", ""),
        },
    }


def _format_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


# ——— 图表：只画实测事实（matplotlib，MATLAB 风格；不做阈值着色，不构成判断） ———

_DB_UNITS = {"LUFS", "dBFS", "dB", "LU"}


def select_chart_measurements(measurements: list[dict[str, Any]]) -> dict[str, list[tuple[str, float]]]:
    """Split raw measurements into chart-ready series (pure, unit-honest).

    Bands share one ratio axis; loudness/level values share one dB axis;
    stereo ratios share a 0..1 axis. Values with other units are never
    mixed onto an axis they do not belong to.
    """
    bands = [(m["id"], float(m["value"])) for m in measurements
             if m.get("group") == "bands"]
    levels = [(m["id"], float(m["value"])) for m in measurements
              if m.get("group") == "loudness" and m.get("unit") in _DB_UNITS]
    stereo = [(m["id"], float(m["value"])) for m in measurements
              if m.get("group") == "stereo" and m.get("unit") == "ratio"]
    return {"bands": bands, "levels_db": levels, "stereo_ratios": stereo}


def _chart_style() -> None:
    import matplotlib

    matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False


def _barh_figure(rows: list[tuple[str, float]], title: str, xlabel: str,
                 log_x: bool, value_fmt: str = "{:.4g}") -> matplotlib.figure.Figure:
    from matplotlib.figure import Figure

    _chart_style()
    fig = Figure(figsize=(7.6, max(2.2, 0.42 * len(rows) + 1.1)), dpi=100)
    axis = fig.add_subplot(111)
    if not rows:
        axis.set_title(title, fontsize=11)
        axis.text(0.5, 0.5, "无可绘图数据", ha="center", va="center",
                  transform=axis.transAxes, color="#555")
        axis.set_axis_off()
        return fig
    labels = [name for name, _ in rows]
    values = [value for _, value in rows]
    positions = range(len(rows))
    axis.barh(positions, values, color="#4878a8", align="center")
    axis.set_yticks(list(positions))
    axis.set_yticklabels(labels, fontsize=8)
    axis.invert_yaxis()
    if log_x:
        axis.set_xscale("log")
    axis.set_xlabel(xlabel, fontsize=9)
    axis.set_title(title, fontsize=11)
    axis.grid(True, axis="x", alpha=0.3)
    if log_x:
        axis.set_xlim(right=max(values) * 3)
    span = (max(values) - min(values)) or 1.0
    for y_pos, value in zip(positions, values):
        offset = span * 0.015
        axis.text(value + (offset if not log_x else value * 0.06 + max(values) * 1e-4),
                  y_pos, value_fmt.format(value), va="center", fontsize=7.5, color="#333")
    fig.tight_layout()
    return fig


def build_band_figure(rows: list[tuple[str, float]]) -> matplotlib.figure.Figure:
    """Band energy ratios span four orders of magnitude — log axis keeps the
    top and the air band visible at once. Descriptive only: no threshold
    coloring (0/16 thresholds calibrated)."""
    return _barh_figure(rows, "频段能量占比（实测）", "ratio（log 轴）", log_x=True)


def build_level_figure(rows: list[tuple[str, float]]) -> matplotlib.figure.Figure:
    return _barh_figure(rows, "电平与响度（实测）", "dB 域（LUFS/dBFS/dB/LU）", log_x=False)


def build_stereo_figure(rows: list[tuple[str, float]]) -> matplotlib.figure.Figure:
    return _barh_figure(rows, "立体声分布（实测）", "ratio", log_x=False)


def build_report_frame(parent, report: dict[str, Any], report_path: Path,
                       on_back: Any = None):
    """Build the report view inside ``parent`` (a Tk widget).

    Used by the standalone report window (``launch``) and embedded by the
    desktop app hub. ``on_back`` adds an in-app "← 档案" navigation button;
    with no callback (single-case view) the window shows nothing that
    leads out of the report.
    """
    import tkinter as tk
    from tkinter import ttk

    from moodify.ui.theme import load_logo

    view_model = build_report_view_model(report)
    frame = ttk.Frame(parent)

    header = ttk.Frame(frame, padding=(12, 10))
    header.pack(fill="x")
    title_line = ttk.Frame(header)
    title_line.pack(fill="x")
    logo = load_logo(168)
    if logo is not None:
        ttk.Label(title_line, image=logo).pack(side="left", padx=(0, 14))
        title_line.image = logo
    ttk.Label(title_line, text=view_model["source_name"], font=("TkDefaultFont", 14, "bold")
              ).pack(side="left")
    if on_back is not None:
        ttk.Button(title_line, text="← 档案", command=on_back).pack(side="right")
    badge_line = ttk.Frame(header)
    badge_line.pack(anchor="w", pady=(4, 0))
    for text, kind in ((view_model["overall"], "state"),
                       (view_model["workflow_decision"], "decision")):
        ttk.Label(badge_line, text=text, style="Badge.TLabel", relief="solid").pack(side="left", padx=(0, 6))
    meta = (f"case {view_model['case_id']} · {view_model['protocol']} · "
            f"{_fmt_num(view_model['duration_s'])}s · "
            f"{_fmt_num(view_model['channels'])}ch @ {_fmt_num(view_model['sample_rate'])}Hz · "
            f"生成于 {view_model['generated_at']}")
    ttk.Label(header, text=meta, foreground="#555").pack(anchor="w", pady=(4, 0))

    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True, padx=12, pady=8)

    # — 测量 —
    measure_frame = ttk.Frame(notebook)
    notebook.add(measure_frame, text="测量")
    cols = ("id", "value", "unit", "status", "group")
    tree = ttk.Treeview(measure_frame, columns=cols, show="headings")
    for key, text, width in (("id", "指标", 260), ("value", "值", 110), ("unit", "单位", 90),
                             ("status", "状态", 80), ("group", "组", 120)):
        tree.heading(key, text=text)
        tree.column(key, width=width, anchor="w")
    for row in view_model["measurements"]:
        tree.insert("", "end", values=[row[c] for c in cols])
    scroll = ttk.Scrollbar(measure_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    # — 图表（实测事实可视化；MATLAB 风格 matplotlib，无阈值着色） —
    charts = ttk.Notebook(notebook)
    notebook.add(charts, text="图表")

    spec_frame = ttk.Frame(charts)
    charts.add(spec_frame, text="频谱")
    scan_dir = report_path.parent / "scan"
    spec_shown = False
    for png_name in ("spectrum_log.png", "spectrum_linear.png"):
        png_path = scan_dir / png_name
        if not png_path.is_file():
            continue
        try:
            photo = tk.PhotoImage(file=str(png_path))
            factor = max(1, photo.width() // 820, photo.height() // 480)
            if factor > 1:
                photo = photo.subsample(factor)
            ttk.Label(spec_frame, image=photo).pack(padx=8, pady=8)
            spec_frame.image = photo  # keep a reference (photo is GC-able otherwise)
            spec_shown = True
            break
        except tk.TclError:
            continue
    if not spec_shown:
        ttk.Label(spec_frame, foreground="#555",
                  text="无频谱图产物（scan/spectrum_*.png 缺失）").pack(padx=12, pady=12)
    ttk.Label(spec_frame, foreground="#555",
              text="实测频谱渲染；不构成审美或平台适配判断").pack(pady=(0, 8))

    chart_series = select_chart_measurements(report.get("measurements") or [])
    for sub_title, rows, builder in (
            ("频段", chart_series["bands"], build_band_figure),
            ("电平", chart_series["levels_db"], build_level_figure),
            ("立体声", chart_series["stereo_ratios"], build_stereo_figure)):
        sub_frame = ttk.Frame(charts)
        charts.add(sub_frame, text=sub_title)
        if not rows:
            ttk.Label(sub_frame, foreground="#555",
                      text="无可绘图数据").pack(padx=12, pady=12)
            continue
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            ttk.Label(sub_frame, foreground="#555",
                      text="matplotlib 不可用，图表跳过").pack(padx=12, pady=12)
            continue
        canvas = FigureCanvasTkAgg(builder(rows), master=sub_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Label(sub_frame, foreground="#555",
                  text="实测值展示；阈值 0/16 已校准（全部 DEFAULT_UNCALIBRATED）——本图不做好坏判断").pack(pady=(0, 6))

    # — 后处理方案（触发判定规则的发现折叠在此：没有发现时保持纯净） —
    plan_frame = ttk.Frame(notebook)
    notebook.add(plan_frame, text="后处理方案")
    plan_text = tk.Text(plan_frame, wrap="word", borderwidth=0)
    plan_text.insert("end", f"状态：{view_model['plan_status']}", "badge")
    plan_text.insert("end", "（方案不等于执行；执行需显式提交 process 作业）\n\n", "muted")
    if view_model["findings"]:
        plan_text.insert("end", "发现\n", "section")
        for f in view_model["findings"]:
            calib = f" · 阈值 {f['calibration_status']}" if f["calibration_status"] else ""
            plan_text.insert("end", f"[{f['severity']}] {f['code']}{calib}\n", "finding_head")
            plan_text.insert("end", f"  {f['message']}\n\n")
    if view_model["plan_nodes"]:
        for node in view_model["plan_nodes"]:
            plan_text.insert("end", f"◆ {node['operator']}\n  {node['reason']}\n\n")
    else:
        plan_text.insert("end", "无自动算子建议（未发现可安全映射到标准算子的发现）。\n\n", "muted")
    for note in view_model["plan_notes"]:
        plan_text.insert("end", f"· {note}\n")
    if view_model["plan_next_actions"]:
        plan_text.insert("end", "\n下一步：\n")
        for action in view_model["plan_next_actions"]:
            plan_text.insert("end", f"→ {action}\n")
    plan_text.insert("end", "\n本窗口只呈现 L1 技术测量与保守草案；不含听感、音乐或商业判断。\n", "muted")
    plan_text.configure(state="disabled")
    plan_text.pack(fill="both", expand=True)

    for tag, kwargs in (("finding_head", {"font": ("TkDefaultFont", 10, "bold")}),
                        ("badge", {"font": ("TkDefaultFont", 10, "bold")}),
                        ("muted", {"foreground": "#555"}),
                        ("section", {"font": ("TkDefaultFont", 11, "bold")})):
        plan_text.tag_configure(tag, **kwargs)

    # no footer buttons by design: nothing inside the window leads out of the
    # Moodify ecosystem — the OS title bar closes the window
    return frame


def launch(report_path: Path) -> int:
    """Open a standalone report window for one persisted case. Returns exit code."""
    try:
        report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read report: {exc}", file=sys.stderr)
        return 2
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        print("tkinter is not available in this Python build", file=sys.stderr)
        return 3

    root = tk.Tk()
    root.title(_WINDOW_TITLE)
    root.minsize(880, 560)
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    from moodify.ui.theme import apply_white_theme, set_app_icon

    apply_white_theme(root, style)
    set_app_icon(root)
    build_report_frame(root, report, Path(report_path))
    root.mainloop()
    return 0


def _fmt_num(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:g}"
    return "—" if value is None else str(value)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python -m moodify.ui.report_window <report.json>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(launch(Path(sys.argv[1])))
