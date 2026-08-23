# Track / Library Invariants

这些 invariant 是 W02 的核心验收，不绑定具体实现技术。

## I-01 Unique Authority

同一运行时只存在一个业务意义上的 Track authority 和一个 Library authority。

## I-02 Stable Identity

Track 的业务 identity 不随：

- UI route
- component mount
- title change
- metadata fallback
- temporary player state

而变化。

## I-03 Path Is Source, Not Display Identity

Windows 路径是 source locator，不等于歌曲标题，也不应直接泄漏为 UI identity。

## I-04 Duplicate Import Is Idempotent

重复执行相同导入操作，不应无限增加相同 Track。

```text
import(x)
import(x)
→ one canonical Track reference
```

除非 W01 证明当前产品明确允许 duplicate membership；即便如此 Track authority 仍不能无限复制。

## I-05 Same Name Can Coexist

```text
C:\A\song.wav
D:\B\song.wav
```

可以是两个不同 Track。

## I-06 Missing Source Preserves Identity

```text
Track exists
source disappears
→ Track remains identifiable
```

是否提供 relink UX 留到后续，但 relation 不能默认销毁。

## I-07 Remove Is Non-destructive

```text
Remove from Library
```

默认只改变 Moodify 内部引用，不删除用户原始文件。

## I-08 Restart Persistence

重启是 W02 的硬边界。

只在内存里“看起来成功”不算完成。

## I-09 Player Consumes Track

Player 通过 Track / source resolver 获取播放源。

禁止：

```text
file picker result
→ private player state
```

绕过 Library。

## I-10 Future Cloud Compatibility

W02 不实现 CloudTrack，但本地 Track 设计不能把未来云端加入逼成全量重构。

至少概念上要保留：

```text
source_kind
source_ref
```

或等价边界。

## I-11 No Canon Leakage

Library 数据层不得引入：

- Ear public state
- stem UI
- evidence UI
- DSP control panel

## I-12 No Hidden Data Loss

migration、dedupe、remove、invalid-source cleanup 任何动作都不能静默删除无法恢复的数据。
