# PRODUCTION_VS_GIT_DIFF.md — MFY-INFRA-FOUNDATION-001 Phase B2

比较对象：
- **LA 生产**：`/opt/moodify/music/current`（release `20260813T050100Z`，38 个源码/配置文件，manifest 见 `la_music_manifest.sha256`）
- **Git 对照**：本地仓库 `apps/music-web/`（当前分支 `codex/music-platform-listening-first` @ 71428a1）

方法：排除 node_modules/.next/dist/.wrangler/.sites-runtime/.openai 后的递归 diff + 逐文件内容对比。

## 差异分类

### production-only（LA 有，Git 无）
| 文件 | 说明 | 处置 |
|---|---|---|
| `CODEX_HANDOFF.md` | Codex 交接文档（1.3KB） | 已导入 baseline |

### git-only（Git 有，LA 无）
| 文件 | 说明 | 处置 |
|---|---|---|
| `AUDIT.md` | 本地新增审计文档 | 不导入 baseline（本地工作分支保留） |
| `assets/cadeau10-album1.json` | 音频 SHA256 manifest（本地新版引入的发布资产机制） | 复制进 baseline 作为音频记录 |
| `public/audio/cadeau10-album1/*.wav` | 5 个 wav（LA 生产同样存在；LA 侧单独 sha256 验证中） | 二进制不进 git（storagePolicy 明确），由 manifest 记录哈希 |

### modified（内容不同，功能等价）
| 文件 | 差异 | 影响 |
|---|---|---|
| `app/page.tsx` | LA 用相对路径 `/audio/...`；Git 用 `albumAudio()` + `NEXT_PUBLIC_AUDIO_BASE_URL`（默认 https://rongjinwenchuan.xyz/audio） | 无：两者解析到同一媒体源。Git 版为超集（支持自定义媒体源） |
| `app/layout.tsx` | Git 版多 `other: {"codex-preview":"development"}` meta | 无：开发标记 |
| `README.md` | LA 为 vinext-starter 默认 README；Git 为 Moodify Music 介绍（含黑胶视觉文案、音频资产策略） | 无：文档差异。baseline 保持 LA 原样 |

### generated（两边均排除）
node_modules / .next / dist / .wrangler / .sites-runtime / .openai（hosting.json 为 d1/r2 null 空配置）

### secret/config
`.npmrc`（audit=false/fund=false/cache=.sites-runtime/npm-cache，无任何 token）→ 无风险，保留
源码敏感扫描（ghp_/gho_/sk-/AKIA/LTAI/password/secret/token）：**零命中**

### unknown
无。

## 结论

LA 生产与 Git `apps/music-web/` 结构一致（38 vs 39 文件），仅 3 个文件内容差异且**全部功能等价**。LA 生产 = Git 版的无环境变量简化版。baseline 回收采用 LA 生产原样（source of truth）+ 音频 manifest。
