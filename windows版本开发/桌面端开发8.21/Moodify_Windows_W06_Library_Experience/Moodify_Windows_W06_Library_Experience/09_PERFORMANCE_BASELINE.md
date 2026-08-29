# Library Experience Performance Baseline

## Datasets

```text
100 Tracks
1,000 Tracks
5,000 Tracks
```

允许 synthetic metadata。

## Observe

- first render
- search typing
- sort
- favorite toggle
- view switching
- memory trend
- rerender count if tooling exists

## Rule

没有证据，不提前引入复杂 virtualization / search index。

只有出现明显：
- main-thread blocking
- visible lag
- large DOM
- excessive rerenders

再优化。

输出设备、数据规模、粗略耗时和是否优化。
