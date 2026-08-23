# Windows Explorer Integration

## Goal

对本地 Track 提供：

```text
在资源管理器中显示
```

## Conditions

必须：

- Track is LOCAL
- source resolver can resolve
- source exists or clear failure
- runtime provides safe native reveal API

## Forbidden

```text
cmd.exe /c explorer ...
```

配合未经严格 escaping 的字符串拼接。

也禁止：

- arbitrary shell execution
- renderer arbitrary filesystem browsing

## If Unsupported

记录：

```text
REVEAL_IN_EXPLORER = BLOCKED_FOR_W09
```

不要为完成 W07 而破坏安全边界。
