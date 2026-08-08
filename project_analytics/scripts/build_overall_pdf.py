"""Render the Moodify overall analysis as a Chinese management PDF."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


NAVY = colors.HexColor("#173B57")
BLUE = colors.HexColor("#2F6B8A")
PALE = colors.HexColor("#EDF3F6")
ORANGE = colors.HexColor("#C66A3D")
GREEN = colors.HexColor("#4A8C74")
GREY = colors.HexColor("#5B6670")
LIGHT = colors.HexColor("#D7E1E7")


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("MoodifyCN", r"C:\Windows\Fonts\msyh.ttc"))
    pdfmetrics.registerFont(TTFont("MoodifyCN-Bold", r"C:\Windows\Fonts\msyhbd.ttc"))


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(LIGHT)
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont("MoodifyCN", 8)
    canvas.setFillColor(GREY)
    canvas.drawString(18 * mm, 9 * mm, "Moodify 整体数据分析 · 内部决策材料")
    canvas.drawRightString(192 * mm, 9 * mm, f"第 {doc.page} 页")
    canvas.restoreState()


def build_pdf(data_path: Path, output_path: Path) -> None:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    run_dir = data_path.parent
    charts = run_dir / "charts"
    register_fonts()
    styles = getSampleStyleSheet()
    title = ParagraphStyle("TitleCN", parent=styles["Title"], fontName="MoodifyCN-Bold", fontSize=25, leading=34, textColor=NAVY, alignment=TA_LEFT, spaceAfter=8)
    subtitle = ParagraphStyle("SubtitleCN", parent=styles["Normal"], fontName="MoodifyCN", fontSize=10, leading=16, textColor=GREY)
    h1 = ParagraphStyle("H1CN", parent=styles["Heading1"], fontName="MoodifyCN-Bold", fontSize=17, leading=24, textColor=NAVY, spaceBefore=4, spaceAfter=10)
    h2 = ParagraphStyle("H2CN", parent=styles["Heading2"], fontName="MoodifyCN-Bold", fontSize=12, leading=18, textColor=BLUE, spaceBefore=8, spaceAfter=6)
    body = ParagraphStyle("BodyCN", parent=styles["BodyText"], fontName="MoodifyCN", fontSize=9.5, leading=16, textColor=colors.HexColor("#25313A"), spaceAfter=6)
    small = ParagraphStyle("SmallCN", parent=body, fontSize=8, leading=12, textColor=GREY)
    callout = ParagraphStyle("CalloutCN", parent=body, fontName="MoodifyCN-Bold", fontSize=12, leading=20, textColor=NAVY, backColor=PALE, borderPadding=10, borderColor=LIGHT, borderWidth=0.6, borderRadius=3, spaceBefore=8, spaceAfter=12)
    table_header = ParagraphStyle("TableHeader", parent=small, fontName="MoodifyCN-Bold", textColor=colors.white, alignment=TA_CENTER)
    table_cell = ParagraphStyle("TableCell", parent=small, textColor=colors.HexColor("#26333C"))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=18 * mm, bottomMargin=20 * mm, title="Moodify 整体数据分析", author="Moodify Project Analytics")
    story = []
    story += [Spacer(1, 14 * mm), Paragraph("Moodify 整体数据分析", title), Paragraph("工程资产、任务组合、可信度风险与投入回报评估", subtitle), Spacer(1, 8 * mm)]
    story.append(Paragraph(data["executive_conclusion"], callout))
    story.append(Paragraph(f"分析时间：{data['analysis_started_at']}<br/>数据快照：{data['source_snapshot_started_at']}<br/>口径：Asia/Shanghai", subtitle))
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph("核心决策", h1))
    story.append(Paragraph(data["decision"], body))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("本报告区分观测事实与模型估算。仓库、任务和测试数字来自时间戳快照；工时、影响点与 ROI 只用于排序，不代表财务收益。", small))
    story.append(PageBreak())

    story.append(Paragraph("01｜当前状态总览", h1))
    metrics = [[Paragraph("指标", table_header), Paragraph("值", table_header), Paragraph("状态", table_header), Paragraph("来源", table_header)]]
    for row in data["metrics"]:
        metrics.append([Paragraph(row["metric"], table_cell), Paragraph(f"{row['value']} {row['unit']}", table_cell), Paragraph(row["status"], table_cell), Paragraph(row["source"], table_cell)])
    t = Table(metrics, colWidths=[57 * mm, 28 * mm, 23 * mm, 58 * mm], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), NAVY), ("GRID", (0,0), (-1,-1), 0.35, LIGHT), ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, PALE]), ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6), ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6)]))
    story += [t, Spacer(1, 8 * mm), Paragraph("判断", h2), Paragraph("项目不是缺少资产，而是资产的可验证性和可管理性落后于能力扩张。当前最稀缺的不是新功能，而是可信基线。", body)]
    story.append(PageBreak())

    story.append(Paragraph("02｜任务组合与完成度", h1))
    story.append(Image(str(charts / "01_task_portfolio.png"), width=174 * mm, height=98 * mm))
    story.append(Paragraph("已开始任务验收率的分母只包含“已验收”和“待验收”，不把尚未开始或仅规划的任务放入分母。该口径回答的是执行闭环效率，而不是全路线图完成率。", small))
    story.append(Paragraph("治理含义", h2))
    story.append(Paragraph("任务状态存在多来源冲突。下一步应让验收文档成为完成事实、handoff 成为流转事实、orchestration 成为计划事实，并为冲突设置自动检查。", body))
    story.append(PageBreak())

    story.append(Paragraph("03｜变更集中度与工程资本", h1))
    story.append(Image(str(charts / "02_change_concentration.png"), width=174 * mm, height=98 * mm))
    story.append(Paragraph(f"核心与运行时占已跟踪改动的 {next(x['value'] for x in data['metrics'] if x['metric']=='核心/运行时改动集中度')}%。集中改动本身并非错误，但在全量测试门禁失效时会显著放大回归风险。", body))
    story.append(Image(str(charts / "03_code_structure_files.png"), width=174 * mm, height=83 * mm))
    story.append(Paragraph("测试文件和测试代码规模说明项目已经积累了验证资产；但测试资产只有在依赖、导入契约和收集阶段稳定时，才能转化为可信度。", small))
    story.append(PageBreak())

    story.append(Paragraph("04｜测试可信度与主要风险", h1))
    story.append(Image(str(charts / "04_trust_evidence.png"), width=174 * mm, height=94 * mm))
    risk_rows = [[Paragraph("风险", table_header), Paragraph("证据", table_header), Paragraph("分数", table_header), Paragraph("处置", table_header)]]
    for row in sorted(data["risks"], key=lambda item: item["score"], reverse=True):
        risk_rows.append([Paragraph(row["risk"], table_cell), Paragraph(row["evidence"], table_cell), Paragraph(str(row["score"]), table_cell), Paragraph(row["treatment"], table_cell)])
    rt = Table(risk_rows, colWidths=[42 * mm, 46 * mm, 16 * mm, 62 * mm], repeatRows=1)
    rt.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), ORANGE), ("GRID", (0,0), (-1,-1), 0.35, LIGHT), ("VALIGN", (0,0), (-1,-1), "TOP"), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#FBF2ED")]), ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
    story += [Spacer(1, 4 * mm), rt]
    story.append(PageBreak())

    story.append(Paragraph("05｜时间投入与模型回报", h1))
    story.append(Image(str(charts / "05_modeled_roi.png"), width=174 * mm, height=98 * mm))
    inv_rows = [[Paragraph("优先", table_header), Paragraph("行动", table_header), Paragraph("工时区间", table_header), Paragraph("影响点", table_header), Paragraph("模型 ROI", table_header), Paragraph("决策", table_header)]]
    for row in data["investments"]:
        inv_rows.append([Paragraph(str(row["priority"]), table_cell), Paragraph(row["initiative"], table_cell), Paragraph(f"{row['hours_low']}–{row['hours_high']}h", table_cell), Paragraph(str(row["impact_points"]), table_cell), Paragraph(str(row["modeled_roi"]), table_cell), Paragraph(row["decision"], table_cell)])
    it = Table(inv_rows, colWidths=[13 * mm, 58 * mm, 27 * mm, 20 * mm, 25 * mm, 23 * mm], repeatRows=1)
    it.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), GREEN), ("GRID", (0,0), (-1,-1), 0.35, LIGHT), ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#EEF6F2")]), ("ALIGN", (0,1), (0,-1), "CENTER"), ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5), ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6)]))
    story += [it, Spacer(1, 6 * mm), Paragraph("前三项稳定化工作的合计工时约为 11–22 小时。它们的价值主要是恢复后续开发的边际效率、减少返工和提高可验收性，而非直接新增功能。", body)]
    story.append(PageBreak())

    story.append(Paragraph("06｜建议的恢复开发门槛", h1))
    gates = [
        ("门槛 1", "全量测试可完成收集", "收集错误 = 0；再逐步要求全量通过"),
        ("门槛 2", "任务状态单一可信", "状态冲突 = 0；每个正式任务包只有一个当前状态"),
        ("门槛 3", "工作区可回滚", "所有变更完成分桶、归属和验证记录"),
        ("门槛 4", "关键路径在制品受控", "优先关闭当前关键任务，再开启下一任务包"),
    ]
    gate_rows = [[Paragraph("编号", table_header), Paragraph("门槛", table_header), Paragraph("判定标准", table_header)]] + [[Paragraph(a, table_cell), Paragraph(b, table_cell), Paragraph(c, table_cell)] for a,b,c in gates]
    gt = Table(gate_rows, colWidths=[24 * mm, 58 * mm, 84 * mm])
    gt.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), NAVY), ("GRID", (0,0), (-1,-1), 0.35, LIGHT), ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, PALE]), ("LEFTPADDING", (0,0), (-1,-1), 7), ("RIGHTPADDING", (0,0), (-1,-1), 7), ("TOPPADDING", (0,0), (-1,-1), 8), ("BOTTOMPADDING", (0,0), (-1,-1), 8)]))
    story += [gt, Spacer(1, 8 * mm), Paragraph("常态化分析建议", h2), Paragraph("每周更新任务闭环、测试门禁、工作区变更和风险趋势；每个阶段结束时重新评估架构集中度、交付吞吐与投入回报；功能或路线图重大变更时追加专项分析。", body)]
    story.append(PageBreak())

    story.append(Paragraph("附录｜口径与限制", h1))
    for limitation in data["limitations"]:
        story.append(Paragraph(f"• {limitation}", body))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("可复核来源", h2))
    story.append(Paragraph(f"源快照：{data['source_snapshot']}<br/>源快照时间：{data['source_snapshot_started_at']}<br/>结构化分析数据：analysis_data.json<br/>图表：charts/01–05 PNG", small))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("结论置信度", h2))
    story.append(Paragraph("关于工程治理与测试风险的结论：中高置信度。关于时间投入的结论：中等置信度。关于用户价值或财务回报：当前证据不足，不能下结论。", body))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build_pdf(args.data.resolve(), args.output.resolve())
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
