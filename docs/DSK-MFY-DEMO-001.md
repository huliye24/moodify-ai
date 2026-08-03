# DSK-MFY-DEMO-001：投资人演示版任务包（交接单）

**状态：** ✅ 已完成并真机验证通过
**日期：** 2026-08-03
**定位：** Moodify Android App 对外演示（投资人/客户），端到端真实链路，无假进度。
**交接官：** Claude A

---

## 0. 演示目标与故事线

五幕式演示，全部真实链路：

| 幕 | 内容 | 现状 |
|---|---|---|
| 一 | CWC 通行证开场：深链 `moodify://cwc/CWC-XZ7M-42KP` → 礼物页 → 输入通行码激活 → 创作者中心 | ✅ 已实现（保留） |
| 二 | 配对：我的 → 电脑端连接 → 配对成功 | ✅ 已实现（保留） |
| 三 | 真上传：系统文件选择器选真实音频 → 上传后端 | ❌ 现为 mock 文件列表 |
| 四 | 真处理：后端 v01 管线真实跑，App 显示真实阶段进度 | ❌ 现为静态假进度（68% 写死） |
| 五 | 真结果：作品库出现真实产物（真实文件名 + MRS/诊断指标） | ❌ 现为 demoWorks 假数据 |

---

## 1. 已扫描事实（2026-08-03，Claude A 验证）

### 可用资产
- **后端启动**：`moodify serve` → uvicorn `0.0.0.0:8000`（`moodify-core-package/src/moodify/cli.py:290`）
- **mobile API v1**：health/pair/pair-revoke/capabilities 为 live；projects/uploads/jobs/artifacts 返回 `NOT_IMPLEMENTED`（`api/routes/v1.py:299-350`）；契约文档 `docs/api/v1.md`
- **contract 测试**：`pytest tests/api/test_v1_contract.py` → **13 passed**（刚验证）
- **v01 管线 Windows 冒烟**：`process_audio` 真实跑通，12s 合成音频 18.1s 完成，quality gate passed，MRS 986.2→991.86（**刚验证**）
- **设备**：小米 10 `5fe6dfde` 已连接 adb
- **构建环境**：JAVA_HOME=`C:\Program Files\Android\Android Studio\jbr`，ANDROID_HOME=`C:\Users\Administrator\AppData\Local\Android\Sdk`（bash 未设，需显式 export）
- **APK**：`app-debug.apk` 已构建（18MB），但**落后最新提交 e70cf6d（抽屉去重）**，需重建

### 已知边界（演示时如实展示，不伪装）
1. **CWC 为客户端 demo 验证**（`CwcRepository.kt:11` 注释自认）：通行码在本地 SharedPreferences 验证，无服务器环节。演示定位为"产品概念展示"。
2. **MRS 引擎走 proxy fallback**：core 包独立运行时 `moodify_runtime` 不在路径，MRS 用 `mrs_proxy_v01` 估算。数值方向正确（处理后提升），但非生产引擎。
3. **v1 业务接口为演示级实现**：本任务包实现的 uploads/projects/jobs/artifacts 遵循冻结 schema 与错误契约，但语义为单机演示（内存态 job 注册表 + 临时文件存储），非生产数据层。
4. **处理时长**：真实歌曲（3-4 分钟）预计 30-60s，演示时可展示真实进度推进，正好作为亮点。

---

## 2. 缺陷清单（扫描产出）

| # | 缺陷 | 证据 | 处置 |
|---|---|---|---|
| D1 | APK 落后最新代码（缺 e70cf6d 抽屉去重） | APK 17:37:19 vs 提交 17:39:53 | 最终重建 |
| D2 | 处理页纯界面假象：进度写死 68%、波形静态、"AI Demo Track" | `ProcessingScreen.kt:54,63,77` | 任务包核心改造 |
| D3 | 上传为 mock 文件列表，无系统文件选择器 | `UploadFlowScreen.kt:53` | 接 OpenDocument |
| D4 | CWC 客户端假验证 | `CwcRepository.kt:11` | 保留，文档标注边界 |
| D5 | 作品库假数据 | `WorksScreen.kt:30` | 真实产物入库 |
| D6 | 业务接口全 501 | `v1.py:299-350` | 演示级实现 |
| D7 | 首次启动 CWC 认证拦截 | `MoodifyApp.kt:88-94` | 保留为开场故事；提供演示重置入口 |

---

## 3. 实施任务

### B 后端（moodify-core-package）

**B1 — v01_pipeline 阶段回调**
`process_audio(input_path, preset, output_dir, on_stage=None)`：在 S/A/D/P/V/R/G 七阶段各调用 `on_stage(stage_name, progress_float)`。默认 None 保持现有行为（现有测试不受影响）。改动点：`v01_pipeline.py:30` 签名 + 各阶段标注处。

**B2 — v1.py 演示级实现（保持冻结 schema + 错误契约）**
- `POST /api/v1/uploads`：multipart 接收 `project_id, filename, size_bytes, sha256` + 二进制音频 → 存 `data/demo_uploads/`，校验 sha256 与 size → `V1UploadStatus`（status=received）
- `POST /api/v1/projects`：创建 project 并**自动创建并启动第一个 job**（关联首个 audio_id）→ `V1ProjectStatus`
- `GET /api/v1/jobs/{id}`：返回 `V1JobStatus`，含 `progress` 与 `stage`（当前阶段名），后台线程跑 `process_audio(on_stage=...)`，阶段映射进度：scan 0.15 / analyze 0.35 / diagnose 0.45 / process 0.65 / validate 0.8 / report 0.9 / generate 1.0
- `POST /api/v1/jobs/{id}/cancel`：置 cancelled（不杀线程，标记跳过产物入库）
- `GET /api/v1/artifacts/{id}`：`V1Artifact` 元数据 + 可选下载 WAV；另增 `GET /api/v1/jobs/{id}/result` 返回 JSON 摘要（preset、MRS 前后、gate、诊断 issue 前 3 条）供 App 展示真实指标
- 全部要求 `Authorization: Bearer`（复用 `_pair_store`），错误走 `_v1_error` 结构
- job 注册表：模块级内存 dict（演示语义，重启即清，与 token 生命周期一致）

**B3 — 测试**
新增 `tests/api/test_v1_demo_flow.py`：合成小音频 → pair → uploads → projects → 轮询 jobs 至 done → artifacts/result 校验真实产物存在、MRS 提升、gate passed。跑通后全量 `pytest` 保持 green。

### A Android（apps/android）

**A1 — 系统文件选择器**：`UploadFlowScreen.kt` 接 `ActivityResultContracts.OpenDocument`（audio/*，多选），真实文件名/大小/类型；保留"微信导入/云端导入"为占位入口（演示时走"本地导入"）。

**A2 — 上传+真实处理流程**：新增 `DemoProcessRepository`（或扩展 `MoodifyApiClient`）：
- 选文件 → 计算 sha256 → `POST /uploads` → `POST /projects` → 轮询 `GET /jobs/{id}`（2s 间隔）→ 阶段/进度实时刷新
- `ProcessingScreen` 改造：静态 68% 改为状态驱动（阶段名、进度条、步骤勾选真实映射），失败显示错误
- 上传前检查配对 token，未配对引导到"我的"连接页

**A3 — 作品库真实产物**：处理成功后把结果摘要（文件名、preset、MRS 前后、gate、耗时）持久化到本地（SharedPreferences JSON 列表），`WorksScreen` 真实作品显示真实文件名/指标，`WorkDetailScreen` 展示诊断摘要；demoWorks 假数据降级为"示例"标记或移除。

**A4 — 演示重置入口**：设置页加"重置演示会话"（`CwcRepository.resetDemoSession()` + 清作品缓存 + 清配对），保证第二次演示一键回到开场故事。

### C 配套

**C1 — 一键启动**：`scripts/demo_serve.bat`：设 PYTHONPATH（core + runtime）、`moodify serve`；`scripts/demo_adb.bat`：`adb reverse tcp:8000 tcp:8000`。

**C2 — 演示流程文档**：`docs/DSK-MFY-DEMO-001.md` 追加操作手册（五幕步骤 + 预期 + 故障排查表）。

**C3 — 端到端验证 + 交付**：真机 golden path 五幕全跑通；重建 APK（含最新代码）并安装；截图归档。

---

## 4. 验证标准（完成定义）

1. `pytest`（core）全绿，新增 demo flow 测试通过 ✅（725 passed + 19 API tests）
2. 真机五幕 golden path 全通：深链激活 → 配对 → 真文件上传 → 真实进度处理 → 作品库真实产物 ✅
3. APK 为最新代码重建并安装到 5fe6dfde ✅
4. 无崩溃、无底部遮挡、无假进度（ProcessingScreen 只显示后端回报的真实阶段）✅

### 真机验证记录（2026-08-03，小米 10 / 5fe6dfde）

| 幕 | 结果 | 证据 |
|---|---|---|
| 一 CWC | ✅ 深链 → 礼物页 → 通行码预填 → 激活成功 | 截图 `deliverables/demo_01_launch.png`、`demo_02_deeplink.png`、`demo_03_activated.png` |
| 二 配对 | ✅ 连接 → 配对成功（显示"撤销配对"） | adb UI dump |
| 三 上传 | ✅ 上传页"演示音频"专区（App 专属目录 `files/demo/`）直接选歌 | 服务端 `data/demo/uploads/` 收到文件 |
| 四 处理 | ✅ 真实进度：扫描→特征分析→智能诊断→DSP(45%)→报告(80%)→完成；MRS 1002.4→1048.8 (Δ46.4)；真实诊断 issues | 截图 `deliverables/demo_04_works.png` |
| 五 作品库 | ✅ demo_01.wav 真实条目：clean_master + MRS Δ+46.4 + 真实日期 | 截图 `deliverables/demo_04_works.png` |

### 验证中发现并修复的缺陷（追加）

- **D8**（真机发现）：`MoodifyApiClient.request()` 的 Authorization 头在 outputStream 写入（连接建立）之后设置 → `PropertyException: Cannot set request property after connection is made`。首次配对后所有带 token 的请求失败。已修复（头设置在写流之前）。**此 bug 在单测环境不暴露（token 参数此前恒为 null），只有真机带 token 流程触发。**
- **D9**（真机发现）：ProcessingHub 文案"不超过 200MB"与后端 50MB 限制不一致 → 已统一为 50MB。
- **D10**（需求新增）：系统文件选择器对 adb push 的 wav 不友好（DocumentsUI 分类视图滞后）→ 新增 App 内"演示音频"专区（`files/demo/` 目录直读，零权限），脚本 `scripts/demo_push.bat` 推送歌曲。

## 5. 风险

- v01 管线处理真实歌曲耗时长（30-60s）：属预期，演示话术按"真实算力在跑"编排
- 大文件超 50MB 限制：演示选 <50MB 音频；`MoodifyApiClient` 已有超时分类

---

## 6. 演示操作手册（对外演示使用）

### 前置准备（演示前 10 分钟）

1. 启动后端（电脑端，PowerShell）：
   ```
   E:\moodify\scripts\demo_serve.bat
   ```
   看到 `Uvicorn running on http://0.0.0.0:8000` 即就绪。
2. 手机 USB 连电脑并开 USB 调试，建立反向代理（PowerShell）：
   ```
   E:\moodify\scripts\demo_adb.bat
   ```
   输出显示 `tcp:8000` 即成功。手机端 app 的服务器地址保持默认 `http://127.0.0.1:8000`。
3. 可选：若上次演示留有数据，打开 App → 我的 → 左侧栏 → 设置 → 演示 → 重置演示会话。

### 五幕演示脚本

| 幕 | 操作 | 预期 |
|---|---|---|
| 一 CWC 开场 | 在手机浏览器打开 `moodify://cwc/CWC-XZ7M-42KP`（或用带深链的二维码），进入礼物页 → 点"激活通行证" | 通行码自动填入 → 激活成功 → 创作者中心展示权益（演示版本为本地验证） |
| 二 配对 | 底部"我的" → 电脑端连接卡片 → 连接 → 配对 | 状态徽章变"已连接"，显示 API v0.1.0 |
| 三 真上传 | 底部"处理" → 处理中心 → 选择音频文件 → 上传页"演示音频"专区点一首歌（预置在 App 目录，用 `demo_push.bat` 推送）；或走系统文件选择器 | 批量页显示真实文件名 |
| 四 真处理 | 点"开始处理" | 处理页显示真实阶段（扫描→特征分析→智能诊断→DSP 处理→质量验证→报告生成→交付打包）与真实百分比；约 30-60s 后完成 |
| 五 真结果 | 点"查看作品库" | 作品库顶部出现真实作品：真实文件名 + preset + MRS 前后分数（Δ提升）+ 质量门通过 |

### 播放功能（2026-08-03 追加，Media3）

- 作品库：真实作品卡片右侧播放按钮 → 播放后端处理产物（`/api/v1/artifacts/{id}/download`），底部固定播放条（播放/暂停/进度/时间）
- 作品详情：**处理前 / 处理后一键切换对比播放**（处理后走 artifacts，处理前走 `/api/v1/uploads/{id}/download`）——演示核心亮点
- 播放条带 Bearer token 自动刷新（PlaybackManager 每次播放前从 TokenStore 取最新 token）
- 已验证：真机播放 00:07→00:51 进度推进；切换"处理前"后播放条标题变"（处理前）"
- 平台化路线：已定接受 GPL-3.0，Booming Music 播放核心（Media3 + 逐字歌词 + 15 段 EQ/AutoEQ + 无缝播放）作为中期移植目标；"无损母带 + 高保真播放"为平台卖点

### 演示话术要点

- 第四幕的等待时间就是真实算力在跑：展示"真实处理引擎在电脑端执行 DSP 管线"
- MRS 分数（如 986 → 992）是质量分提升的真实数据，可指向处理前后对比
- 若被问"CWC 激活是否真实"：如实说明"当前为产品概念演示，通行码验证为本地演示逻辑，正式版将服务端原子验证"
- 若被问"更多平台/作品库同步"：说明 v1 API 契约已冻结，正在实现 ANDROID-004/005 数据层

### 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| 处理页提示"请先在我的中连接并配对" | 未配对或后端未启动 | 检查后端窗口；"我的"里连接+配对 |
| 上传报错"文件超过 50MB" | 音频过大 | 换更小的文件 |
| 配对后仍"未连接" | adb reverse 失效（拔线/重启） | 重跑 `demo_adb.bat` |
| 处理失败（PROCESS_FAILED） | 音频损坏或格式不支持 | 换 WAV 文件 |
| 手机息屏后 app 断连 | 正常 | 重新点亮，点"重连" |
| 演示中途想重来 | — | 设置 → 重置演示会话（清激活/作品/配对） |

### 演示素材建议

- 用 `E:\moodify\music\` 下 <50MB 的 WAV（约 24MB，处理约 30-60s），提前拷贝到手机 Download
- 演示前用 `demo_serve.bat` 起服务后，先在电脑端 `curl http://127.0.0.1:8000/api/v1/health` 确认 200
- 轮询频率与 LSM 低配置：2s 间隔足够，避免频繁轮询打满
