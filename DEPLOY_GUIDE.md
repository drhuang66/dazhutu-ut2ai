# 🚀 ut2ai.com 云上大耳兔 — 快速部署指南

> 3 分钟完成 Railway 部署

---

## 📋 一、本地代码已就绪

✅ Git 仓库已初始化  
✅ 42 个文件已提交（commit: `49e7c74`）  
✅ main.py + frontend/ 全部就绪  

**下一步：推送到 GitHub → Railway 部署**

---

## 🛠️ 二、推送代码到 GitHub

### Step 1: 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名：`dazhutu-ut2ai`（或其他你喜欢名称）
3. 选择 **Public**
4. **不要**勾选"Initialize with README"等选项
5. 点击 **"Create repository"**

### Step 2: 推送代码到 GitHub

在 Git Bash 中执行以下命令：

```bash
# 设置远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/dazhutu-ut2ai.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

> 💡 **如果推送失败**，请检查：
> - GitHub 账号是否已登录？
> - 用户名是否正确？
> - 是否有推送权限？

---

## ☁️ 三、Railway 部署（3 分钟）

### Step 1: 连接 Railway

1. 访问 https://railway.app
2. 点击 **"Login"** → GitHub 授权登录
3. 点击 **"New Project"**
4. 选择 **"Deploy from GitHub repo"**
5. 搜索并选择 `dazhutu-ut2ai` 仓库
6. Railway 自动检测 FastAPI + uvicorn ✅

### Step 2: 配置环境变量

部署过程中，Railway 会提示设置环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `PORT` | `5000` | **必需** — 服务端口 |
| `QDRANT_URL` | *(留空)* | 可选 — Qdrant 向量数据库 |
| `OLLAMA_BASE_URL` | *(留空)* | 可选 — 本地 LLM 服务 |

> 💡 **提示：** 即使不配置 QDRANT_URL 和 OLLAMA_BASE_URL，应用也能正常运行（自动降级为简化模式）

### Step 3: 等待部署完成

- Railway 自动构建，约 1-3 分钟
- 完成后会分配一个域名：`https://your-project.up.railway.app`

---

## ✅ 四、验证部署成功

### 方式 1: 访问主页

浏览器打开：`https://your-project.up.railway.app/`

应该看到：
```
🐰 云上大耳兔
智慧康复平台 · 从聆听开始的治愈陪伴
[立即体验] [了解更多]
```

### 方式 2: 测试 API

浏览器打开：`https://your-project.up.railway.app/health`

应该返回 JSON：
```json
{
  "status": "ok",
  "service": "云上大耳兔 · 智慧康复平台",
  "version": "3.0.0",
  "qdrant": "unavailable",
  "ollama_base_url": "",
  "port": 5000
}
```

### 方式 3: 测试注册功能

在 `/login` 页面尝试注册新用户，如果成功跳转 `/dashboard`，说明部署完全正常 ✅

---

## 🔑 五、配置自定义域名（可选）

如果你想使用 `ut2ai.com`：

1. **购买/已有 ut2ai.com 域名**
2. **Cloudflare DNS 设置：**
   - A 记录 → Railway IP: `76.76.21.21`
   - 或 CNAME 记录 → your-project.up.railway.app
3. **Railway 域名绑定：**
   - Railway Dashboard → Your Project → Settings → Domains
   - 添加自定义域名：`ut2ai.com` 和 `www.ut2ai.com`

---

## 📊 六、功能清单（部署后自动启用）

| 路由 | 功能 |
|------|------|
| `/` | 品牌着陆页 |
| `/login` | 登录/注册页面 |
| `/dashboard` | 知识库管理仪表盘 |
| `/chat` | AI康复助手对话 |
| `/health` | 健康检查 API |
| `/api/auth/*` | 认证 API（注册/登录/登出）|
| `/api/knowledge/*` | 知识库 API（上传/搜索/删除）|
| `/api/chat` | AI 对话 API |

---

## 🆘 七、常见问题

### Q1: Railway 部署一直显示 "Building"？

**原因：** 依赖安装失败或构建脚本错误  
**解决：**
- 检查 `requirements.txt` 是否包含所有必需包
- 查看 Railway Dashboard → Deployments → Logs 中的详细错误信息

### Q2: 登录后页面空白？

**原因：** API 端点不可访问  
**解决：**
- 确认 `/health` 返回 200 OK
- 检查浏览器控制台（F12）是否有 CORS 错误

### Q3: AI 对话返回"暂时不可用"？

**原因：** Ollama LLM 未部署或不可达  
**解决：**
- 这是正常行为，知识库搜索功能仍可用
- 如需 AI 功能，请部署 Ollama（见 README.md）

---

## 📞 需要帮助？

如果部署过程中遇到任何问题：
1. 查看 Railway Dashboard → **Logs** 面板的完整错误信息
2. 提供截图给我，我会帮您诊断
3. 检查 `README.md` 中的详细文档

---

*云上大耳兔 v3.0 · 从聆听开始的治愈陪伴*  
*部署时间：2026-09-02*
