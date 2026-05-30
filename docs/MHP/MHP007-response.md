# MHP-007 回传单：ChatGPT 确认 MHP-006-C

> 日期：2026-05-30
> 结论：进入 MHP-006-C。只改 Limiter ceiling，不改 preset、不新增 P16。

---

## MHP-006-C：pedalboard_chain.py Limiter ceiling

```python
# Before
board.append(pedalboard.Limiter())

# After
board.append(pedalboard.Limiter(threshold_db=-1.0))
```

## 预期
peak 从 -0.0 降到 ~-1.0 dBFS，crest 回升。

## 不改
v01_presets / v01_exporter / v01_pipeline / tests / P16
