"""Moodify desktop app — the company's one-shell desktop software.

Product definition (human, 2026-10-02): ONE shell, white, carrying the
company logo. The flow is fixed: pick a song → detect → data & charts →
repair/mixing plan. Pick a song with the file dialog, analyze inside the
app (worker thread, UI stays responsive), and every case lands in a
permanent archive that reopens instantly from the history list — no
re-analysis. The report view (数据 / 图表 / 后处理方案) is the same shell
navigated in place; nothing here leads out of the ecosystem.

Run standalone:

    python -m moodify.ui.app [cases_root]

The archive root defaults to ``~/.moodify/cases`` (app-owned, stable
across working directories) and is shown in the UI.
"""

from __future__ import annotations

import json
import queue
import sys
import threading
from pathlib import Path
from typing import Any

from moodify.ui.report_window import build_report_frame
from moodify.ui.theme import apply_white_theme, load_logo, set_app_icon

DEFAULT_CASES_ROOT = Path.home() / ".moodify" / "cases"

_AUDIO_FILETYPES = [
    ("音频", "*.flac *.wav *.mp3 *.m4a *.aac *.ogg *.aiff *.aif"),
    ("所有文件", "*.*"),
]


def scan_case_archive(cases_root: Path) -> list[dict[str, Any]]:
    """List analyzable case bundles newest-first (pure, tolerant).

    Partial or corrupt bundles are skipped, never fatal: the archive list
    must survive an interrupted analysis.
    """
    rows: list[dict[str, Any]] = []
    if not cases_root.is_dir():
        return rows
    for report_path in sorted(cases_root.glob("case_*/report.json")):
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        source = report.get("source") or {}
        technical = report.get("technical_state") or {}
        case = report.get("case") or {}
        rows.append({
            "case_id": case.get("case_id", report_path.parent.name),
            "report_path": str(report_path),
            "source_name": source.get("name", "?"),
            "generated_at": report.get("generated_at", "?"),
            "overall": technical.get("overall", "?"),
            "workflow_decision": technical.get("workflow_decision", "?"),
        })
    # newest first; rows without a timestamp sink to the end
    rows.sort(key=lambda row: (row["generated_at"] != "?", row["generated_at"]),
              reverse=True)
    return rows


def run_analysis(audio_path: Path, cases_root: Path) -> dict[str, Any]:
    """Analyze one file through the 0.2 protocol path (no DSP here).

    Runs on a worker thread; the Tk main thread only observes a queue.
    Raises ProtocolError (or anything unexpected, caught by the worker)
    on failure.
    """
    from moodify.sound_protocol import PROTOCOL_V02, execute_job, validate_job

    job = validate_job(
        {"protocol": PROTOCOL_V02, "type": "analyze",
         "source": str(audio_path), "output_dir": str(cases_root)},
        Path.home(),
    )
    return execute_job(job)


class MoodifyApp:
    """Hub window: open file / analysis status / case archive list."""

    def __init__(self, root, cases_root: Path):
        import tkinter as tk
        from tkinter import ttk

        self.root = root
        self.cases_root = Path(cases_root)
        self.queue: queue.Queue[tuple[str, Any]] = queue.Queue()
        self._analyzing = False
        self._rows: dict[str, dict[str, Any]] = {}

        self.root.title("Moodify")
        self.root.minsize(880, 480)
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            # "clam" unavailable in this Tk build: keep the default theme, the
            # white theme below is applied regardless.
            ...
        apply_white_theme(self.root, style)
        set_app_icon(self.root)

        self._show_hub()
        self._poll()

    # — hub —
    def _show_hub(self) -> None:
        import tkinter as tk
        from tkinter import ttk

        self._clear()
        top = ttk.Frame(self.root, padding=(14, 12))
        top.pack(fill="x")
        logo = load_logo(280)
        if logo is not None:
            ttk.Label(top, image=logo).pack(side="left")
            top.image = logo  # keep a reference (photo is GC-able otherwise)
        self.open_button = ttk.Button(top, text="打开音频文件…", command=self._open_audio)
        self.open_button.pack(side="right")
        self.status_var = tk.StringVar(value="空闲 — 选择一首歌开始检测")
        ttk.Label(top, textvariable=self.status_var, style="Muted.TLabel").pack(
            side="right", padx=12)

        ttk.Label(self.root, text=f"档案目录：{self.cases_root}",
                  style="Muted.TLabel").pack(anchor="w", padx=14)

        list_frame = ttk.Frame(self.root, padding=(12, 4))
        list_frame.pack(fill="both", expand=True)
        hint_line = ttk.Frame(list_frame)
        hint_line.pack(fill="x")
        ttk.Label(hint_line, text="历史档案（双击打开，无需重新分析）").pack(side="left")
        ttk.Button(hint_line, text="刷新", command=self._refresh).pack(side="right")

        cols = ("source", "time", "overall", "decision")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings")
        for key, text, width in (("source", "源文件", 300), ("time", "分析时间", 180),
                                 ("overall", "状态", 90), ("decision", "工作流判定", 200)):
            self.tree.heading(key, text=text)
            self.tree.column(key, width=width, anchor="w")
        self.tree.bind("<Double-1>", self._on_row_open)
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self._refresh()

    def _clear(self) -> None:
        for child in self.root.winfo_children():
            child.destroy()

    def _refresh(self) -> None:
        rows = scan_case_archive(self.cases_root)
        self._rows = {row["case_id"]: row for row in rows}
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", iid=row["case_id"],
                             values=[row["source_name"], row["generated_at"],
                                     row["overall"], row["workflow_decision"]])

    # — navigation —
    def _on_row_open(self, _event) -> None:
        if self._analyzing:
            return
        selection = self.tree.selection()
        if selection and selection[0] in self._rows:
            self._open_report(Path(self._rows[selection[0]]["report_path"]))

    def _open_report(self, report_path: Path) -> None:
        from tkinter import messagebox

        self._clear()
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            messagebox.showerror("无法打开档案", str(exc), parent=self.root)
            self._show_hub()
            return
        build_report_frame(self.root, report, report_path, on_back=self._show_hub)

    # — analysis —
    def _open_audio(self) -> None:
        from tkinter import filedialog

        path = filedialog.askopenfilename(title="选择音频文件", filetypes=_AUDIO_FILETYPES)
        if path:
            self._start_analysis(Path(path))

    def _start_analysis(self, audio_path: Path) -> None:
        if self._analyzing:
            return
        self._analyzing = True
        self.open_button.configure(state="disabled")
        self.status_var.set(f"分析中：{audio_path.name} …（完整测量链路，约几十秒到几分钟）")
        threading.Thread(target=self._worker, args=(audio_path,), daemon=True).start()

    def _worker(self, audio_path: Path) -> None:
        try:
            self.queue.put(("done", run_analysis(audio_path, self.cases_root)))
        except Exception as exc:  # worker failures surface in the UI, never crash Tk
            self.queue.put(("error", f"{type(exc).__name__}: {exc}"))

    def _poll(self) -> None:
        try:
            while True:
                kind, payload = self.queue.get_nowait()
                if kind == "done":
                    self._analyzing = False
                    self._refresh()
                    self._open_report(Path(payload["reports"]["json"]))
                elif kind == "error":
                    from tkinter import messagebox

                    self._analyzing = False
                    self.open_button.configure(state="normal")
                    self.status_var.set("分析失败")
                    messagebox.showerror("分析失败", str(payload), parent=self.root)
        except queue.Empty:
            # Expected control flow: the worker queue is simply empty this tick.
            ...
        self.root.after(150, self._poll)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    cases_root = Path(args[0]).expanduser() if args else DEFAULT_CASES_ROOT
    try:
        import tkinter as tk
    except ImportError:
        print("tkinter is not available in this Python build", file=sys.stderr)
        return 3
    root = tk.Tk()
    MoodifyApp(root, cases_root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
