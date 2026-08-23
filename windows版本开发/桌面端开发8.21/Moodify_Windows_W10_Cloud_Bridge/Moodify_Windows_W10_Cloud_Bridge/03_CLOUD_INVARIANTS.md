# Cloud Bridge Invariants

## C-01 Verified Reality Only
没有 evidence 的 cloud capability 不能进入 live product path。

## C-02 Cloud Is Not Track Authority
CloudPreparation/PreparedSource 只能映射到 Track。

## C-03 Cloud Is Not Playback Authority
Playback 仍属于 W04。

## C-04 Local Playback Must Survive
云端失败不能让本地播放器失效。

## C-05 Internal Pipeline Hidden
Ear / Stem / Judge / Intervene / Evidence 不进入用户 UI。

## C-06 Client Holds No Infrastructure Secret
service-key、DB credential、第三方 API secret 不得打包进 Windows 客户端。

## C-07 Idempotency Is Mandatory
重复触发不能无限创建云任务。

## C-08 Restart Does Not Resubmit
active preparation 只恢复并刷新，不重新创建。

## C-09 Unknown Status Is Safe
后端返回未知状态时不 crash，也不假装 READY。

## C-10 READY Requires Evidence
只有真实 prepared source 可解析时才能标 READY。

## C-11 Offline Is a First-class State
No Network ≠ No Music。

## C-12 User-facing States Stay Simple
普通用户只看到：未准备 / 正在准备 / 准备完成 / 失败 / 网络不可用。

## C-13 No Automatic Mass Processing by Default
W10 默认不因批量导入自动提交海量云任务。

## C-14 Cloud Source Failure Falls Back
若 local source 仍可用，cloud playback failure 应优先回退 local。

## C-15 No Canon Change
W10 是 Windows 产品实现，不修改公开产品身份。
