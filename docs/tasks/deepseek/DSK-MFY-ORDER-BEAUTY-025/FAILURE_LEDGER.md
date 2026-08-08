# DSK-MFY-ORDER-BEAUTY-025｜失败台账

**日期：** 2026-08-02 UTC  
**规则：** 历史失败不得删除或改写为成功（PR-007）。

| # | 阶段 | 失败 | 根因 | 处置 |
|---|---|---|---|---|
| 1 | Stage B | test_collection collected=0 | 解析正则匹配 `tests? collected` 但实际行是 "662 tests collected in 4.47s"——正则没匹配到 | 改用 `re.search(r"(\d+)\s+tests? collected", out)` 修复 |
| 2 | 测试 | test_red_line_triggered KeyError red_lines | 测试 fixture 目录建在 `tmp/observations`，代码找 `tmp/project_analytics/observations` | fixture 目录加 project_analytics 层 |
| 3 | 测试 | test_stage_honest_not_measured 失败 | test_weekly 直接赋值 `reports.ROOT = tmp_path` 污染模块全局，后续测试读到临时 ROOT | 改用 monkeypatch.setattr（自动恢复） |

## 负面知识沉淀

- **测试隔离教训**：修改模块级 ROOT/配置必须用 monkeypatch（pytest 自动
  恢复），直接赋值会污染同文件后续测试——这是测试编写铁律（EX-009 模式）。
- **观测层解析要匹配真实输出格式**：pytest 汇总行的 "N tests collected"
  格式需精确正则。

## 边界

- 观测层零写入产品代码/任务状态/工作区；历史分析不可覆盖（observations/
  按 run_id 追加）。
- 无网络上传、后台监听、个人行为跟踪、新服务依赖。
