"""Moodify Lab — the research workbench inside the desktop app.

The human's directive (2026-10-02): a research-grade GUI comes first, then
the CLI — we need to see what is happening, what can happen, and how to
optimize and iterate. The lab answers all three from artifacts that already
exist on disk; it orchestrates, it never adds DSP or thresholds:

- 观测 (observation): stage-level provenance of one case — job, input hash,
  scan profile, evidence chain, the judgment rules that were in force, and
  the representation layer. Reading persisted facts, nothing more.
- 目录 (catalog): the honest capability map — what the machine CAN do and
  where each capability lives. Statuses come from REPOSITORY_STATUS values;
  nothing is presented as runnable that is not reachable from this window.
- 实验 (experiment): A/B comparison through the 0.2 ``compare`` job — the
  same validate/execute path as every other job. Observation only: no
  parameter may be written back, no threshold edited (L3 decision, deferred).

Development doctrine (human-adjudicated): new capabilities surface here
first; once stable they condense into CLI commands. One core, two
interfaces — the lab is the human research face.
"""

from __future__ import annotations

import json
import queue
import threading
from pathlib import Path
from typing import Any

_CASES_TAB = ("观测", "目录", "实验")

_HASH_DISPLAY = 18  # sha256 shown truncated; full value lives in the artifacts


# ——— 观测区：从档案事实装配过程视图（纯函数，可测） ———


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _read_json_any(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _rule_limits_text(spec: dict[str, Any]) -> str:
    """Render one universal threshold's limits without inventing semantics."""
    metric = spec.get("metric", "?")
    parts = [f"metric={metric}"]
    for key, value in spec.items():
        if key in ("metric", "_source", "source", "status", "date_added"):
            continue
        parts.append(f"{key}={value}")
    source = spec.get("_source") or spec.get("source") or ""
    if isinstance(source, dict):
        source = source.get("status", "")
    if source:
        parts.append(f"source={source}")
    return " ".join(parts)


def load_case_provenance(case_root: Path) -> dict[str, Any]:
    """Assemble the observation view of one case from persisted facts.

    Tolerant by design: a partially written case shows what exists and
    marks the rest absent — the lab must survive an interrupted analysis.
    """
    case_root = Path(case_root)
    report = _read_json(case_root / "report.json")
    manifest = _read_json(case_root / "scan" / "scan_manifest.json")
    rules_doc = _read_json(case_root / "judgment_rules.json")
    evidence_raw = _read_json_any(case_root / "evidence.json")
    case = report.get("case") or {}
    job = report.get("job") or {}
    source = report.get("source") or {}
    representation = report.get("representation") or {}
    evidence = [
        {
            "artifact_type": rec.get("artifact_type", "?"),
            "logical_path": rec.get("logical_path", "?"),
            "hash": str(rec.get("content_hash", "?"))[:_HASH_DISPLAY],
            "created_at": rec.get("created_at", "?"),
            "size_bytes": rec.get("size_bytes"),
        }
        for rec in (evidence_raw if isinstance(evidence_raw, list)
                    else evidence_raw.get("records") or []
                    if isinstance(evidence_raw, dict) else [])
    ]
    rules = [
        {"id": rule_id, "text": _rule_limits_text(spec)}
        for rule_id, spec in (rules_doc.get("universal_thresholds") or {}).items()
        if isinstance(spec, dict)
    ]
    artifacts = [
        {"name": name, "path": str(spec.get("path", "?")) if isinstance(spec, dict) else str(spec)}
        for name, spec in (manifest.get("artifacts") or {}).items()
    ]
    return {
        "case_id": case.get("case_id", case_root.name),
        "exists": bool(report),
        "job_type": job.get("type", "?"),
        "protocol": report.get("protocol", "?"),
        "source_name": source.get("name", "?"),
        "input_sha256": str(manifest.get("input_sha256", "?"))[:_HASH_DISPLAY],
        "profile_id": manifest.get("scan_profile_id",
                                   (report.get("provenance") or {}).get("profile_id", "?")),
        "stage": manifest.get("stage", "?"),
        "evidence": evidence,
        "rules": rules,
        "artifacts": artifacts,
        "representation": {
            "timeline_windows": representation.get("timeline_windows"),
            "stft_arrays": representation.get("stft_arrays", "?"),
            "timeline_path": representation.get("timeline_path", "?"),
        },
    }


# ——— 能力目录：机器可以发生什么（诚实状态，入口可核查） ———

_CAPABILITY_STATUSES = {"CANONICAL", "EXPERIMENTAL", "EXPERIMENTAL_ACCEPTED",
                        "READY", "LEGACY", "HISTORICAL", "ABSENT", "UNRESOLVED"}

CAPABILITY_CATALOG: list[dict[str, str]] = [
    {"name": "0.2 analyze 作业", "domain": "协议", "status": "EXPERIMENTAL",
     "what": "纯读取分析 → 报告三件套（无新 DSP）",
     "entry": "本实验台·观测区 / moodify demo"},
    {"name": "0.2 compare 作业", "domain": "协议", "status": "EXPERIMENTAL",
     "what": "A/B 对比：响度对齐 + delta 只描述不评级",
     "entry": "本实验台·实验区"},
    {"name": "0.1 process 作业", "domain": "协议", "status": "EXPERIMENTAL",
     "what": "preset 处理（会写出音频文件）",
     "entry": "CLI: moodify protocol process"},
    {"name": "Mix Graph finishing", "domain": "制作", "status": "EXPERIMENTAL",
     "what": "混音图派生 / 渲染验证 / 交付编码",
     "entry": "CLI: moodify finishing new|render|verify|export"},
    {"name": "Era Diagnostic", "domain": "重建", "status": "EXPERIMENTAL",
     "what": "年代诊断（P04 只可自动消费 HIGH/MEDIUM）",
     "entry": "代码层: moodify.era_diagnostic"},
    {"name": "Identity Guard", "domain": "重建", "status": "EXPERIMENTAL",
     "what": "六维 veto guard + ranking",
     "entry": "代码层: moodify.identity_guard"},
    {"name": "MAMSE-001..012", "domain": "研究", "status": "EXPERIMENTAL_ACCEPTED",
     "what": "多尺度听觉表示（R 轴/CQT/小波/相位/倒谱/调制/SVD/NMF/RPCA/张量/协方差/图）",
     "entry": "证据包: artifacts/mamse_001..012"},
    {"name": "敏感性验证", "domain": "校准", "status": "EXPERIMENTAL",
     "what": "生产判定路径翻转点验证（16/16 一致）",
     "entry": "证据包: artifacts/msp02_calibration_001/"},
    {"name": "环境探测 doctor", "domain": "环境", "status": "READY",
     "what": "python/core/依赖/ffmpeg 就绪探测",
     "entry": "CLI: moodify doctor"},
]

_CALIBRATION_NOTE = "阈值现状 0/16 calibrated（全部 DEFAULT_UNCALIBRATED）；实验台只观测，不写入参数。"


# ——— 实验区：compare 视图模型（纯函数，可测） ———


def build_compare_view_model(report: dict[str, Any]) -> dict[str, Any]:
    """Map a 0.2 compare report.json onto widget-ready data (pure)."""
    comparison = report.get("comparison") or {}
    reference = comparison.get("reference") or {}
    normalization = comparison.get("loudness_normalization") or {}
    rows = [
        {
            "id": row.get("id", "?"),
            "before": _fmt(row.get("before")),
            "after": _fmt(row.get("after")),
            "delta": _fmt(row.get("absolute_delta")),
            "unit": row.get("unit", ""),
            "direction": row.get("direction", ""),
        }
        for row in comparison.get("metric_deltas") or []
    ]
    checks_raw = comparison.get("pair_checks") or {}
    pair_checks = [
        {"check": key, "passed": value, "detail": ""}
        if isinstance(value, bool)
        else {"check": key, "passed": None, "detail": str(value)}
        for key, value in (checks_raw.items() if isinstance(checks_raw, dict) else [])
    ]
    return {
        "candidate": (report.get("source") or {}).get("name", "?"),
        "reference_name": reference.get("name", "?"),
        "reference_sha256": str(reference.get("sha256", "?"))[:_HASH_DISPLAY],
        "normalization": f"{normalization.get('gain_db')} dB"
                         if normalization.get("gain_db") is not None else "无效/未对齐",
        "normalization_valid": bool(normalization.get("valid")),
        "rows": rows,
        "pair_checks": pair_checks,
        "delta_spectrograms": list(comparison.get("delta_spectrograms") or []),
        "visibility_note": comparison.get("visibility_note", ""),
    }


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4g}"
    return "—" if value is None else str(value)


def run_compare(reference: Path, source: Path, cases_root: Path) -> dict[str, Any]:
    """Run the 0.2 compare job (same validate/execute path; no new DSP)."""
    from moodify.sound_protocol import PROTOCOL_V02, execute_job, validate_job

    job = validate_job(
        {"protocol": PROTOCOL_V02, "type": "compare", "source": str(source),
         "reference": str(reference), "output_dir": str(cases_root)},
        Path.home(),
    )
    return execute_job(job)


# ——— Tk：实验台框架（只在窗口进程实例化） ———


def build_lab_frame(parent, cases_root: Path, on_back, on_open_case=None):
    """Build the lab inside ``parent``; ``on_back`` returns to the archive."""
    from tkinter import ttk

    frame = ttk.Frame(parent)
    header = ttk.Frame(frame, padding=(12, 10))
    header.pack(fill="x")
    ttk.Label(header, text="实验台", font=("TkDefaultFont", 14, "bold")).pack(side="left")
    ttk.Label(header, foreground="#555",
              text="观测 · 目录 · 实验 —— 只读取事实，只做对比观测").pack(side="left", padx=12)
    ttk.Button(header, text="← 档案", command=on_back).pack(side="right")

    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True, padx=12, pady=8)
    _build_observation_tab(notebook, cases_root)
    _build_catalog_tab(notebook)
    _build_experiment_tab(notebook, cases_root)
    return frame


def _tree(tab: Any, columns: tuple[tuple[str, str, int], ...]) -> Any:
    from tkinter import ttk

    tree = ttk.Treeview(tab, columns=[c[0] for c in columns], show="headings")
    for key, text, width in columns:
        tree.heading(key, text=text)
        tree.column(key, width=width, anchor="w")
    scroll = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return tree


def _build_observation_tab(notebook, cases_root: Path) -> None:
    import tkinter as tk
    from tkinter import ttk

    tab = ttk.Frame(notebook)
    notebook.add(tab, text=_CASES_TAB[0])

    picker = ttk.Frame(tab)
    picker.pack(fill="x", padx=12, pady=(10, 4))
    ttk.Label(picker, text="案例：").pack(side="left")
    case_var = tk.StringVar()
    combo = ttk.Combobox(picker, textvariable=case_var, state="readonly", width=48)
    combo.pack(side="left", padx=6)
    status_label = ttk.Label(picker, foreground="#555", text="")
    status_label.pack(side="left", padx=8)

    detail = ttk.Frame(tab)
    detail.pack(fill="both", expand=True)
    meta = ttk.Frame(detail)
    meta.pack(fill="x", padx=12, pady=4)
    meta_labels: dict[str, ttk.Label] = {}
    for key, title in (("job", "作业"), ("input", "输入"), ("profile", "扫描档"),
                       ("stage", "阶段"), ("representation", "表示层")):
        row = ttk.Frame(meta)
        row.pack(fill="x")
        ttk.Label(row, text=f"{title}：", foreground="#555", width=8).pack(side="left")
        meta_labels[key] = ttk.Label(row, text="—")
        meta_labels[key].pack(side="left")

    evidence_tree = _tree(_subframe(detail, "证据链（evidence.json）"),
                          (("type", "产物", 130), ("path", "逻辑路径", 220),
                           ("hash", "内容哈希", 150), ("time", "创建", 150),
                           ("size", "字节", 80)))
    rules_tree = _tree(_subframe(detail, "判定规则现状（judgment_rules.json）"),
                       (("id", "规则", 280), ("text", "阈值定义", 460)))

    def _show_case() -> None:
        index = combo.current()
        if index < 0:
            return
        rows = scan_cases(cases_root)
        if index >= len(rows):
            return
        prov = load_case_provenance(Path(rows[index]["report_path"]).parent)
        meta_labels["job"].configure(
            text=f"{prov['job_type']} · {prov['protocol']}")
        meta_labels["input"].configure(
            text=f"{prov['source_name']} · sha256 {prov['input_sha256']}…")
        meta_labels["profile"].configure(text=str(prov["profile_id"]))
        meta_labels["stage"].configure(text=str(prov["stage"]))
        rep = prov["representation"]
        meta_labels["representation"].configure(
            text=f"timeline_windows={rep['timeline_windows']} · "
                 f"stft={rep['stft_arrays']}")
        evidence_tree.delete(*evidence_tree.get_children())
        for rec in prov["evidence"]:
            evidence_tree.insert("", "end", values=[
                rec["artifact_type"], rec["logical_path"], rec["hash"],
                rec["created_at"], "—" if rec["size_bytes"] is None else rec["size_bytes"]])
        rules_tree.delete(*rules_tree.get_children())
        for rule in prov["rules"]:
            rules_tree.insert("", "end", values=[rule["id"], rule["text"]])
        status_label.configure(
            text=f"{len(prov['evidence'])} 条证据 · {len(prov['rules'])} 条规则")

    ttk.Button(picker, text="载入", command=_show_case).pack(side="left")
    _reload_cases(cases_root, combo)
    if combo.current() < 0:
        status_label.configure(text="档案为空——先在档案页分析一首歌")
    combo.bind("<<ComboboxSelected>>", lambda _e: _show_case())


def _subframe(parent, title: str):
    from tkinter import ttk

    box = ttk.LabelFrame(parent, text=title)
    box.pack(fill="both", expand=True, padx=12, pady=4)
    return box


def _build_catalog_tab(notebook) -> None:
    from tkinter import ttk

    tab = ttk.Frame(notebook)
    notebook.add(tab, text=_CASES_TAB[1])
    tree = _tree(tab, (("name", "能力", 200), ("domain", "域", 90),
                       ("status", "状态", 180), ("what", "说明", 380),
                       ("entry", "入口", 280)))
    for cap in CAPABILITY_CATALOG:
        tree.insert("", "end", values=[cap["name"], cap["domain"],
                                       cap["status"], cap["what"], cap["entry"]])
    ttk.Label(tab, foreground="#555", text=_CALIBRATION_NOTE
              ).pack(anchor="w", padx=12, pady=6)


def _build_experiment_tab(notebook, cases_root: Path) -> None:
    import tkinter as tk
    from tkinter import ttk

    tab = ttk.Frame(notebook)
    notebook.add(tab, text=_CASES_TAB[2])
    state: dict[str, Any] = {"queue": queue.Queue(), "running": False}

    picker = ttk.Frame(tab)
    picker.pack(fill="x", padx=12, pady=(10, 4))
    ref_var = tk.StringVar()
    src_var = tk.StringVar()
    for label, var in (("参考 A：", ref_var), ("候选 B：", src_var)):
        ttk.Label(picker, text=label).pack(side="left")
        ttk.Label(picker, textvariable=var, foreground="#333", width=42).pack(side="left")
        var.set("（未选择）")

    def _pick(var: tk.StringVar) -> None:
        from tkinter import filedialog

        path = filedialog.askopenfilename(
            title="选择音频文件",
            filetypes=[("音频", "*.flac *.wav *.mp3 *.m4a *.aac *.ogg"),
                       ("所有文件", "*.*")])
        if path:
            var.set(path)

    pick_row = ttk.Frame(tab)
    pick_row.pack(anchor="w", padx=12)
    ttk.Button(pick_row, text="选参考 A…", command=lambda: _pick(ref_var)).pack(side="left")
    ttk.Button(pick_row, text="选候选 B…", command=lambda: _pick(src_var)).pack(side="left", padx=8)

    status_var = tk.StringVar(value="选择两个文件后运行对比（delta 只描述，不评级）")
    ttk.Label(tab, textvariable=status_var, foreground="#555").pack(
        anchor="w", padx=12, pady=4)

    result_box = ttk.Frame(tab)
    result_box.pack(fill="both", expand=True)

    def _poll() -> None:
        try:
            while True:
                kind, payload = state["queue"].get_nowait()
                state["running"] = False
                if kind == "done":
                    status_var.set("对比完成")
                    _render_compare_result(result_box, Path(payload["report_dir"]))
                else:
                    status_var.set("对比失败")
                    ttk.Label(result_box, foreground="#a33",
                              text=str(payload)).pack(anchor="w", padx=12)
        except queue.Empty:
            pass
        if tab.winfo_exists():
            tab.after(150, _poll)

    def _run() -> None:
        from tkinter import messagebox

        if state["running"]:
            return
        if ref_var.get().startswith("（") or src_var.get().startswith("（"):
            messagebox.showinfo("先选文件", "请先选择参考 A 与候选 B 两个音频文件", parent=tab)
            return
        for child in result_box.winfo_children():
            child.destroy()
        state["running"] = True
        status_var.set("对比中：两次分析 + 响度对齐 + delta …（约 1–3 分钟）")
        reference, source = Path(ref_var.get()), Path(src_var.get())
        threading.Thread(
            target=_compare_worker,
            args=(reference, source, cases_root, state["queue"]),
            daemon=True).start()

    ttk.Button(pick_row, text="运行对比", command=_run).pack(side="left", padx=8)
    _poll()


def _compare_worker(reference: Path, source: Path, cases_root: Path,
                    out_queue: queue.Queue) -> None:
    try:
        result = run_compare(reference, source, cases_root)
        out_queue.put(("done", {"report_dir": result["compare_root"]}))
    except Exception as exc:  # surface in the UI, never crash Tk
        out_queue.put(("error", f"{type(exc).__name__}: {exc}"))


def _render_compare_result(box, compare_root: Path) -> None:
    import tkinter as tk
    from tkinter import ttk

    report = _read_json(compare_root / "report.json")
    model = build_compare_view_model(report)
    head = (f"候选 {model['candidate']}  ←  参考 {model['reference_name']}  ·  "
            f"响度对齐 {model['normalization']}")
    ttk.Label(box, text=head, font=("TkDefaultFont", 11, "bold")).pack(
        anchor="w", padx=12, pady=(8, 2))
    checks = " · ".join(
        f"{c['check']}={'✓' if c['passed'] is True else ('✗' if c['passed'] is False else '?')}"
        for c in model["pair_checks"]) or "—"
    ttk.Label(box, foreground="#555", text=f"配对校验：{checks}").pack(
        anchor="w", padx=12)

    columns = (("id", "指标", 220), ("before", "A 值", 110), ("after", "B 值", 110),
               ("delta", "Δ", 110), ("unit", "单位", 90), ("direction", "方向", 90))
    tree = ttk.Treeview(box, columns=[c[0] for c in columns], show="headings", height=9)
    for key, text, width in columns:
        tree.heading(key, text=text)
        tree.column(key, width=width, anchor="w")
    scroll = ttk.Scrollbar(box, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(fill="both", expand=True, padx=12, pady=6)
    scroll.pack(side="right", fill="y")
    for row in model["rows"]:
        tree.insert("", "end", values=[row[c[0]] for c in columns])

    for png_name in ("delta_spectrum_log.png", "delta_spectrum_linear.png"):
        png_path = compare_root / png_name
        if not png_path.is_file():
            continue
        try:
            photo = tk.PhotoImage(file=str(png_path))
            factor = max(1, photo.width() // 820, photo.height() // 420)
            if factor > 1:
                photo = photo.subsample(factor)
            ttk.Label(box, image=photo).pack(padx=12, pady=4)
            box.image = photo
            break
        except tk.TclError:
            continue
    ttk.Label(box, foreground="#555",
              text=model["visibility_note"] or "delta 只描述不评级；无新判断。").pack(
        anchor="w", padx=12, pady=(0, 8))


# ——— 档案桥（复用 app 的扫描；避免环导入放在运行时） ———


def scan_cases(cases_root: Path) -> list[dict[str, Any]]:
    from moodify.ui.app import scan_case_archive

    return scan_case_archive(cases_root)


def _reload_cases(cases_root: Path, combo) -> None:
    rows = scan_cases(cases_root)
    combo["values"] = [f"{row['source_name']} · {row['generated_at']}" for row in rows]
    if rows:
        combo.current(0)
