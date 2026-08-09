"""Auditory evidence panel (DSK-MFY-PANEL-001).

Serves scan cases (before/after spectrograms, delta spectrum, metrics)
to a browser — the iPad second screen during listening/verification runs.

Pure stdlib: python tools/auditory_panel.py [--root DIR] [--port N]
"""

from __future__ import annotations

import argparse
import json
import socket
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

HTML = """<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Moodify 听觉面板</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: -apple-system, "Segoe UI", sans-serif;
         background: #0d1117; color: #e6edf3; }
  header { display: flex; align-items: center; gap: 12px; padding: 12px 16px;
           background: #161b22; border-bottom: 1px solid #30363d; position: sticky; top: 0; z-index: 5; }
  header h1 { font-size: 18px; margin: 0; flex: 1; }
  #cases { font-size: 16px; padding: 6px 10px; background: #0d1117; color: #e6edf3;
           border: 1px solid #30363d; border-radius: 6px; max-width: 320px; }
  #status { font-size: 13px; color: #8b949e; }
  #refresh { appearance: none; border: 1px solid #30363d; border-radius: 6px;
             background: #21262d; color: #e6edf3; padding: 7px 11px; cursor: pointer; }
  #refresh:hover { border-color: #58a6ff; }
  #refresh:disabled { cursor: wait; opacity: .65; }
  .ok { color: #3fb950; } .warn { color: #d29922; }
  section { padding: 12px 16px; }
  h2 { font-size: 15px; color: #8b949e; margin: 6px 0 10px; font-weight: 600; }
  .imgs { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .imgs.one { grid-template-columns: 1fr; }
  figure { margin: 0; }
  figure img { display: block; width: 100%; border: 1px solid #30363d; border-radius: 8px;
               background: #000; content-visibility: auto; }
  figcaption { font-size: 13px; color: #8b949e; text-align: center; margin-top: 4px; }
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  th, td { padding: 6px 10px; border-bottom: 1px solid #21262d; text-align: right; }
  th:first-child, td:first-child { text-align: left; }
  th { color: #8b949e; font-weight: 600; position: sticky; top: 57px; background: #161b22; }
  .up { color: #3fb950; } .down { color: #f85149; }
  #empty { padding: 60px 20px; text-align: center; color: #8b949e; font-size: 15px; }
  canvas { width: 100%; height: 160px; background: #000; border: 1px solid #30363d; border-radius: 8px; }
  @media (max-width: 1180px) {
    header { flex-wrap: wrap; padding: 9px 12px; gap: 8px; }
    header h1 { flex-basis: 100%; }
    #cases { flex: 1; max-width: none; }
    section { padding: 9px 12px; }
    .imgs { gap: 7px; }
    figcaption { font-size: 12px; }
  }
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { scroll-behavior: auto !important; animation: none !important; transition: none !important; }
  }
</style>
</head>
<body>
<header>
  <h1>Moodify 听觉面板</h1>
  <select id="cases"></select>
  <button id="refresh" type="button">刷新</button>
  <span id="status">连接中…</span>
</header>
<div id="empty" hidden>未找到 scan case。先运行 auditory golden scan 生成 outputs/auditory_golden/cases/。</div>
<section id="content" hidden>
  <section>
    <h2>频谱对比 (linear)</h2>
    <div class="imgs" id="spec-linear"></div>
    <h2>频谱对比 (log)</h2>
    <div class="imgs" id="spec-log"></div>
  </section>
  <section>
    <h2>时间轴 (RMS dBFS · 0.5s 窗)</h2>
    <canvas id="timeline"></canvas>
  </section>
  <section>
    <h2>Delta 频谱</h2>
    <div class="imgs" id="delta"></div>
  </section>
  <section>
    <h2>指标对比</h2>
    <table id="metrics"></table>
  </section>
</section>
<script>
const $ = (s) => document.querySelector(s);
let cases = [], selected = null, timer = null, selectedModified = null, refreshing = false;

function fmt(v) {
  if (v === null || v === undefined || v === "") return "—";
  if (typeof v === "number") return Number(v).toLocaleString("zh-CN", {maximumFractionDigits: 4});
  return String(v);
}

function specBlock(label, url, revision) {
  const suffix = revision ? `?v=${encodeURIComponent(revision)}` : "";
  return `<figure><img src="${url}${suffix}" loading="lazy" decoding="async"><figcaption>${label}</figcaption></figure>`;
}

function metricRows(before, delta) {
  const keys = before ? Object.keys(before) : [];
  let rows = "";
  for (const k of keys) {
    const b = before[k], d = delta ? delta[k] : null;
    const unit = (b && b.unit) || (d && d.unit) || "";
    const bv = fmt(b && b.value);
    const av = d && d.after !== undefined && d.after !== null ? fmt(d.after) : "—";
    const dv = d && d.absolute_delta !== undefined && d.absolute_delta !== null ? fmt(d.absolute_delta) : "—";
    let cls = "", arrow = "";
    if (d && d.direction === "INCREASE") { cls = "up"; arrow = " ▲"; }
    if (d && d.direction === "DECREASE") { cls = "down"; arrow = " ▼"; }
    rows += `<tr><td>${k}</td><td>${bv} ${unit}</td><td>${av} ${unit}</td>` +
            `<td class="${cls}">${dv}${arrow}</td></tr>`;
  }
  return `<tr><th>指标</th><th>Before</th><th>After</th><th>Δ</th></tr>` + rows;
}

function drawTimeline(before, after) {
  const cv = $("#timeline");
  const dpr = window.devicePixelRatio || 1;
  const w = cv.clientWidth, h = cv.clientHeight;
  cv.width = w * dpr; cv.height = h * dpr;
  const ctx = cv.getContext("2d");
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, w, h);
  const series = [];
  for (const [d, color] of [[before, "#3fb950"], [after, "#f0883e"]]) {
    if (!d) continue;
    const pts = d.map((p) => p.rms_dbfs);
    if (pts.length) series.push({pts, color});
  }
  if (!series.length) return;
  const all = series.flatMap((s) => s.pts);
  const min = Math.min(...all), max = Math.max(...all);
  const pad = 6, range = Math.max(max - min, 1e-9);
  for (const s of series) {
    ctx.strokeStyle = s.color; ctx.lineWidth = 2; ctx.beginPath();
    s.pts.forEach((v, i) => {
      const x = pad + (i / Math.max(s.pts.length - 1, 1)) * (w - pad * 2);
      const y = pad + (1 - (v - min) / range) * (h - pad * 2);
      i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
    });
    ctx.stroke();
  }
  ctx.fillStyle = "#8b949e"; ctx.font = "11px sans-serif";
  ctx.fillText(`${max.toFixed(1)} dBFS`, 4, 12);
  ctx.fillText(`${min.toFixed(1)} dBFS`, 4, h - 4);
}

async function refresh() {
  const id = selected;
  if (!id || refreshing) return;
  refreshing = true;
  $("#refresh").disabled = true;
  try {
    const r = await fetch(`/api/case/${encodeURIComponent(id)}`, {cache: "no-store"});
    const d = await r.json();
    $("#status").textContent = `更新 ${new Date().toLocaleTimeString("zh-CN")}`;
    $("#status").className = "ok";
    const lin = $("#spec-linear"), log = $("#spec-log"), delta = $("#delta");
    const hasAfter = !!d.after, hasBefore = !!d.before;
    lin.className = "imgs" + (hasAfter ? "" : " one");
    log.className = lin.className; delta.className = "imgs one";
    const revision = d.modified || selectedModified || "stable";
    lin.innerHTML = (hasBefore ? specBlock("Before", d.files.before_linear, revision) : "") +
                    (hasAfter ? specBlock("After", d.files.after_linear, revision) : "");
    log.innerHTML = (hasBefore ? specBlock("Before", d.files.before_log, revision) : "") +
                    (hasAfter ? specBlock("After", d.files.after_log, revision) : "");
    delta.innerHTML = (d.files.delta_linear ? specBlock("Delta (linear)", d.files.delta_linear, revision) : "") +
                      (d.files.delta_log ? specBlock("Delta (log)", d.files.delta_log, revision) : "");
    $("#metrics").innerHTML = metricRows(d.before_metrics, d.delta_metrics);
    drawTimeline(d.before_timeline, d.after_timeline);
  } catch (e) {
    $("#status").textContent = "连接断开，重试中…"; $("#status").className = "warn";
  } finally {
    refreshing = false;
    $("#refresh").disabled = false;
  }
}

async function loadCases() {
  try {
    const r = await fetch("/api/cases?t=" + Date.now());
    const d = await r.json();
    cases = d.cases || [];
    const sel = $("#cases");
    const prev = selected;
    const previousOptions = Array.from(sel.options).map((o) => `${o.value}:${o.textContent}`).join("|");
    const nextOptions = cases.map((c) => `${c.id}:${c.id + (c.comparison ? "" : " (未对比)")}`).join("|");
    if (previousOptions !== nextOptions) {
      sel.innerHTML = "";
      for (const c of cases) {
        const opt = document.createElement("option");
        opt.value = c.id; opt.textContent = c.id + (c.comparison ? "" : " (未对比)");
        sel.appendChild(opt);
      }
    }
    if (cases.length) {
      const pick = prev && cases.some((c) => c.id === prev) ? prev : cases[0].id;
      const current = cases.find((c) => c.id === pick);
      const changed = pick !== selected || !current || current.modified !== selectedModified;
      sel.value = pick; selected = pick;
      $("#empty").hidden = true; $("#content").hidden = false;
      if (changed) {
        selectedModified = current ? current.modified : null;
        refresh();
      }
    } else {
      $("#empty").hidden = false; $("#content").hidden = true;
    }
  } catch (e) {
    $("#status").textContent = "连接断开，重试中…"; $("#status").className = "warn";
  }
}

$("#cases").addEventListener("change", (e) => {
  selected = e.target.value;
  const current = cases.find((c) => c.id === selected);
  selectedModified = current ? current.modified : null;
  refresh();
});
$("#refresh").addEventListener("click", refresh);
loadCases();
timer = setInterval(() => { if (document.visibilityState === "visible") loadCases(); }, 10000);
</script>
</body>
</html>
"""


def lan_ips() -> list[str]:
    ips = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ips.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.add(info[4][0])
    except OSError:
        pass
    return sorted(ips)


def resolve_case(root: Path, case_id: str) -> Path | None:
    if not case_id or case_id in {".", ".."} or "/" in case_id or "\\" in case_id:
        return None
    cand = root / case_id
    return cand if cand.is_dir() else None


def case_summary(root: Path, case_dir: Path) -> dict:
    id_ = case_dir.name
    before = case_dir / "01_before_scan"
    after = case_dir / "04_after_scan"
    cmp = case_dir / "05_comparison"
    mtime = max(
        (p.stat().st_mtime for p in [before, after, cmp] if p.is_dir()),
        default=case_dir.stat().st_mtime,
    )
    return {
        "id": id_,
        "before": before.is_dir(),
        "after": after.is_dir(),
        "comparison": cmp.is_dir(),
        "modified": mtime,
    }


def read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


class Handler(BaseHTTPRequestHandler):
    server_version = "AuditoryPanel/1.0"

    @property
    def root(self) -> Path:
        return self.server.root  # type: ignore[attr-defined]

    def _json(self, obj: dict) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, path: Path) -> None:
        try:
            data = path.read_bytes()
        except OSError:
            self.send_error(404, "not found")
            return
        ext = path.suffix.lower()
        ctype = {".png": "image/png", ".json": "application/json", ".wav": "audio/wav"}.get(ext, "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        parts = [unquote(p) for p in parsed.path.split("/") if p]

        if parts and parts[0] == "api":
            if len(parts) == 2 and parts[1] == "cases":
                cases = sorted(
                    (case_summary(self.root, d) for d in self.root.iterdir() if d.is_dir()),
                    key=lambda c: c["modified"], reverse=True,
                )
                self._json({"cases": cases})
                return
            if len(parts) == 3 and parts[1] == "case":
                case_dir = resolve_case(self.root, parts[2])
                if case_dir is None:
                    self.send_error(404, "unknown case")
                    return
                before = case_dir / "01_before_scan"
                after = case_dir / "04_after_scan"
                cmp = case_dir / "05_comparison"
                delta = read_json(cmp / "metrics_delta.json") if cmp.is_dir() else None
                self._json({
                    "id": parts[2],
                    "modified": case_summary(self.root, case_dir)["modified"],
                    "before": before.is_dir(),
                    "after": after.is_dir(),
                    "before_metrics": read_json(before / "metrics.json") if before.is_dir() else None,
                    "after_metrics": read_json(after / "metrics.json") if after.is_dir() else None,
                    "delta_metrics": (delta or {}).get("metric_deltas"),
                    "before_timeline": [json.loads(line) for line in (before / "timeline_metrics.jsonl").read_text(encoding="utf-8").splitlines()] if (before / "timeline_metrics.jsonl").is_file() else None,
                    "after_timeline": [json.loads(line) for line in (after / "timeline_metrics.jsonl").read_text(encoding="utf-8").splitlines()] if (after / "timeline_metrics.jsonl").is_file() else None,
                    "files": {
                        "before_linear": f"/files/{parts[2]}/01_before_scan/spectrum_linear.png",
                        "before_log": f"/files/{parts[2]}/01_before_scan/spectrum_log.png",
                        "after_linear": f"/files/{parts[2]}/04_after_scan/spectrum_linear.png",
                        "after_log": f"/files/{parts[2]}/04_after_scan/spectrum_log.png",
                        "delta_linear": f"/files/{parts[2]}/05_comparison/delta_spectrum_linear.png" if (cmp / "delta_spectrum_linear.png").is_file() else None,
                        "delta_log": f"/files/{parts[2]}/05_comparison/delta_spectrum_log.png" if (cmp / "delta_spectrum_log.png").is_file() else None,
                    },
                })
                return

        if parts and parts[0] == "files" and len(parts) >= 3:
            case_dir = resolve_case(self.root, parts[1])
            if case_dir is None:
                self.send_error(404, "unknown case")
                return
            rel = Path(*parts[2:])
            if rel.parts and not any(p in {".", ".."} for p in rel.parts):
                target = (case_dir / rel).resolve()
                if case_dir.resolve() in target.parents and target.is_file():
                    self._serve_file(target)
                    return
            self.send_error(404, "not found")
            return

        if parsed.path == "/" or parsed.path == "/index.html":
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_error(404, "not found")

    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {fmt % args}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Moodify auditory evidence panel")
    ap.add_argument("--root", default="outputs/auditory_golden/cases", help="scan cases root dir")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: root dir not found: {root}")
        return 1

    server = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    server.root = root  # type: ignore[attr-defined]
    print(f"panel root : {root}")
    print(f"local      : http://127.0.0.1:{args.port}")
    for ip in lan_ips():
        print(f"LAN (iPad) : http://{ip}:{args.port}")
    print("Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
