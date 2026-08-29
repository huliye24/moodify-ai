# Cloud Product E2E — 执行清单与脚本

**Document ID:** MFY-CLOUD-E2E-001
**Version:** 1.0
**Date:** 2026-08-14
**Package:** MFY_CLOUD_PRODUCT_E2E_001 (60)
**Status:** 清单生效；真机执行需部署授权（从用户入口开始，不得绕过 nginx）

## 1. 执行原则

- 测试必须从用户入口开始（https:// 域名），不得直接调用 localhost 冒充生产通过；
- 使用 56 定义的验证数据集（合成 fixture + 公开 Music + 专用测试账号；禁止私人数据）；
- 每场景记录：入口 URL、请求序列、状态码/断言、证据截图或日志摘要。

## 2. 场景清单（真机执行模板）

### 官网
| 场景 | 断言 | 本地证据（46 包） |
|---|---|---|
| 七路由可达 + 无 404 | 全 200 | check_site 6/6 |
| CTA 指向真实路由 | href 解析 | check_site |
| claim 成熟度标签 | maturity 类名 | check_site |
| 404 页降级 | nginx 404 页非 500 | 待真机 |
| 移动宽度渲染 | 390 截图 | 46 截图 |

### Ear
| 场景 | 断言 | 本地证据 |
|---|---|---|
| 上传→Job→Case→Result→Evidence | 47 真实链路（job_4b85…） | ✓ 本地全链路 |
| HUMAN_REQUIRED 创建→队列→决定 | 48 API + reviews 页 | 15 测试 |
| INCONCLUSIVE / FAILED | 48 终态 | 15 测试 |
| worker 中断/恢复 | 48 幂等 resume | 既有 |
| manifest/hash + no-store | 47 证据 | ✓ |
| 工作台从公网可达 | https://rongjingmusic.com/ear 工作台 | 待部署（60/65） |

### Music Listener
| 场景 | 断言 | 本地证据 |
|---|---|---|
| anonymous discover/play/Range/seek | Range 206 矩阵 5/5 | ✓ 线上已验 |
| media 404/5xx 恢复 | onError 横幅 | 49 检查 |
| login/favorite/follow/library | 51 会话 + 49 幂等 | ✓ |
| Track/Creator/default cover | 页面元素 | 49 截图 |
| 无 Ear 公开评分 | 静态检查 | ✓ |

### Creator
| 场景 | 断言 | 本地证据 |
|---|---|---|
| profile→upload→draft→version→Passport→preview→publish | 50 全流程测试 | ✓ |
| 中断恢复（各点） | 50 恢复测试 | ✓ |
| publish response lost | 50 读权威状态 | ✓ |
| 幂等同/异 payload | 50/51 测试 | ✓ |
| owner/IDOR | 50 越权 403 | ✓ |
| public Track Range | 49 矩阵 | ✓ |

### Bridge
| 场景 | 断言 | 本地证据 |
|---|---|---|
| owner request→evidence_ready→human_reviewed→attach | 52 happy path | ✓ |
| failed/inconclusive 不改发布 | 52 终态 | ✓ |
| detach 保留审计 | 52 | ✓ |

## 3. 执行顺序（真机，待授权）

```text
1. 部署 46 官网静态站（deploy_static_origins.sh）
2. 部署 47 工作台（nginx 同源代理）
3. Ear API/worker 上线（deploy_moodify_service.sh）
4. BFF/杭州/PolarDB 数据面（58 完成后）
5. 按 §2 逐场景执行 + 截图/日志证据
6. 记录到 artifacts/phase1_launch/e2e_cloud_001/
```

## 4. 事实边界

- 本地代理链 E2E 已验（47 真实案例全链路 + 49 线上 Range）；
- 公网用户入口 E2E 待部署授权（部署脚本已备且语法验证过，57 包）；
- 任一场景失败 → 记录归包 → 修复后重跑受影响门（63 独立验证同样适用）。
