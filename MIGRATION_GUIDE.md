# 从 Railway 迁移到 Fly.io — 操作指南

## 📋 已完成的准备工作

- ✅ `Dockerfile` — 标准 Python 3.11 Docker 镜像
- ✅ `fly.toml` — Fly.io 应用配置（新加坡节点，512MB RAM）
- ✅ `.dockerignore` — 排除不必要的文件
- ✅ 清理了 Railway 相关配置文件
- ✅ 代码已推送到 GitHub

## 🚀 部署步骤

### 1. 安装 Fly CLI

```bash
# macOS
brew install flyctl

# Linux (WSL)
curl -L https://fly.io/install.sh | sh
```

### 2. 登录 Fly.io

```bash
flyctl auth login
# 会在浏览器中打开授权页面
```

### 3. 创建应用

```bash
cd /root/clacky_workspace/yunshangtu
flyctl launch --no-deploy --name yunshangtu
# 回答提示：Yes, I'll select it now → sin (新加坡) → No for Postgres/Redis
```

### 4. 设置环境变量（从 Railway 迁移）

```bash
# 登录 Railway 获取这些值
flyctl secrets set \
  ADMIN_USERNINGS="你的管理员用户名" \
  QDRANT_URL="https://your-qdrant-fly-app.fly.dev" \
  OLLAMA_BASE_URL="https://your-ollama-fly-app.fly.dev"
```

> ⚠️ 注意：Qdrant 和 Ollama 需要单独部署为 Fly.io 服务

### 5. 部署

```bash
flyctl deploy
```

### 6. 验证

```bash
flyctl status
flyctl logs
# 测试 API
curl https://yunshangtu.fly.dev/health
```

## 🗄️ Qdrant + Ollama 的 Fly.io 部署方案

由于你的应用依赖 Qdrant 和 Ollama，有两种选择：

### 方案 A：使用外部托管服务（推荐）
- **Qdrant**: https://cloud.qdrant.io/ （有免费额度）
- **Ollama**: 需要自托管或使用 Groq / OpenRouter 等替代

### 方案 B：在 Fly.io 上部署全部服务
每个服务独立部署为 Fly app，通过内部网络通信。

## 🌐 自定义域名配置

```bash
# 添加自定义域名
flyctl certs add www.ut2ai.com
flyctl cert show www.ut2ai.com

# DNS 记录指向 Fly.io
# CNAME www → yunshangtu.fly.dev
```

## 💰 费用估算

- **应用服务**: $0/月（512MB + shared CPU，在免费额度内）
- **Qdrant 托管**: ~$9/月（cloud.qdrant.io free tier）
- **总计**: ~$9/月（远低于 Railway Pro）
