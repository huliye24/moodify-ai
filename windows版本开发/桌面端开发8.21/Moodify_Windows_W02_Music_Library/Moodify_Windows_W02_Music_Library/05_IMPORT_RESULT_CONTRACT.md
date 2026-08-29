# Import Result Contract

W02 的导入行为应有稳定的内部结果，而不是只靠 toast 文案判断。

推荐语义：

```text
IMPORTED
ALREADY_EXISTS
UNSUPPORTED
INVALID
FAILED
```

字段名可适配现有代码。

## IMPORTED

Track 成功建立/恢复并进入 Library。

## ALREADY_EXISTS

同一 canonical source 已在 Library 中。

这个结果不应作为错误。

## UNSUPPORTED

文件类型或 decode capability 明确不支持。

## INVALID

文件看起来像音乐，但不可有效读取 / probe / decode。

## FAILED

I/O、权限、unexpected internal failure。

FAILED 需要有内部 error evidence，但 UI 不应泄漏完整 stack trace。

## Batch Import

多文件导入时返回 aggregate：

```text
total
imported
already_exists
unsupported
invalid
failed
```

一个坏文件不得默认让整批回滚，除非当前 persistence 设计明确要求事务性 batch。
