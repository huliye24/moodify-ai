# 04 — Data Assets / External Capability Reality

**扫描时间：** 2026-08-17 20:05–20:15 CST（本地文件系统只读统计）

---

## A. 音频与 Evidence

### 真实歌曲与音频分布

| 目录 | 音频文件数 | 大小 | 性质 |
|---|---|---|---|
| pre-music/ | 173 | 7.8 GB | 真实曲目库（法语独立音乐）+ lalalai 分轨 + 处理产物 |
| 07Music/ | 110 | 1.6 GB | 音乐素材（播放库候选） |
| outputs/ | 159 | 3.7 GB | 处理产物（data_factory cases、CAD、calib、daily_runs、cloud_results） |
| output/ | 31 | 1.5 GB | 处理产物 |
| music/ | 44 | 753 MB | 音乐文件 |
| listening_test/ | 34 | 924 MB | 聆听测试音频 |
| local_audio_assets/ | 11 | 222 MB | 本地音频资产 |
| data/ | 7 | 180 MB | 数据目录 |
| uploads/ | 4 | 132 MB | 上传文件 |
| artifacts/ | 258 | 765 MB | 证据音频（案例、golden、测试） |
| deliverables/ | 0 音频 | 150 MB | 仅 APK/manifest |
| shared-fixtures/ | 0 | 2 KB | 引用关系（git-lfs 或 symlink 式） |

**合计：~790 个音频文件，~17 GB**（含处理产物与证据，非全部为"真实歌曲"）。

### 真实歌曲（owned tracks，pre-music）

1. Des portes et des lampes (1).wav
2. J'apprends à te recevoir maladroitement.wav
3. Viens chez moi (1).wav
4. Ne vivons pas seulement de souvenirs/（目录，含多次 lalalai split zip）
5. Nous pouvons nous reconnaître encore/（目录）
6. Où es-tu maintenant/（目录）
7. Vieillir et devenir nouveau avec toi/（目录）

- **唯一 track identity：** 无全库统一 track-hash 注册表；仅 golden case 有 `source_manifest.json`（源哈希）+ 黑箱调查中 5 文件 music-media（LA）。
- **Analyze/Process 状态：** pre-music 每曲有多次 lalalai 分轨尝试（2026-07-24 ~ 08-02 zip）；outputs/data_factory/cases 有 4 个 case（+cases.jsonl + pairwise_preferences.jsonl + dataset_summary.json）；CAD 案例 01_CAD-MFY-001-FR（spectrum png + warm_vocal wav）；calib_clean_master/warm_vocal/wide_space 预设产物。
- **Before/after：** outputs 中 CAD/calib 体系存在前后对比产物；无统一对比契约（REPOSITORY_STATUS.md 曾声明 EXPERIMENTAL）。
- **人耳评价：** 无真人盲评数据（用户已拍板算法化评审，人工评审一律 PENDING_HUMAN/SKIPPED_PER_USER）。listening_test/（34 文件）存在但结果 DATA_PENDING。
- **Golden Case 候选：** moodify-core-package/golden_run_out（golden_record.json、source_manifest.json、blind_mapping.json、era_diagnostic.v0.1.json、candidates/、listening/）+ era_cli_out。重建 P06/P07 使用的 owned 219s 曲目（ne-vivons / Vieillir）为当前实际 golden 候选（PROMISING_NOT_GOLDEN，未定案）。
- **重复/孤立产物：** 无法追溯来源的 output 存在（outputs/、temp/、tmp/ 大量历史产物，未见来源索引）；lalalai split 多次重试产生重复 zip（同曲 5-7 次）。

### Evidence 资产（artifacts/）

59 个子目录，绝大多数含 FINAL_RESPONSE.md / execution_record / TEST_RESULTS：
- 重建系列 mfy_classic_reconstruction_p01..p07
- MAMSE-001..016（001-012 完整；013-016 仅结构）
- 移动端 6 包（audio_path/device_aware/dsp/mobile_listening/one_play/preserve_identity）+ android_baseline
- 数据管线 mfy_24x7、失败注入、算法评审、phase1_launch（EVIDENCE_INDEX+GO_NO_GO+独立验证）、pilot、web_origin、ocean_bridge、aliyun_node、g4_04、g6_03、audiolla_cloud_deploy、pr15_extraction、ear_pilot 等

**隐私：** 本报告不含任何私人音频内容；曲名仅为目录级元数据。

---

## B. 外部能力（唯一状态分类）

| 能力 | 状态 | 代码集成 | 运行时证据 | 备注 |
|---|---|---|---|---|
| LALAL.AI | CONNECTED_UNTESTED | stems 模块（72c47c4d）+ audiolla 代理 | audiolla 容器部署 LA（健康，Up 24h+），**无自动 pipeline 调用** | 模型在 lalal 云端，本地无推理 |
| Audiolla（psyb0t/audiolla） | CONNECTED_UNTESTED | /srv/moodify/audiolla | 容器 running healthy | 唯一部署的「听/分离」外部能力 |
| FFmpeg | PRODUCTION_USED | 部署工具链 | 杭州 8.0.1 + LA 4.4.2（存在，活跃任务无证据） | winget 路径本地也有 |
| Demucs | UNAVAILABLE | 仓库引用 | 无（权重未下载） | 记忆：bsroformer/demucs 权重下载待办 |
| Basic Pitch | EXPERIMENTAL | 仓库工具 + LA capabilities 目录 | 无运行进程证据 | 工具代码存在 |
| Matchering | EXPERIMENTAL（未接入） | 仅讨论/代码 | 无 | — |
| 现有 DSP/processing chain | EXPERIMENTAL→CURRENT 混合 | v01_pipeline（canonical）+ pedalboard_chain + intervention primitives（分支） | 数据工厂批处理（杭州 pilot） | 干预原语 3 个（71 包）未编译进播放链 |
| Android playback | PRODUCTION_USED（本地） | apps/music-android 3.1 + Media3 | 设备测试 7/7（68 包）、真机长时播放（73 包） | 云端 URL 播放可用 |
| cloud API | DEPLOYED_NOT_VERIFIED | moodify.api + music BFF | LA:8000/3100/8100 + 杭州:8000 health OK | 无生产业务流量 |
| PolarDB | DEPLOYED_NOT_VERIFIED（schema-only） | moodify-music-package（alembic） | moodify_dev 19 表 ≈0 数据 | 凭据核验 BLOCKED |
| OSS | UNAVAILABLE（NOT_PROVISIONED） | 无 | 无 | W01-P03 计划中 |
| Cloudflare（DNS+隧道） | PRODUCTION_USED | cloudflared | LA 隧道运行 | 免费计划 |

## 回答任务书问题

- 真实歌曲总数：**可访问范围约 7 首（pre-music）+ 播放库若干（07Music/music/local_audio_assets 未去重统计）**；黑箱调查云端 5 文件。
- 音频文件在哪里：本地 pre-music/07Music/music/local_audio_assets + outputs（产物）+ artifacts（证据）；云端 LA music-media、杭州 /var/lib/moodify。
- 已 analyze/stem/process：lalalai 分轨（多次尝试）；data_factory 4 case + 10 曲 pilot（杭州）；CAD/calib 产物。
- 有 before/after：outputs CAD/calib 体系（无统一契约）。
- 有人耳评价：无（算法化评审替代）。
- 完整 Evidence：artifacts 59 目录 + golden_run_out + 各包 TEST_RESULTS。
- Golden Case 候选：ne-vivons / Vieillir（重建 golden，PROMISING_NOT_GOLDEN）。
- 重复/孤立：lalalai 多次重试 zip + outputs/temp/tmp 历史产物无来源索引 → 存在。
