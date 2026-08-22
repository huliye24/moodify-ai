# Search & Sort Contract

## Search Fields

```text
title
artist
album
```

可选 filename fallback，但 raw path 不作为主要展示。

## Search Requirements

- trim
- Unicode safe
- Chinese safe
- null safe
- partial match
- case normalization where valid
- rapid typing stable

不做 semantic / embedding / AI search。

## Sort Keys

推荐：

```text
title
artist
added_at
duration
```

## Tie-break

必须稳定，例如：

```text
primary key
→ title
→ track_id
```

## Pipeline

```text
Authority
→ Base View
→ Search
→ Sort
→ Render
```

不写回 authority。
