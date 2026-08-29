# Recovery Invariants

## R-01 Restore Is Safe
恢复永远先验证，再应用。

## R-02 Restore Is Not Auto Play
重启后默认不自动出声。

## R-03 Durable Data > Session State
Recovery snapshot 损坏不得清空 Library / Playlist 等 durable data。

## R-04 Partial Recovery Is Valid
局部失效不应拖垮全部恢复。

## R-05 Stable IDs Only
Snapshot 保存 Track/QueueItem/Playlist stable IDs，不保存 UI object refs。

## R-06 Current Track May Be Unavailable
Track identity 可恢复，source availability 单独判断。

## R-07 Queue Can Be Repaired
坏 QueueItem 可局部丢弃，合法项继续保留。

## R-08 Position Must Be Clamped
任何非法 position 不得直接写入 engine。

## R-09 Window Must Stay Visible
恢复后的窗口必须位于可见工作区。

## R-10 Versioned State
Recovery snapshot 必须有 schema version。

## R-11 No Silent Global Reset
恢复失败不能默认“清除全部应用数据”。

## R-12 No Runtime Objects
不保存 Promise、callback、DOM、audio engine。

## R-13 Writes Must Be Bounded
不能高频同步写磁盘。

## R-14 Current Playback Authority Remains W04
W08 只恢复 W04 状态，不建立新的 Player authority。
