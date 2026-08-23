# Single Instance & Open File Contract

## Primary Instance

只有一个长期 Moodify 实例持有共享 persistence。

## Secondary Instance

```text
Invocation
→ parse structured args
→ handoff to primary
→ activate primary only for explicit user action
→ exit
```

推荐 payload：

```text
{
  kind: "activate" | "open_files",
  files: [...]
}
```

## Open One File

```text
OS/Open With
→ validate
→ W02 import/resolve
→ Track
→ W05 minimal Queue/context
→ W04 Play
```

## Open Multiple Files

```text
preserve argument order
→ import valid Tracks
→ Queue same order
→ play first valid
```

一个坏文件不能让整批失败。

## Duplicate

已有 Track 时解析 canonical Track，不创建重复 Track。

## Folder

W09 不默认递归扫描目录。只有 W02/W07 已明确支持目录导入才复用。
