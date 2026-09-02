# 🐰 云上大耳兔 · 智慧康复平台 v3.0

> 从聆听开始的治愈陪伴 — AI康复智能体统一 Web 应用

## 📋 项目简介

**ut2ai.com** 是一个基于 FastAPI 构建的智慧康复医学平台，集成了：
- ✅ 用户注册/登录认证系统
- ✅ 智慧知识库管理（文本上传、搜索、文档列表）
- ✅ AI康复助手对话（RAG检索增强生成）
- ✅ 品牌着陆页 + 完整前端 UI

---

## 🚀 快速开始

### 1. 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py

# 访问 http://localhost:5000
```

### 2. Railway 部署

Railway 会自动检测 FastAPI + uvicorn 配置。

#### 环境变量设置（Railway Dashboard → Variables）：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `PORT` | `5000` | 服务端口 |
| `QDRANT_URL` | `http://127.0.0.1:6333` | Qdrant向量数据库（可选）|
| `OLLAMA_BASE_URL` | `http://127.0.0.1:8081` | 本地 LLM 服务（可选）|
| `LLM_MODEL` | `qwen2.5` | 使用的模型名称 |

#### Dockerfile（Railway 自动检测，也可手动添加）：

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
```

---

## 📁 项目结构

```
workspace/
├── main.py                  # FastAPI 主应用（入口）
├── requirements.txt         # Python 依赖
├── Procfile                 # Railway 进程配置
├── .gitignore               # Git 忽略文件
└── frontend/                # 前端页面
    ├── landing.html          # 品牌着陆页 (/)
    ├── auth.html             # 登录注册页 (/login)
    ├── knowledge.html        # 知识库管理页 (/dashboard)
    └── chat.html             # AI对话页 (/chat)
```

---

## 🔌 API 接口文档

### 认证模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| POST | `/api/auth/logout` | 用户登出 |
| GET | `/api/auth/me?token={token}` | 获取当前用户信息 |

### 知识库模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/knowledge/upload-text` | 上传文本到知识库 |
| POST | `/api/knowledge/upload-file` | 上传文件到知识库 |
| GET | `/api/knowledge/documents` | 列出所有文档 |
| DELETE | `/api/knowledge/document/{id}` | 删除文档 |
| POST | `/api/knowledge/search` | 搜索知识库 |
| POST | `/api/knowledge/seed` | 填充示例数据 |

### AI 对话模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat` | AI康复助手对话 |

### 健康检查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 服务健康状态 |
| GET | `/api/status` | API 状态信息 |

---

## 🧪 测试

```bash
# 快速测试（核心功能）
python run_test.py

# 完整测试
python test_app.py
```

---

## 🔧 依赖服务（可选增强）

### Qdrant 向量数据库
用于知识库向量检索，提升搜索精度。

```bash
# Docker 启动
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

# 或安装本地版
pip install qdrant-client
```

### Ollama 本地 LLM
用于 AI 对话的回复生成。

```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 拉取模型
ollama pull qwen2.5

# 启动服务（默认端口 11434，可通过 OLLAMA_BASE_URL 环境变量修改）
ollama serve
```

---

## 📊 当前状态

| 组件 | 状态 |
|------|------|
| FastAPI 后端 | ✅ 已完成 |
| 用户认证 | ✅ 已完成 |
| 前端页面 | ✅ 已完成 |
| Qdrant 向量检索 | ⚠️ 可选（本地未部署时可降级为纯文本模式）|
| Ollama LLM | ⚠️ 可选（未部署时返回友好提示）|

---

## 📝 更新日志

### v3.0 (2026-09-02)
- ✨ 统一后端架构（FastAPI + 静态前端）
- ✨ 完整的用户注册/登录系统
- ✨ 智慧知识库管理界面
- ✨ AI康复助手对话页面
- 🐛 修复 Qdrant 不可用时的异常处理
- 🎨 优化 UI 设计和响应式布局

---

## ⚠️ 注意事项

1. **生产环境**：建议将 `USERS_DB` / `SESSIONS_DB` 替换为 PostgreSQL
2. **安全**：JWT_SECRET 环境变量应使用强随机密钥
3. **Qdrant**：如果不需要向量搜索，可以完全移除 Qdrant 依赖
4. **LLM**：AI 对话功能需要 Ollama 或外部 LLM API

---

*Powered by FastAPI · Railway · 云上大耳兔*  
*© 2026 ut2ai.com — 从聆听开始的治愈陪伴*
