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
from typing import Any

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
        "findings_empty_text": "无（未触发阈值）" if not findings else "",
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


def launch(report_path: Path) -> int:
    """Open the window for a persisted report.json. Returns process exit code."""
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read report: {exc}", file=sys.stderr)
        return 2
    view_model = build_report_view_model(report)
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        print("tkinter is not available in this Python build", file=sys.stderr)
        return 3

    root = tk.Tk()
    root.title(view_model["title"])
    root.minsize(880, 560)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Badge.TLabel", padding=(8, 2))

    header = ttk.Frame(root, padding=(12, 10))
    header.pack(fill="x")
    ttk.Label(header, text=view_model["source_name"], font=("TkDefaultFont", 14, "bold")
              ).pack(anchor="w")
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

    notebook = ttk.Notebook(root)
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

    # — 发现 —
    findings_frame = ttk.Frame(notebook)
    notebook.add(findings_frame, text="发现")
    findings_text = tk.Text(findings_frame, wrap="word", borderwidth=0, height=10)
    if view_model["findings"]:
        for f in view_model["findings"]:
            calib = f" · 阈值 {f['calibration_status']}" if f["calibration_status"] else ""
            findings_text.insert("end", f"[{f['severity']}] {f['code']}{calib}\n", "finding_head")
            findings_text.insert("end", f"  {f['message']}\n\n")
    else:
        findings_text.insert("end", view_model["findings_empty_text"] + "\n")
    findings_text.configure(state="disabled")
    findings_text.pack(fill="both", expand=True)

    # — 后处理方案 —
    plan_frame = ttk.Frame(notebook)
    notebook.add(plan_frame, text="后处理方案")
    plan_text = tk.Text(plan_frame, wrap="word", borderwidth=0)
    plan_text.insert("end", f"状态：{view_model['plan_status']}", "badge")
    plan_text.insert("end", "（方案不等于执行；执行需显式提交 process 作业）\n\n", "muted")
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
    plan_text.configure(state="disabled")
    plan_text.pack(fill="both", expand=True)

    # — 边界与来源 —
    boundary_frame = ttk.Frame(notebook)
    notebook.add(boundary_frame, text="边界与来源")
    boundary_text = tk.Text(boundary_frame, wrap="word", borderwidth=0)
    boundary_text.insert("end", "判断边界\n", "section")
    for layer in view_model["boundary"]:
        boundary_text.insert("end", f"· {layer['layer']}：{layer['state']}\n")
    summary = view_model["calibration_summary"]
    if summary.get("calibrated") is not None:
        boundary_text.insert("end", "\n阈值校准\n", "section")
        boundary_text.insert(
            "end",
            f"· {summary['calibrated']}/{summary['calibrated'] + summary['default_uncalibrated']} "
            f"条已校准，其余 DEFAULT_UNCALIBRATED\n")
        if summary.get("note"):
            boundary_text.insert("end", f"· {summary['note']}\n")
    boundary_text.configure(state="disabled")
    boundary_text.pack(fill="both", expand=True)

    for tag, kwargs in (("finding_head", {"font": ("TkDefaultFont", 10, "bold")}),
                        ("badge", {"font": ("TkDefaultFont", 10, "bold")}),
                        ("muted", {"foreground": "#555"}),
                        ("section", {"font": ("TkDefaultFont", 11, "bold")})):
        findings_text.tag_configure(tag, **kwargs)
        plan_text.tag_configure(tag, **kwargs)
        boundary_text.tag_configure(tag, **kwargs)

    footer = ttk.Frame(root, padding=(12, 8))
    footer.pack(fill="x")
    html_path = report_path.with_name("report.html")
    if html_path.is_file():
        ttk.Button(footer, text="打开 HTML 报告（导出物）",
                   command=lambda: _open_html(html_path)).pack(side="left")
    ttk.Button(footer, text="退出", command=root.destroy).pack(side="right")

    root.mainloop()
    return 0


def _fmt_num(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:g}"
    return "—" if value is None else str(value)


def _open_html(html_path: Path) -> None:
    import webbrowser

    webbrowser.open(html_path.resolve().as_uri())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python -m moodify.ui.report_window <report.json>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(launch(Path(sys.argv[1])))
