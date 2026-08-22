# MFD-005 Visual System Baseline

## Design principle

> 少，即是产品的一部分。

---

## Typography

优先系统字体或已有品牌字体策略。

不要为 Alpha 引入复杂字体打包问题。

层级：

```text
Brand
Track title
Artist
Status
```

不要超过太多字号层级。

---

## Spacing

建立统一 spacing scale。

不要每个组件手写随机 margin。

---

## Motion

只允许：

- vinyl rotation
- subtle fade
- subtle loading transition

避免：

- bounce
- flashy gradients
- particle
- music visualizer
- constant moving UI

---

## Disc

建议：

- geometric
- neutral
- minimal
- no fake cover requirement

如果没有封面：

> 不要为了填空而使用随机图片。

---

## Theme Tokens

至少：

```text
background
foreground
muted
border
surface
focus
spacing
radius
motion
```

不要把 token 系统升级成皮肤引擎。
