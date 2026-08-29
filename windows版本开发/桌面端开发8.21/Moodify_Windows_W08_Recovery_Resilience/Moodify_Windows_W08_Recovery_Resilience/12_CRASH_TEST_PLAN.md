# Crash / Abnormal Exit Test Plan

## C-01 Kill Process After Snapshot

正常 checkpoint 后强制 kill。

重启应恢复最近有效 snapshot。

## C-02 Kill During Write

尽可能模拟写到一半。

要求 canonical snapshot 仍可读取，或 fallback to LKG。

## C-03 Renderer Crash

如果 runtime 支持 renderer/main 分离：
模拟 renderer crash，验证 persistence authority 不损坏。

## C-04 Corrupted File

手工截断 snapshot。

重启不能 crash loop。

## C-05 Invalid Queue

插入坏 QueueItem。

只修坏项，不丢整个 Queue。

## C-06 Missing Track Source

关机前有效，重启前删除文件。

Track/Queue identity 保留，source unavailable。

## C-07 Monitor Change

保存副屏窗口位置，移除副屏后启动。

窗口必须可见。
