"""Deterministic renderers for the MSP/0.2 analysis report (report.md / report.html).

Pure functions from the report dict to text. The HTML file is the "display
screen" for analysis results: self-contained (inline CSS, base64-embedded
spectrogram PNGs, no CDN, no JavaScript) so it can be moved or attached
anywhere and still render offline.
"""

from __future__ import annotations

import base64
import html
from pathlib import Path

SEVERITY_CLASS = {
    "BLOCKING": "sev-blocking",
    "WARNING": "sev-warning",
    "INFO": "sev-info",
    "OK": "sev-ok",
    "RISK": "sev-warning",
    "PARTIAL": "sev-unknown",
    "EXECUTED": "sev-ok",
    "NOT_RUN": "sev-unknown",
    "NOT_PROMISED": "sev-promised",
}

GROUP_ORDER = ["loudness", "integrity", "spectral", "bands", "stereo", "format", "other"]
GROUP_LABELS = {
    "loudness": "响度与动态",
    "integrity": "信号完整性",
    "spectral": "频谱",
    "bands": "频段能量占比",
    "stereo": "立体声",
    "format": "格式",
    "other": "其他",
}

LAYER_LABELS = {
    "layer1_measurement": "L1 测量（技术状况）",
    "layer2_comparison": "L2 受控比较（感知差异）",
    "layer3_musical_judgment": "L3 音乐判断（表达/比例/意图）",
    "layer4_production_judgment": "L4 制作判断（可编辑/可追溯）",
    "layer5_cultural_judgment": "L5 文化判断（人类作者身份）",
}


def _fmt(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def _grouped(measurements: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in measurements:
        grouped.setdefault(row.get("group", "other"), []).append(row)
    return grouped


def render_report_markdown(report: dict) -> str:
    """Human-readable markdown twin of report.json."""
    source = report["source"]
    state = report["technical_state"]
    lines: list[str] = []
    lines.append(f"# Moodify 分析报告 — {source['name']}")
    lines.append("")
    lines.append(f"- 报告契约：`{report['report_schema_version']}`（协议 `{report['protocol']}`）")
    lines.append(f"- case：`{report['case']['case_id']}`")
    lines.append(f"- 生成时间：{report['generated_at']}")
    lines.append(f"- 源音频：`{source['name']}` / `{source['sha256']}`")
    lines.append(f"- 技术状态：**{state['overall']}** · {state['workflow_decision']}")
    lines.append("")
    for reason in state["reasons"]:
        lines.append(f"- {reason}")
    lines.append("")

    lines.append("## 判断边界")
    lines.append("")
    lines.append("| 评估层 | 状态 |")
    lines.append("| --- | --- |")
    for key, label in LAYER_LABELS.items():
        lines.append(f"| {label} | {report['judgment_boundary'][key]} |")
    lines.append("")

    lines.append("## 测量")
    for group in GROUP_ORDER:
        rows = _grouped(report["measurements"]).get(group)
        if not rows:
            continue
        lines.append("")
        lines.append(f"### {GROUP_LABELS.get(group, group)}")
        lines.append("")
        lines.append("| 指标 | 值 | 单位 | 状态 | 可见性 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for row in rows:
            warnings = "；".join(row["warnings"])
            value = _fmt(row["value"])
            if warnings:
                value = f"{value}（{warnings}）"
            lines.append(
                f"| `{row['id']}` | {value} | {_fmt(row['unit'])} | {row['status']} "
                f"| {row.get('visibility', '—')} |"
            )
    lines.append("")

    lines.append("## 发现")
    if not report["findings"]:
        lines.append("")
        lines.append("无。未发现触发阈值的技术风险。")
    else:
        for finding in report["findings"]:
            lines.append("")
            lines.append(
                f"- **[{finding['severity']}] {finding['code']}** — {finding['message']}"
            )
            detail = []
            if finding.get("metric"):
                detail.append(f"指标 `{finding['metric']}` = {_fmt(finding.get('observed_value'))}"
                              f" {_fmt(finding.get('unit'))}".rstrip())
            detail.append(f"检查方式 {finding['check']}")
            if finding.get("evidence_refs"):
                detail.append("证据 " + ", ".join(f"`{ref}`" for ref in finding["evidence_refs"]))
            lines.append(f"  - {'；'.join(detail)}")
    lines.append("")

    lines.append("## 后处理方案")
    plan = report["plan"]
    lines.append("")
    lines.append(f"状态：**{plan['status']}**（方案不等于执行；执行需显式提交 process 作业）")
    if plan["nodes"]:
        lines.append("")
        lines.append("| 算子 | 参数 | 理由 | 证据 | 可回退 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for node in plan["nodes"]:
            params = ", ".join(f"{k}={_fmt(v)}" for k, v in node["params"].items())
            refs = ", ".join(node["evidence_refs"])
            lines.append(
                f"| {node['op']} | {html.escape(params)} | {node['reason']} | {refs} "
                f"| {'是' if node['reversible'] else '否'} |"
            )
    else:
        lines.append("")
        lines.append("无自动算子建议（未发现可安全映射到标准算子的发现）。")
    for note in plan["notes"]:
        lines.append(f"- 注：{note}")
    lines.append("")
    lines.append("下一步（可直接复制的命令形式）：")
    lines.append("")
    for action in plan["next_actions"]:
        lines.append("```text")
        lines.append(action)
        lines.append("```")
    lines.append("")

    lines.append("## 证据与溯源")
    lines.append("")
    rep = report["representation"]
    lines.append(f"- 扫描 profile：`{rep['profile']}`；频谱图："
                 + ", ".join(f"`{item}`" for item in rep["spectrograms"]))
    if rep.get("timeline_windows"):
        lines.append(f"- 时间线窗口：{rep['timeline_windows']}（`{rep['timeline_path']}`）")
    if rep.get("stft_arrays"):
        lines.append(f"- STFT 阵列：`{rep['stft_arrays']}`")
    prov = report["provenance"]
    lines.append(f"- Core {prov['core_version']} · 判断规则 {prov['judgment_rules_version']}"
                 f" · ffmpeg {prov['ffmpeg']}")
    lines.append(f"- profile 参数哈希：`{prov['profile_parameters_sha256']}`")
    lines.append("")
    lines.append("> 本报告只覆盖 L1 测量层（以及标注为 EXECUTED 的层）。未标注 EXECUTED 的层"
                 "不构成任何听感、音乐或商业判断。")
    lines.append("")
    return "\n".join(lines)


def render_report_html(report: dict, images: dict[str, bytes] | None = None) -> str:
    """Single-file display screen. ``images`` maps logical paths to PNG bytes."""
    images = images or {}
    esc = html.escape
    source = report["source"]
    state = report["technical_state"]
    overall = esc(state["overall"])
    overall_class = SEVERITY_CLASS.get(state["overall"], "sev-unknown")

    out: list[str] = []
    out.append("<!doctype html>")
    out.append('<html lang="zh-Hans">')
    out.append("<head><meta charset=\"utf-8\">")
    out.append(f"<title>Moodify 分析报告 — {esc(source['name'])}</title>")
    out.append(f"<style>{_CSS}</style>")
    out.append("</head><body>")
    out.append("<header>")
    out.append('<div class="brand">Moodify <span>分析报告 · MSP 0.2</span></div>')
    out.append(f'<h1>{esc(source["name"])}</h1>')
    out.append('<div class="meta">')
    out.append(f'<span>case <code>{esc(report["case"]["case_id"])}</code></span>')
    out.append(f'<span>{esc(report["generated_at"])}</span>')
    out.append(f'<span><code>{esc(source["sha256"])}</code></span>')
    out.append(f'<span class="badge {overall_class}">{overall}</span>')
    out.append(f'<span>{esc(state["workflow_decision"])}</span>')
    out.append("</div>")
    out.append("</header>")

    out.append('<section id="boundary"><h2>判断边界</h2><div class="layers">')
    for key, label in LAYER_LABELS.items():
        value = report["judgment_boundary"][key]
        out.append(f'<div class="layer"><span class="badge '
                   f'{SEVERITY_CLASS.get(value, "sev-unknown")}">{esc(value)}</span>'
                   f'<span class="layer-label">{esc(label)}</span></div>')
    out.append("</div></section>")

    out.append('<section id="spectrograms"><h2>频谱图</h2>')
    for name in report["representation"]["spectrograms"]:
        data = images.get(name)
        title = esc(Path(name).name)
        if data is None:
            out.append(f'<p class="missing">缺少频谱图 <code>{title}</code></p>')
            continue
        b64 = base64.b64encode(data).decode("ascii")
        out.append(f'<figure><img alt="{title}" src="data:image/png;base64,{b64}">'
                   f'<figcaption>{title}</figcaption></figure>')
    out.append("</section>")

    out.append('<section id="measurements"><h2>测量</h2>')
    grouped = _grouped(report["measurements"])
    for group in GROUP_ORDER:
        rows = grouped.get(group)
        if not rows:
            continue
        out.append(f"<h3>{esc(GROUP_LABELS.get(group, group))}</h3>")
        out.append('<table><thead><tr><th>指标</th><th>值</th><th>单位</th>'
                   '<th>状态</th><th>可见性</th></tr></thead><tbody>')
        for row in rows:
            warnings = "；".join(row["warnings"])
            value = esc(_fmt(row["value"]))
            if warnings:
                value += f' <span class="warn-note">（{esc(warnings)}）</span>'
            visibility = esc(row.get("visibility", "—"))
            out.append(
                f"<tr><td><code>{esc(row['id'])}</code></td><td class=\"num\">{value}</td>"
                f"<td>{esc(_fmt(row['unit']))}</td>"
                f"<td>{esc(row['status'])}</td><td class=\"vis\">{visibility}</td></tr>"
            )
        out.append("</tbody></table>")
    out.append("</section>")

    out.append('<section id="findings"><h2>发现</h2>')
    if not report["findings"]:
        out.append('<p class="muted">无。未发现触发阈值的技术风险。</p>')
    for finding in report["findings"]:
        sev = esc(finding["severity"])
        out.append(
            f'<div class="finding {SEVERITY_CLASS.get(finding["severity"], "sev-unknown")}">'
            f'<div class="finding-head"><span class="badge '
            f'{SEVERITY_CLASS.get(finding["severity"], "sev-unknown")}">{sev}</span>'
            f'<strong>{esc(finding["code"])}</strong>'
            f'<span class="muted">{esc(finding["message"])}</span></div>'
            f'<div class="finding-body">指标 <code>{esc(_fmt(finding.get("metric")))}</code> '
            f'= <strong>{esc(_fmt(finding.get("observed_value")))}</strong> '
            f'{esc(_fmt(finding.get("unit")))} · 检查方式 {esc(finding["check"])}'
        )
        if finding.get("evidence_refs"):
            refs = " ".join(f"<code>{esc(ref)}</code>" for ref in finding["evidence_refs"])
            out.append(f" · 证据 {refs}")
        out.append("</div></div>")
    out.append("</section>")

    plan = report["plan"]
    out.append('<section id="plan"><h2>后处理方案</h2>')
    out.append(f'<p>状态 <span class="badge sev-promised">{esc(plan["status"])}</span>'
               '<span class="muted">（方案不等于执行；执行需显式提交 process 作业）</span></p>')
    if plan["nodes"]:
        out.append('<table><thead><tr><th>算子</th><th>参数</th><th>理由</th>'
                   '<th>证据</th><th>可回退</th></tr></thead><tbody>')
        for node in plan["nodes"]:
            params = ", ".join(f"{k}={_fmt(v)}" for k, v in node["params"].items())
            refs = " ".join(f"<code>{esc(ref)}</code>" for ref in node["evidence_refs"])
            out.append(
                f"<tr><td>{esc(node['op'])}</td><td><code>{esc(params)}</code></td>"
                f"<td>{esc(node['reason'])}</td><td>{refs}</td>"
                f"<td>{'是' if node['reversible'] else '否'}</td></tr>"
            )
        out.append("</tbody></table>")
    else:
        out.append('<p class="muted">无自动算子建议（未发现可安全映射到标准算子的发现）。</p>')
    for note in plan["notes"]:
        out.append(f'<p class="warn-note">注：{esc(note)}</p>')
    for action in plan["next_actions"]:
        out.append(f"<pre>{esc(action)}</pre>")
    out.append("</section>")

    prov = report["provenance"]
    rep = report["representation"]
    out.append('<section id="provenance"><h2>证据与溯源</h2><table><tbody>')
    out.append(f"<tr><td>扫描 profile</td><td><code>{esc(rep['profile'])}</code></td></tr>")
    if rep.get("timeline_windows"):
        out.append(f"<tr><td>时间线窗口</td><td>{rep['timeline_windows']}"
                   f"（<code>{esc(rep['timeline_path'])}</code>）</td></tr>")
    if rep.get("stft_arrays"):
        out.append(f"<tr><td>STFT 阵列</td><td><code>{esc(rep['stft_arrays'])}</code></td></tr>")
    out.append(f"<tr><td>Core</td><td>{esc(prov['core_version'])} · 判断规则 "
               f"{esc(prov['judgment_rules_version'])} · ffmpeg {esc(prov['ffmpeg'])}</td></tr>")
    out.append(f"<tr><td>profile 参数哈希</td><td><code>"
               f"{esc(prov['profile_parameters_sha256'])}</code></td></tr>")
    out.append("</tbody></table>")
    out.append('<p class="muted footer-note">本报告只覆盖标注为 EXECUTED 的评估层；'
               '未标注 EXECUTED 的层不构成任何听感、音乐或商业判断。</p>')
    out.append("</section>")
    out.append("</body></html>")
    return "\n".join(out)


_CSS = """
:root { --fg:#1a1f2e; --muted:#5b6472; --line:#dde2ea; --bg:#ffffff; --panel:#f6f8fa;
        --ok:#15803d; --warn:#b45309; --block:#b91c1c; --unknown:#52606d; }
* { box-sizing:border-box; }
body { margin:0; padding:0 0 64px; background:var(--bg); color:var(--fg);
       font:15px/1.6 -apple-system,"Segoe UI","Microsoft YaHei",Roboto,sans-serif; }
header { padding:32px 40px 20px; border-bottom:1px solid var(--line); }
.brand { font-size:13px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
.brand span { text-transform:none; letter-spacing:0; }
h1 { margin:8px 0 12px; font-size:26px; font-weight:650; }
.meta { display:flex; flex-wrap:wrap; gap:10px 22px; align-items:center;
        font-size:13px; color:var(--muted); }
section { padding:8px 40px 20px; max-width:1080px; }
h2 { font-size:17px; margin:28px 0 10px; padding-top:18px; border-top:1px solid var(--line); }
h3 { font-size:14px; margin:18px 0 6px; color:var(--muted); }
table { border-collapse:collapse; width:100%; font-size:13.5px; margin:6px 0 14px; }
th,td { text-align:left; padding:6px 10px; border-bottom:1px solid var(--line);
        vertical-align:top; }
th { color:var(--muted); font-weight:600; background:var(--panel); }
td.num { font-variant-numeric:tabular-nums; }
td.vis, .vis { color:var(--muted); font-size:12.5px; max-width:420px; }
code { font:12.5px/1.5 ui-monospace,Consolas,monospace; background:var(--panel);
       padding:1px 5px; border-radius:4px; }
pre { background:var(--panel); border:1px solid var(--line); border-radius:6px;
      padding:10px 12px; font:12.5px/1.5 ui-monospace,Consolas,monospace;
      overflow-x:auto; }
.badge { display:inline-block; padding:1px 9px; border-radius:999px; font-size:12px;
         font-weight:600; color:#fff; }
.sev-ok { background:var(--ok); }
.sev-warning { background:var(--warn); }
.sev-blocking { background:var(--block); }
.sev-info { background:var(--unknown); }
.sev-unknown { background:var(--unknown); }
.sev-promised { background:#6d6a75; }
.layers { display:flex; flex-wrap:wrap; gap:12px 28px; margin-top:6px; }
.layer { display:flex; align-items:center; gap:8px; font-size:13.5px; }
.layer-label { color:var(--muted); }
.finding { border:1px solid var(--line); border-left:4px solid var(--unknown);
           border-radius:6px; padding:10px 14px; margin:10px 0; }
.finding.sev-blocking { border-left-color:var(--block); }
.finding.sev-warning { border-left-color:var(--warn); }
.finding-head { display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
.finding-body { margin-top:6px; font-size:13px; color:var(--muted); }
figure { margin:10px 0 18px; }
figure img { max-width:100%; border:1px solid var(--line); border-radius:6px; }
figcaption { font-size:12.5px; color:var(--muted); margin-top:4px; }
.muted { color:var(--muted); }
.missing { color:var(--warn); }
.warn-note { color:var(--warn); }
.footer-note { margin-top:14px; }
"""
