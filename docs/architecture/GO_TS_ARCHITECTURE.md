# Moodify 架构设计方案

> 设计日期：2026-04-12
> 架构：Go 后端 + TypeScript 前端

---

## 一、设计目标

### 解决的核心问题

| 问题 | 现状 | 目标 |
|------|------|------|
| 后端分散 | Flask、Streamlit 各自独立 | 统一 Go 后端 |
| API 调用分散 | React 直接调用 DeepSeek | 后端代理 |
| 规则无法共享 | 两套规则不互通 | 统一规则引擎 |
| 数据存储混乱 | SQLite + LocalStorage | PostgreSQL 统一存储 |

---

## 二、技术栈

### 后端（Go）
- 框架：Gin
- ORM：GORM
- 认证：JWT
- 配置：Viper
- 日志：Zap

### 前端（TypeScript）
- 框架：Next.js 14
- UI：TailwindCSS + shadcn/ui
- 状态：Zustand + TanStack Query
- 类型：TypeScript strict

### 基础设施
- 数据库：PostgreSQL + Redis
- 容器：Docker

---

## 三、数据模型

### ER 图
```
用户 (User)
  ├── 虚拟人物 (Character) [1:N]
  │     ├── 情绪历史 (MoodEntry)
  │     └── 生成历史 (GenerationEntry)
  ├── 项目 (Project) [1:N]
  │     └── 歌词 (Lyrics)
  ├── 规则 (Rule) [1:N]
  └── 音乐 (MusicTrack) [1:N]
```

---

## 四、API 接口设计

### 4.1 认证模块
- POST /api/v1/auth/register - 注册
- POST /api/v1/auth/login - 登录

### 4.2 人物模块
- GET /api/v1/characters - 列表
- POST /api/v1/characters - 创建
- GET /api/v1/characters/:id - 详情
- PUT /api/v1/characters/:id - 更新
- DELETE /api/v1/characters/:id - 删除

### 4.3 歌词生成模块（核心）
```json
POST /api/v1/o3ics/generate
Request: {
    "content": "用户文案",
    "character_id": "uuid（可选）",
    "params": {
        "emotion": "悲伤",
        "theme": "爱情",
        "style": "民谣",
        "rhyme": "AABB",
        "length": "medium"
    },
    "use_rules": true,
    "use_dice": true
}

Response: {
    "o3ics": "生成的歌词...",
    "suno_prompts": ["prompt1", "prompt2", "prompt3"],
    "dice_result": { "closing_style": "...", "turning_point": "..." }
}
```

### 4.4 规则引擎模块
- GET /api/v1/rules - 列表
- POST /api/v1/rules - 创建
- GET /api/v1/rules/featured - 精选
- POST /api/v1/rules/import - 导入
- GET /api/v1/rules/export/:id - 导出

### 4.5 音乐生成模块（Suno）
- POST /api/v1/music/submit - 提交任务
- GET /api/v1/music/status/:task_id - 查询状态
- GET /api/v1/music/tracks - 音乐列表

---

## 五、项目结构

### Go 后端 (backend/)
```
backend/
├── cmd/server/main.go
├── internal/
│   ├── config/
│   ├── handler/     # 路由处理
│   ├── middleware/  # 中间件
│   ├── model/       # 数据模型
│   ├── repository/  # 数据层
│   ├── service/     # 业务逻辑
│   └── pkg/         # 工具包
├── migrations/
└── Dockerfile
```

### TypeScript 前端 (frontend/)
```
frontend/
├── src/
│   ├── app/         # Next.js App Router
│   ├── components/  # React 组件
│   ├── hooks/       # 自定义 Hooks
│   ├── lib/         # 工具库
│   ├── store/       # Zustand
│   └── types/       # 类型定义
├── Dockerfile
└── package.json
```

---

## 六、实施计划

### Phase 1: 基础骨架（第 1-2 周）
- 搭建 Go 项目结构
- 实现用户认证 API
- 搭建 Next.js 项目
- 实现登录/注册页面

### Phase 2: 歌词生成（第 3-4 周）
- 实现歌词生成 API（DeepSeek）
- 实现规则引擎 API
- 实现歌词生成界面
- 实现摇色子功能

### Phase 3: 播放器 + 完善（第 5-6 周）
- 情绪播放器 Web 版
- 规则导入/导出
- Suno API 集成
- 全流程测试

---

## 七、核心代码示例

### 统一响应
```go
type Response struct {
    Code    int         `json:"code"`
    Message string      `json:"message"`
    Data    interface{} `json:"data,omitempty"`
}

func Success(c *gin.Context, data interface{}) {
    c.JSON(200, Response{Code: 0, Message: "success", Data: data})
}
```

### API 客户端
```typescript
// src/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1'

async function request<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    const token = localStorage.getItem('token')
    const headers: Record<string, string> = { 'Content-Type': 'application/json' }
    if (token) headers['Authorization'] = `Bearer ${token}`
    
    const response = await fetch(`${API_BASE}${endpoint}`, {
        method: options?.method || 'GET',
        headers,
        body: options?.body ? JSON.stringify(options.body) : undefined,
    })
    
    const data = await response.json()
    if (data.code !== 0) throw new Error(data.message)
    return data.data
}

export const api = {
    auth: {
        login: (email: string, password: string) =>
            request('/auth/login', { method: 'POST', body: { email, password } }),
    },
    o3ics: {
        generate: (data: GenerateRequest) =>
            request('/o3ics/generate', { method: 'POST', body: data }),
    },
    rules: {
        list: (params?: { type?: string }) => request('/rules', { params }),
    },
}
```

---

## 八、环境变量

### 后端 (.env)
```bash
DATABASE_URL=postgres://user:password@localhost:5432/moodify
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
DEEPSEEK_API_KEY=your-deepseek-api-key
PORT=8080
```

### 前端 (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8080/api/v1
```

---

## 九、待确认

1. Suno API BASE_URL 和认证方式
2. 是否需要强制登录
3. 部署方案选择
4. 数据迁移需求

---

*最后更新：2026-04-12*
