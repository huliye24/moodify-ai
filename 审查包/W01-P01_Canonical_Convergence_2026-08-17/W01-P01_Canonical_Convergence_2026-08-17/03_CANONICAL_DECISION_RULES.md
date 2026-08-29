# Canonical Decision Rules

## R1 — Human product direction outranks old product prose

当前显式人类方向优先于旧 README、旧 AGENTS、旧产品文档。

但人类方向不能伪造运行事实。

---

## R2 — Runtime evidence outranks docs for “what exists”

如果文档说部署了，但 P00 没有 runtime evidence：

不能写成“已经运行”。

只能写：

`implemented / planned / deployment unknown`

---

## R3 — One external product identity

高权威文档不得同时存在两个并列的对外一级产品身份。

当前目标：

`Moodify Music / Player`

Ear / Auditory Intelligence：

`INTERNAL`

---

## R4 — Preserve assets, reduce authority

旧系统如果有工程价值：

- 不自动删除
- 不因为产品定位变化而否定代码价值
- 先改变 authority / classification

---

## R5 — No duplicate canon

禁止为了“新版本”增加：

- `AGENTS_NEW.md`
- `README_V2.md`
- 第二个 Current Architecture
- 第二个 Product Constitution

除非旧文件无法兼容且有明确迁移计划。

默认优先：

> 更新现有最高权威入口 + 建立单一 `docs/canon/`

---

## R6 — Current reality and target canon are different documents

P00：

`Current Reality`

P01：

`Current Canon / Target Authority`

不要混合。

---

## R7 — Canon change must be visible

所有产品身份、authority order、内部/外部边界变化必须进入：

`CANON_CHANGELOG.md`

---

## R8 — Historical documents cannot self-promote

任何 LEGACY / HISTORICAL 文档都不得通过自身文字把自己提升回 Canon。

---

## R9 — Minimize cognitive surface

Canon 文档数量越少越好。

每一份 Canon 文件都必须回答：

> 它永久消灭了哪类未来重复理解？

若无法回答，不新增。

---

## R10 — Canon is not a feature roadmap

不要把未来规划、商业想象、未验证云端能力塞入 Canon。

Canon 只固定：

- identity
- boundary
- authority
- invariants
- current architectural roles
