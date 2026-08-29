# 05 — Failure Domain Matrix

**依据：** P00 云扫描 + 黑箱调查（MOODIFY_CLOUD_CURRENT_STATE §20）。P04/P05 指控制面/管线任务包。

| # | Failure | Current behavior | Desired behavior | Data loss risk | Job state risk | Recovery authority | Manual action | P04/P05 must implement |
|---|---|---|---|---|---|---|---|---|
| F-01 | Control/API node down（LA 全部服务） | 官网/平台/API 不可达；worker 队列暂停 | 播放面降级提示；worker 可恢复（recover_interrupted_jobs） | 低（队列近空） | 队列保留在 SQLite；recover 逻辑存在 | 人工 + 24x7 recover | 重启 systemd / 检查 nginx/隧道 | P04（恢复演练） |
| F-02 | Worker down（LA/杭州） | 队列停消费；任务保持 pending | 自动重启（on-failure）+ 幂等恢复 | 低 | pending 任务保留 | 人工 + recover_interrupted_jobs | systemctl restart | P04（恢复演练） |
| F-03 | DB unavailable（PolarDB moodify_dev） | 当前无生产流量 → 影响≈0 | API 返回 503 + 熔断 | 低（数据≈0） | 不涉及（SQLite 承载队列） | 人工（控制台） | 检查 VPC 对等/凭据 | P04（连通性） |
| F-04 | OSS unavailable | 不存在（NOT_PROVISIONED） | 开通后：下载降级 + 重试 | — | — | 人工 | — | P03/P05 |
| F-05 | External stem API unavailable（LALAL.AI/audiolla） | 分离请求失败（无自动 pipeline 调用，影响≈0） | 任务重试/降级（BYPASS 分轨） | 低 | 任务可重试 | 人工 | 检查容器/计费 | P05（重试语义） |
| F-06 | Network partition（LA↔杭州） | BFF 调用杭州失败（未测） | 超时 + 503；本地播放不受影响 | 低 | 不涉及 | 人工 | 检查路由/安全组 | P04 |
| F-07 | Disk full | 未触发过；杭州 40G（23G 可用）、LA 98G（76G 可用） | 告警 + 清理 scratch | 高（媒体不可重建） | 无 | 人工 | 清理 /var/lib/moodify 历史 | P03（对象存储后缓解） |
| F-08 | Job process crash | on-failure 重启 + recover（24x7 验证） | 幂等重试 | 低 | failed 保留（codes+stage） | 人工 + 24x7 | 检查 journald | 已实现（24x7） |
| F-09 | App cannot fetch READY track | 播放失败（URL 直接访问静态） | 限时 URL + 降级提示 | 无 | 无 | 用户侧重试 | — | P06（交付面） |
| F-10 | 隧道/Cloudflare down | 官网/平台公网不可达（同 LA 单点） | 备用入口（DNS 切换） | 无 | 无 | 人工 | 检查 cloudflared/控制台 | P06 |
| F-11 | SQLite 队列文件损坏 | 队列丢失（当前近空，损失小） | 备份 + 恢复 | 低（当前） | 队列丢失 | 人工 | 从备份恢复 | P04（DB-backed 评估） |
| F-12 | 杭州 swap 耗尽（OOM） | pilot 期 0 OOM（swap ~1GiB 驻留） | 并发=1 保持 + 资源守卫 | 低 | 任务失败可重试 | 人工 + resource-probe timer | 检查 memory | P08（3-song pilot 前） |

## 汇总

- **最大单点：** LA（F-01/F-10）——官网、平台、API、worker、audiolla 同机。
- **最高数据风险：** 磁盘满导致媒体丢失（F-07）——媒体文件不可重建。
- **当前影响面最小的失败：** DB（F-03）与外部分离 API（F-05）——因为无生产流量/无自动调用。
- **人工动作要求最多的恢复路径：** 全部涉及人工判断（无自动化恢复系统）——记录，不实施。
