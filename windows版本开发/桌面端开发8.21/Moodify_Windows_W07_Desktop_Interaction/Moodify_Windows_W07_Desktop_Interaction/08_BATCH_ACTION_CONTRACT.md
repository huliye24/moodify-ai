# Batch Action Contract

## Input
```text
stable selected IDs
```

## Actions

```text
ADD_TO_PLAYLIST
ADD_TO_QUEUE
FAVORITE
UNFAVORITE
REMOVE_FROM_LIBRARY
```

## Result

推荐 aggregate：

```text
total
succeeded
already_exists
skipped
failed
```

## Partial Failure
默认：
```text
successful items stay successful
failed items report failure
```

除非 existing domain use-case 明确事务性。

## Remove from Library
必须确认。

绝不删除原始文件。

## Clear Selection
批量成功后是否清 selection 必须统一。

推荐：
- collection mutation 后清空
- favorite/queue add 后保留

具体写入实施报告。
