# BASELINE_EQUIVALENCE_REPORT.md — MFY-INFRA-FOUNDATION-001 Phase B5

## 等价性声明

```
Recovered Git baseline（apps/music-web-baseline @ 3180703）
≈
LA production（/opt/moodify/music/releases/20260813T050100Z）
```

## 验证矩阵

| 验证项 | 方法 | 结果 |
|---|---|---|
| 文件清单 | LA `la_music_tree.txt`（38 项）vs baseline 34 项 | 一致（34 = 38 − 5 音频 + 1 assets manifest） |
| 逐文件内容 | source-only tar 解包与 baseline 目录逐字节比较 | 一致（diff -rq 无差异，仅排除目录） |
| SHA-256 | LA `la_music_manifest.sha256`（38 项）已生成并拉回本地 | 保存于 artifacts/baseline/ |
| 音频资产 | LA 5×wav sha256sum vs `assets/cadeau10-album1.json` | **5/5 完全一致** |
| 敏感扫描 | ghp_/gho_/sk-/AKIA/LTAI/password/secret/token 扫描 | 零命中 |
| Git 版本 | 分支 `codex/moodify-production-baseline-20260813`，commit 3180703f，基于 main 0b355e7 | 已推送，Draft PR #1 |

## 允许差异（任务定义范围内）

| 差异 | 类型 | 说明 |
|---|---|---|
| public/audio/*.wav（5 文件 255MB） | 部署资产 | 不进 git；manifest 记录 SHA-256 与字节数 |
| node_modules/.next/dist/.wrangler/.sites-runtime/.openai | 生成物/运行环境 | 两边均排除（excluded_files.txt） |
| runtime config | 环境变量 | 不涉及（无 secret 文件） |

## 等价性结论

Git baseline 与 LA 当前线上源代码**一致**（源码逐字节），音频资产哈希一致，差异仅为任务允许的部署资产与生成物。满足成功标准 2。
