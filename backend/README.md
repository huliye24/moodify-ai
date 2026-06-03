# Moodify 后端

## 快速开始

### 1. 安装依赖
```bash
cd backend
go mod tidy
```

### 2. 配置环境变量
编辑 `.env` 文件，填入你的 DeepSeek API Key：
```bash
DEEPSEEK_API_KEY=your-deepseek-api-key
```

### 3. 启动服务器
```bash
go run cmd/server/main.go
```

服务器将运行在 http://localhost:8080

### 4. 启动前端
```bash
cd frontend
npm install
npm run dev
```

前端将运行在 http://localhost:3000

## API 接口

### 项目管理
- `GET /api/v1/projects` - 获取项目列表
- `POST /api/v1/projects` - 创建项目
- `GET /api/v1/projects/:id` - 获取项目详情
- `PUT /api/v1/projects/:id` - 更新项目
- `DELETE /api/v1/projects/:id` - 删除项目

### 歌词生成
- `POST /api/v1/o3ics/generate` - 生成歌词
- `GET /api/v1/o3ics` - 获取歌词列表
- `GET /api/v1/o3ics/:id` - 获取歌词详情
- `PUT /api/v1/o3ics/:id` - 更新歌词
- `DELETE /api/v1/o3ics/:id` - 删除歌词
- `POST /api/v1/o3ics/:id/favorite` - 收藏/取消收藏

### 规则管理
- `GET /api/v1/rules` - 获取规则列表
- `POST /api/v1/rules` - 创建规则
- `GET /api/v1/rules/featured` - 获取精选规则
- `GET /api/v1/rules/:id` - 获取规则详情
- `PUT /api/v1/rules/:id` - 更新规则
- `DELETE /api/v1/rules/:id` - 删除规则
- `POST /api/v1/rules/import` - 导入规则
- `GET /api/v1/rules/export/:id` - 导出规则

### 其他
- `GET /api/v1/options` - 获取生成选项
- `GET /health` - 健康检查

## 技术栈

- Go + Gin 框架
- GORM + SQLite
- DeepSeek API 集成
