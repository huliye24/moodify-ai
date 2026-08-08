# ScoreBackend 合同（Stage 0 冻结）

**冻结日期：** 2026-08-02  
**版本：** `score-backend/0.1`

## 1. 角色

ScoreBackend 是 MoodifyScore 与外部排版/渲染引擎之间的稳定适配层。Moodify
持有语义与证据；后端只负责呈现（排版、渲染、播放或人工编辑能力）。

```text
MoodifyScore v0.1  ──export MusicXML──>  ScoreBackend  ──>  PDF / SVG / PNG + evidence
```

## 2. ScoreBackend Protocol

```python
class ScoreBackend(Protocol):
    backend_id: str
    display_name: str
    license_label: str          # e.g. "GPLv3 (external process)"
    capabilities: BackendCapabilities

    def available(self) -> bool: ...                    # 探测后端可执行环境
    def version(self) -> str | None: ...                # 显式探测版本；不可用=None
    def validate(self, score) -> ValidationResult: ...  # 合同校验（可默认走 MoodifyScore.validate）
    def export(self, score, out_dir) -> ExportResult: ...  # MusicXML/PDF/SVG 导出
    def inspect(self, artifact) -> InspectionResult: ...   # 重解析产物做 round-trip 检查
```

## 3. BackendCapabilities（能力位，不实现）

| 能力 | 类型 | MuseScore(本任务) | Verovio | LilyPond | OSMD |
|---|---|---|---|---|---|
| musicxml_import | bool | true | true | true | true |
| pdf_export | bool | true | false | true | false |
| svg_export | bool | true | true | false | true |
| png_export | bool | true | false | false | false |
| audio_playback | bool | false | false | false | false |
| human_editing | bool | false | false | false | false |
| license | str | GPLv3（外部进程） | LGPL-3.0 | GPL-3.0 | MIT |

**规则：** 未实现后端（Verovio/LilyPond/OSMD）只冻结能力位，**不得创建可
调用但会误导用户的假实现**。后端探测函数返回 `UNAVAILABLE`，调用方必须
处理该状态。

## 4. 后端注册与探测

1. 注册表 `BACKENDS`：`musescore`（实现）、`verovio`/`lilypond`/`osmd`（能力位占位，available=False）。
2. `detect_musescore()` 探测顺序：显式路径参数 > 环境变量（如 `MUSESCORE_BIN`）> PATH 搜索。
3. 探测记录：可执行路径、`--version` 输出、exit code、耗时、探测时间；进入 evidence。
4. MuseScore 缺失或版本无法解析 → 稳定返回 `UNAVAILABLE`；CLI 显示明确信息，不伪成功。

## 5. 进程调用安全合同

1. **参数数组**启动独立进程；**禁止 shell 字符串拼接**（防命令注入）。
2. 超时（默认 120s，可配置）、退出码、stdout/stderr、命令参数、版本、输出文件哈希全部进入 evidence。
3. 输出目录必须**全新或为空**；拒绝覆盖既有文件；拒绝路径逃逸（`..`、绝对路径、符号链接穿透）。
4. 非零退出码、超时、stderr 非空 → `ExportResult` 标记失败并带诊断，禁止伪成功。
5. MuseScore 的 GPLv3、版本、调用方式记入许可证清单；不复制/修改其源码与安装。

## 6. 导出与重解析（round-trip 基础）

1. 导出链：MoodifyScore → MusicXML 4.x（partwise）→ MuseScore 无界面导出 PDF/SVG。
2. 输出产物集：`{score}.musicxml`、`{score}.pdf`、`{score}.svg`（每页）、`manifest.json`、`roundtrip_report.json`。
3. 导出后**重解析验证**：至少比较 part、measure、note、pitch、duration、tempo。
4. 允许的损失必须显式进入 `roundtrip_report.json`；不得用"成功导出"掩盖差异。

## 7. 错误码

| 码 | 含义 | CLI 行为 |
|---|---|---|
| 0 | 成功 | 正常退出 |
| 1 | 通用失败 | ERROR + 诊断 |
| 2 | 用法/合同错误 | ERROR + usage |
| 3 | 后端 UNAVAILABLE | 明确提示未安装/未探测到 |

## 8. 本任务不实现

- 不接 Verovio/LilyPond/OSMD（只冻结能力位）。
- 不开发可视化编辑器；不重新实现排版算法。
- 不把 `.mscz` 作为事实源或内部格式。
