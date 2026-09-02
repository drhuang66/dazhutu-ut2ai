# 🐰 云上大耳兔 v3.0 — Railway 一键部署检查清单

---

## ✅ 已完成（本地阶段）

- [x] FastAPI 主应用 `main.py` 已编写并测试通过
- [x] 4个前端页面已完成（landing/auth/knowledge/chat）
- [x] API 接口全部测试通过（13/13项）
- [x] Git 仓库已初始化（2次提交）
- [x] 部署指南 `DEPLOY_GUIDE.md` 已生成
- [x] `.gitignore`、`requirements.txt`、`Procfile` 配置完成

---

## ⬜ 待执行（您需要操作）

### Step 1: GitHub 仓库创建

| 操作 | 说明 |
|------|------|
| 访问 | https://github.com/new |
| 仓库名 | `dazhutu-ut2ai` |
| 可见性 | Public |
| ❌ 不要勾选 | "Initialize with README" |

### Step 2: 推送代码到 GitHub

**复制以下命令执行（替换 YOUR_USERNAME）：**

```bash
cd C:/Users/drhua/AppData/Local/MdtAgent/workspace

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/dazhutu-ut2ai.git

# 推送代码
git push -u origin main
```

**常见问题：**
- ❌ `error: The requested URL returned error: 403` → GitHub 用户名错误
- ❌ `fatal: unable to access` → GitHub Token 过期（需重新配置）

### Step 3: Railway 部署

1. **访问 Railway:** https://railway.app → Login with GitHub

2. **创建项目:**
   - New Project → Deploy from GitHub repo
   - 选择 `dazhutu-ut2ai` 仓库

3. **设置环境变量:**
   ```
   PORT=5000
   ```
   （QDRANT_URL 和 OLLAMA_BASE_URL 可选，不填也能正常运行）

4. **等待部署完成**（1-3分钟）
   - Railway Dashboard → Deployments → 查看最新部署状态
   - 成功后会显示: `Your service is live at https://xxx.up.railway.app`

---

## ✅ 验证部署成功

### 测试 1: 访问主页
```
https://your-project.up.railway.app/
```
**预期结果:** 看到"云上大耳兔"品牌页面

### 测试 2: 测试 API
```
https://your-project.up.railway.app/health
```
**预期返回:**
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

### 测试 3: 注册测试
1. 访问 `/login`
2. 切换到"注册"Tab
3. 填写用户名、密码 → 点击"注册并进入"
4. ✅ 如果跳转到 `/dashboard`，说明部署完全正常！

---

## 📊 部署后功能清单

| 路由 | 功能 | 状态 |
|------|------|------|
| `/` | 品牌着陆页 | ⬜ 待验证 |
| `/login` | 登录/注册 | ⬜ 待验证 |
| `/dashboard` | 知识库管理 | ⬜ 待验证 |
| `/chat` | AI康复助手 | ⬜ 待验证 |
| `/health` | 健康检查 API | ⬜ 待验证 |

---

## 🆘 需要帮助？

### 部署失败的常见原因：

1. **GitHub 仓库未创建** → 先完成 Step 1
2. **环境变量缺失** → Railway Dashboard → Variables → 添加 PORT=5000
3. **依赖安装失败** → 检查 `requirements.txt` 内容
4. **端口配置错误** → Railway 使用 `$PORT` 环境变量，不能写死

### 获取帮助：

1. 查看 Railway Dashboard → Deployments → Logs（完整错误信息）
2. 截图发送给我，我会帮您诊断
3. 参考 `DEPLOY_GUIDE.md` 详细步骤

---

## 🎉 完成后的下一步

部署成功后，您可以：

- [ ] 配置自定义域名（ut2ai.com）
- [ ] 添加真实用户数据（上传康复文献）
- [ ] 接入 Qdrant 向量数据库（提升搜索精度）
- [ ] 部署 Ollama LLM（启用 AI 对话功能）
- [ ] 微信公众号对接（配置 `/wechat` 回调）

---

**云上大耳兔 v3.0 · 从聆听开始的治愈陪伴**  
*准备就绪，等待您的 GitHub 用户名即可一键推送！* 🚀
