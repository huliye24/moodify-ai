# Site Roles and Routing Specification

## 1. 最终结构

```text
rongjingwenchuan.com
荣景文川 / Company
        |
        | 主要作品
        v
rongjingmusic.com
Moodify / Product Home
        |
        | Play
        v
play.rongjingmusic.com
Moodify Web Player
```

过渡期：

```text
rongjinwenchuan.xyz
        |
        +--> Web Player（暂存）
        |
        +--> 明确返回 rongjingmusic.com
```

---

## 2. `rongjingmusic.com`

### 必须承担

- Moodify 的品牌第一解释权。
- Hero 品牌信念。
- 试听 / Demo / Play。
- Android / iOS（未来）下载。
- 少量证明。
- Company 链接。

### 不承担

- 完整开发者文档。
- API 控制台。
- 公司历史长文。
- Creator 后台。
- 完整 Research 索引。
- 多产品门户。

### 推荐主导航

`Moodify | Listen | Download | About`

其中 About 可进入公司站或轻量产品说明。

---

## 3. `rongjingwenchuan.com`

### 必须承担

- 荣景文川公司身份。
- 公司理念。
- Moodify 作为主要公开作品。
- Research 入口。
- Contact。

### 不承担

- 把 Moodify 再定义成 API 公司。
- 让 Developers 成为第一 CTA。
- 让 ACU 成为公司商业身份。

### 推荐主导航

`Company | Moodify | Research | Contact`

---

## 4. `rongjinwenchuan.xyz`

### 过渡期

只做：

- 进入播放器。
- 当前曲目。
- Play / Pause。
- 切歌。
- 极少量必要账户/库功能。
- Moodify Logo 返回主官网。

### 应隐藏或延后

- Creator Center
- 授权意向
- 上传作品
- 大型发现平台
- 复杂社区
- 与当前 Play 无关的实验功能

具体删除/隐藏清单必须由 Codex 通过仓库确认后再执行。

---

## 5. 域名原则

### Canonical

- Product: `https://rongjingmusic.com/`
- Company: `https://rongjingwenchuan.com/`
- Player target: `https://play.rongjingmusic.com/`

### 过渡域名

- `https://rongjinwenchuan.xyz/`

注意：`.xyz` 域名的拼写与 `rongjingwenchuan` 不同，长期容易制造品牌记忆损耗。

因此建议：

1. 不再为 `.xyz` 建立新的长期品牌资产。
2. 新的 Web Player 优先迁移到 `play.rongjingmusic.com`。
3. 迁移完成后再根据真实技术条件决定 301、302 或保留提示页。

---

## 6. 跨站 Footer 统一

所有公开站至少共享：

- `Moodify`
- `荣景文川`
- Product / Company 正确互链
- Privacy
- Contact
- Copyright
- 统一年份格式
- 不出现相互冲突的产品定义

---

## 7. SEO / OG 原则

### Product Home

Title 应围绕：

`Moodify - Listen. Then Play.`

Description 围绕：

`Every voice deserves to be heard.` + 简短产品事实。

### Company Home

Title：

`荣景文川 - Rongjing Wenchuan`

Description：

公司 + Moodify + research，不用 API infrastructure 抢第一句。

### Player

Title：

`Moodify - Play`

Description 只需说明正在进入 Moodify listening experience。

---

## 8. 迁移验收

任何跨站跳转完成后：

- 无死链。
- Logo 回到正确层级。
- Browser back 不造成循环。
- Canonical URL 正确。
- OG 卡片不再出现旧身份。
- 搜索引擎不同时得到三种 Moodify 定义。
