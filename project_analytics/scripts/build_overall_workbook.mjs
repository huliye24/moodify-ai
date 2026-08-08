import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "file:///C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";

const [dataArg, outputArg, previewArg] = process.argv.slice(2);
if (!dataArg || !outputArg || !previewArg) {
  throw new Error("usage: node build_overall_workbook.mjs analysis_data.json output.xlsx previews_dir");
}
const data = JSON.parse(await fs.readFile(dataArg, "utf8"));
await fs.mkdir(path.dirname(outputArg), { recursive: true });
await fs.mkdir(previewArg, { recursive: true });

const wb = Workbook.create();
const summary = wb.worksheets.add("管理摘要");
const metrics = wb.worksheets.add("健康指标");
const tasks = wb.worksheets.add("任务组合");
const changes = wb.worksheets.add("变更集中度");
const code = wb.worksheets.add("代码结构");
const tests = wb.worksheets.add("测试证据");
const risks = wb.worksheets.add("风险登记");
const investments = wb.worksheets.add("投入回报");
const sources = wb.worksheets.add("口径与来源");

const C = { navy:"#173B57", blue:"#2F6B8A", pale:"#EDF3F6", orange:"#C66A3D", green:"#4A8C74", gold:"#B28B35", red:"#B6473A", grey:"#5B6670", light:"#D7E1E7", white:"#FFFFFF" };
const sheets = [summary, metrics, tasks, changes, code, tests, risks, investments, sources];
for (const s of sheets) s.showGridLines = false;

function titleBand(sheet, range, title, subtitle) {
  range.merge();
  range.values = [[title]];
  range.format = { fill:C.navy, font:{bold:true,color:C.white,size:18}, verticalAlignment:"center", wrapText:true };
  range.format.rowHeight = 34;
  const row = range.getRow(0);
  const sub = sheet.getRangeByIndexes(row.rowIndex + 1, range.columnIndex, 1, range.columnCount);
  sub.merge(); sub.values = [[subtitle]];
  sub.format = { fill:C.pale, font:{color:C.grey,size:9}, verticalAlignment:"center", wrapText:true };
  sub.format.rowHeight = 28;
}
function header(range, fill=C.blue) {
  range.format = { fill, font:{bold:true,color:C.white}, verticalAlignment:"center", wrapText:true, borders:{preset:"outside",style:"thin",color:C.light} };
  range.format.rowHeight = 24;
}
function body(range) {
  range.format = { font:{color:"#26333C",size:9}, verticalAlignment:"top", wrapText:true, borders:{insideHorizontal:{style:"thin",color:C.light},bottom:{style:"thin",color:C.light}} };
}
function widths(sheet, widths) {
  widths.forEach((w, i) => sheet.getRangeByIndexes(0, i, 1, 1).format.columnWidth = w);
}

titleBand(summary, summary.getRange("A1:J1"), "Moodify 整体数据分析", `分析时间 ${data.analysis_started_at}｜源快照 ${data.source_snapshot_started_at}｜Asia/Shanghai`);
summary.getRange("A4:J5").merge(); summary.getRange("A4:J5").values=[[data.executive_conclusion]];
summary.getRange("A4:J5").format={fill:C.pale,font:{bold:true,color:C.navy,size:12},wrapText:true,verticalAlignment:"center",borders:{preset:"outside",style:"thin",color:C.light}};
summary.getRange("A7:F7").values=[["关键指标","当前值","单位","状态","解释","数据来源"]]; header(summary.getRange("A7:F7"));
const metricRows = data.metrics.map(x=>[x.metric,x.value,x.unit,x.status,x.metric==="测试/源代码物理行比"?"结构规模比，不是覆盖率":"观测事实",x.source]);
summary.getRange(`A8:F${7+metricRows.length}`).values=metricRows; body(summary.getRange(`A8:F${7+metricRows.length}`));
summary.getRange(`B8:B${7+metricRows.length}`).format.numberFormat="0.0";
summary.getRange("H7:J7").merge(); summary.getRange("H7:J7").values=[["当前决策"]]; header(summary.getRange("H7:J7"),C.orange);
summary.getRange("H8:J12").merge(); summary.getRange("H8:J12").values=[[data.decision]];
summary.getRange("H8:J12").format={fill:"#FBF2ED",font:{bold:true,color:C.navy,size:11},wrapText:true,verticalAlignment:"center",borders:{preset:"outside",style:"thin",color:C.light}};
summary.getRange("H14:J14").merge(); summary.getRange("H14:J14").values=[["恢复新增功能门槛"]]; header(summary.getRange("H14:J14"),C.green);
summary.getRange("H15:J18").values=[["1","全量测试收集错误 = 0",null],["2","任务状态冲突 = 0",null],["3","工作区完成分桶且可回滚",null],["4","当前关键路径任务关闭",null]]; body(summary.getRange("H15:J18"));
summary.getRange("A19:B19").values=[["任务状态","数量"]]; header(summary.getRange("A19:B19"));
summary.getRange("A20:A24").values=data.task_states.map(x=>[x.label]);
summary.getRange("B20:B24").formulas=[["='任务组合'!B3"],["='任务组合'!B4"],["='任务组合'!B5"],["='任务组合'!B6"],["='任务组合'!B7"]];
body(summary.getRange("A20:B24"));
const taskChart=summary.charts.add("bar",summary.getRange("A19:B24")); taskChart.title="任务组合"; taskChart.hasLegend=false; taskChart.setPosition("D20","J33");
summary.getRange("A35:B35").values=[["变更区域","文件数"]]; header(summary.getRange("A35:B35"),C.orange);
const topChanges=data.change_areas.slice(0,8); summary.getRange(`A36:B${35+topChanges.length}`).values=topChanges.map(x=>[x.area,x.changed_files]); body(summary.getRange(`A36:B${35+topChanges.length}`));
const changeChart=summary.charts.add("bar",summary.getRange(`A35:B${35+topChanges.length}`)); changeChart.title="已跟踪变更集中度"; changeChart.hasLegend=false; changeChart.setPosition("D35","J49");
widths(summary,[24,13,10,12,28,20,3,8,28,16]); summary.freezePanes.freezeRows(2);

titleBand(metrics,metrics.getRange("A1:F1"),"健康指标","所有指标均来自同一源快照；状态是管理解释，不改变原始值。" );
metrics.getRange("A4:F4").values=[["指标","值","单位","状态","来源","备注"]]; header(metrics.getRange("A4:F4"));
metrics.getRange(`A5:F${4+metricRows.length}`).values=data.metrics.map(x=>[x.metric,x.value,x.unit,x.status,x.source,x.metric==="测试/源代码物理行比"?"不是覆盖率":""]); body(metrics.getRange(`A5:F${4+metricRows.length}`));
metrics.getRange(`B5:B${4+metricRows.length}`).format.numberFormat="0.0";
metrics.getRange(`D5:D${4+metricRows.length}`).conditionalFormats.add("containsText",{text:"阻断",format:{fill:"#F4CBC6",font:{bold:true,color:C.red}}});
metrics.getRange(`D5:D${4+metricRows.length}`).conditionalFormats.add("containsText",{text:"高",format:{fill:"#F9E2D4",font:{bold:true,color:C.orange}}});
widths(metrics,[30,14,10,12,24,32]); metrics.freezePanes.freezeRows(4);

titleBand(tasks,tasks.getRange("A1:E1"),"任务组合","汇总区域使用公式从任务明细自动计算，便于后续更新。" );
tasks.getRange("A2:B2").values=[["状态","任务数"]]; header(tasks.getRange("A2:B2"));
tasks.getRange("A3:A7").values=data.task_states.map(x=>[x.label]);
const rawStart=12, rawEnd=rawStart+data.tasks.length-1;
const stateLabels=Object.fromEntries(data.task_states.map(x=>[x.state,x.label]));
tasks.getRange(`A${rawStart}:D${rawEnd}`).values=data.tasks.map(x=>[x.task,stateLabels[x.state]||x.state,x.handoff_status,x.acceptance_docs]);
tasks.getRange("B3").formulas=[[`=COUNTIF(B${rawStart}:B${rawEnd},A3)`]]; tasks.getRange("B3:B7").fillDown();
tasks.getRange("D2:E2").values=[["正式任务包","已开始验收率"]]; header(tasks.getRange("D2:E2"),C.green);
tasks.getRange("D3").formulas=[["=SUM(B3:B7)"]]; tasks.getRange("E3").formulas=[["=IFERROR(B3/(B3+B4),0)"]]; tasks.getRange("E3").format.numberFormat="0.0%";
tasks.getRange(`A${rawStart-1}:D${rawStart-1}`).values=[["任务包","状态","Handoff 状态","验收文档数"]]; header(tasks.getRange(`A${rawStart-1}:D${rawStart-1}`)); body(tasks.getRange(`A${rawStart}:D${rawEnd}`));
tasks.tables.add(`A${rawStart-1}:D${rawEnd}`,true,"TaskPortfolioTable").style="TableStyleMedium2";
widths(tasks,[56,18,42,15,18]); tasks.freezePanes.freezeRows(rawStart-1);

titleBand(changes,changes.getRange("A1:D1"),"变更集中度","改动文件数来自 git diff --numstat；只统计已跟踪文件。" );
changes.getRange("A4:C4").values=[["区域","改动文件数","占比"]]; header(changes.getRange("A4:C4"),C.orange);
const ce=4+data.change_areas.length; changes.getRange(`A5:B${ce}`).values=data.change_areas.map(x=>[x.area,x.changed_files]);
changes.getRange("C5").formulas=[[`=IFERROR(B5/SUM($B$5:$B$${ce}),0)`]]; changes.getRange(`C5:C${ce}`).fillDown(); changes.getRange(`C5:C${ce}`).format.numberFormat="0.0%"; body(changes.getRange(`A5:C${ce}`));
changes.getRange("A2:D2").values=[["已跟踪改动文件",data.repository.changed_tracked_files,"核心/运行时集中度",data.metrics.find(x=>x.metric==="核心/运行时改动集中度").value/100]]; changes.getRange("D2").format.numberFormat="0.0%";
widths(changes,[34,18,16,22]); changes.freezePanes.freezeRows(4);

titleBand(code,code.getRange("A1:D1"),"代码结构","物理行数反映资产规模，不代表覆盖质量。" );
code.getRange("A4:C4").values=[["类别","文件数","物理行数"]]; header(code.getRange("A4:C4"),C.green);
code.getRange("A5:C6").values=[["Python 源代码",data.code_structure.python_source_files,data.code_structure.source_physical_lines],["Python 测试",data.code_structure.python_test_files,data.code_structure.test_physical_lines]]; body(code.getRange("A5:C6"));
code.getRange("A8:B8").values=[["测试/源代码物理行比",data.code_structure.test_to_source_physical_line_ratio_pct/100]]; code.getRange("B8").format.numberFormat="0.0%";
code.getRange("A10:D11").merge(); code.getRange("A10:D11").values=[["解释：测试资产规模可观，但由于全量测试收集失败，现阶段不能把结构规模等同于验证可信度。"]]; code.getRange("A10:D11").format={fill:C.pale,wrapText:true,font:{color:C.navy,bold:true},verticalAlignment:"center"}; widths(code,[30,18,20,28]);

titleBand(tests,tests.getRange("A1:D1"),"测试证据","当前只采用全量 pytest 收集结果；目标测试通过记录不混入本次快照。" );
tests.getRange("A4:B4").values=[["证据","值"]]; header(tests.getRange("A4:B4"),C.red);
tests.getRange("A5:B8").values=[["门禁状态",data.test_evidence.status],["收集到的测试",data.test_evidence.tests_collected],["收集错误",data.test_evidence.collection_errors],["退出码",data.test_evidence.exit_code]]; body(tests.getRange("A5:B8"));
tests.getRange("A10:D12").merge(); tests.getRange("A10:D12").values=[["结论：全量测试收集阶段即失败，因此不能声明系统级测试基线为绿色。优先修复导入契约与依赖，再评估真实失败用例。"]]; tests.getRange("A10:D12").format={fill:"#F9E2D4",font:{bold:true,color:C.red},wrapText:true,verticalAlignment:"center",borders:{preset:"outside",style:"thin",color:C.orange}}; widths(tests,[32,18,20,28]);

titleBand(risks,risks.getRange("A1:G1"),"风险登记","风险分数 = 概率 × 影响（1–5）；分数是决策排序，不是概率预测。" );
risks.getRange("A4:G4").values=[["风险","证据","概率","影响","分数","责任域","处置建议"]]; header(risks.getRange("A4:G4"),C.orange);
const rr=data.risks.map(x=>[x.risk,x.evidence,x.probability,x.impact,x.score,x.owner,x.treatment]); risks.getRange(`A5:G${4+rr.length}`).values=rr; body(risks.getRange(`A5:G${4+rr.length}`)); risks.getRange(`E5:E${4+rr.length}`).conditionalFormats.add("colorScale",{colors:["#EEF6F2","#F7E6B5","#F4CBC6"],thresholds:["min","50%","max"]}); widths(risks,[32,42,10,10,10,16,56]); risks.freezePanes.freezeRows(4);

titleBand(investments,investments.getRange("A1:J1"),"投入回报模型","工时、影响点和 ROI 均为估算；模型 ROI = 影响点 ÷ 工时中位数。" );
investments.getRange("A4:J4").values=[["优先级","行动","工时下限","工时上限","工时中位","影响点","模型 ROI","置信度","降低风险","决策"]]; header(investments.getRange("A4:J4"),C.gold);
const ie=4+data.investments.length;
investments.getRange(`A5:J${ie}`).values=data.investments.map(x=>[x.priority,x.initiative,x.hours_low,x.hours_high,null,x.impact_points,null,x.confidence,x.risk_reduced,x.decision]);
investments.getRange("E5").formulas=[["=AVERAGE(C5:D5)"]]; investments.getRange(`E5:E${ie}`).fillDown(); investments.getRange("G5").formulas=[["=IFERROR(F5/E5,0)"]]; investments.getRange(`G5:G${ie}`).fillDown();
body(investments.getRange(`A5:J${ie}`)); investments.getRange(`C5:G${ie}`).format.numberFormat="0.00"; investments.getRange(`G5:G${ie}`).conditionalFormats.add("dataBar",{color:C.gold,gradient:true});
investments.getRange("A12:D12").values=[["立即稳定化总工时下限","立即稳定化总工时上限","平均模型 ROI","说明"]]; header(investments.getRange("A12:D12"),C.green);
investments.getRange("A13").formulas=[["=SUM(C5:C7)"]]; investments.getRange("B13").formulas=[["=SUM(D5:D7)"]]; investments.getRange("C13").formulas=[["=AVERAGE(G5:G7)"]]; investments.getRange("D13").values=[["前三项是恢复后续开发效率的基础投资"]]; body(investments.getRange("A13:D13"));
widths(investments,[10,38,14,14,14,12,14,14,32,14]); investments.freezePanes.freezeRows(4);

titleBand(sources,sources.getRange("A1:D1"),"口径、来源与限制","用于复核分析结论，避免把代理指标解释成业务结果。" );
sources.getRange("A4:D4").values=[["项目","定义/内容","来源","性质"]]; header(sources.getRange("A4:D4"));
const srcRows=[
  ["分析时间",data.analysis_started_at,"运行清单","观测"],
  ["源快照",data.source_snapshot,"snapshot.json","观测"],
  ["已开始验收率","已验收 ÷（已验收 + 待验收）","任务状态文件","公式"],
  ["核心/运行时集中度","两区域改动文件数 ÷ 全部已跟踪改动文件数","git diff --numstat","公式"],
  ["模型 ROI","影响点 ÷ 估算工时中位数","决策假设","估算"],
  ...data.limitations.map(x=>["限制",x,"分析说明","限制"])
]; sources.getRange(`A5:D${4+srcRows.length}`).values=srcRows; body(sources.getRange(`A5:D${4+srcRows.length}`)); widths(sources,[24,72,34,14]); sources.freezePanes.freezeRows(4);

const inspection = await wb.inspect({kind:"workbook,sheet,table",maxChars:8000,tableMaxRows:4,tableMaxCols:8});
await fs.writeFile(path.join(previewArg,"workbook_inspection.txt"),inspection.ndjson ?? String(inspection),"utf8");
const formulaErrors = await wb.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",options:{useRegex:true,maxResults:100},maxChars:4000});
await fs.writeFile(path.join(previewArg,"formula_error_scan.txt"),formulaErrors.ndjson ?? String(formulaErrors),"utf8");

const out = await SpreadsheetFile.exportXlsx(wb);
await out.save(outputArg);
const renderLog = [];
for (const s of sheets) {
  try {
    const preview = await wb.render({sheetName:s.name,autoCrop:"all",scale:1,format:"png"});
    await fs.writeFile(path.join(previewArg,`${s.name}.png`),new Uint8Array(await preview.arrayBuffer()));
    renderLog.push(`${s.name}: ok`);
  } catch (error) {
    renderLog.push(`${s.name}: failed - ${error?.message ?? error}`);
  }
}
await fs.writeFile(path.join(previewArg,"render_log.txt"),renderLog.join("\n")+"\n","utf8");
console.log(outputArg);
