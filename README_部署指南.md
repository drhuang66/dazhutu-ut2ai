# 大耳兔微信链接应用 - Railway部署指南
## ================================

## 📋 问题诊断结果

您的 Railway 项目 **目前没有运行 Flask 应用**，返回的是其他内容（"Century · 百年人生"），所以 `/wechat` 端点返回 404。

---

## 🔧 修复步骤：在 Railway 上正确部署 Flask 应用

### 第一步：准备项目文件（已在本地生成）

您工作区 `C:/Users/drhua/AppData/Local/MdtAgent/workspace/` 下已有以下文件：

| 文件名 | 用途 |
|--------|------|
| `web_app.py` | Flask 应用主文件（入口：`app`） |
| `Procfile` | Railway 进程配置（告诉 Railway 如何启动） |
| `requirements.txt` | Python 依赖包清单 |
| `.env.example` | 环境变量模板 |

### 第二步：上传代码到 GitHub / GitLab

1. **创建新仓库**  
   - 访问 https://github.com/new
   - 仓库名建议：`dazhutu-wechat-app`
   - Public 即可，点击 "Create repository"

2. **将本地文件推送到 GitHub**

   ```bash
   # 在 workspace 目录下执行：
   cd C:/Users/drhua/AppData/Local/MdtAgent/workspace
   git init
   git add .
   git commit -m "Initial commit: 大耳兔微信链接应用"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/dazhutu-wechat-app.git
   git push -u origin main
   ```

3. **⚠️ 重要：`.gitignore`**  
   如果您的工作区已有 `.gitignore`，确保包含：
   ```
   .env
   __pycache__/
   *.pyc
   ```

### 第三步：在 Railway 上部署

1. **登录 Railway**  
   https://railway.app → GitHub 登录

2. **新建项目**  
   - 点击 "New Project"
   - 选择 **"Deploy from GitHub repo"**
   - 选择您刚创建的 `dazhutu-wechat-app` 仓库

3. **Railway 会自动检测 Flask，并显示：**  
   > "Flask project detected!"

### 第四步：设置环境变量（关键！）

在 Railway Dashboard → 您的项目 → **Variables** 标签页，添加以下变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `PORT` | `5000` | Railway 要求的端口 |
| `WECHAT_APPID` | `wx1234567890abcdef` | **替换为您公众号的 AppID** |
| `WECHAT_SECRET` | `abcdef1234567890` | **替换为您公众号的 Secret** |
| `WECHAT_TOKEN` | `mytoken123` | 自定义 Token（建议用字母+数字）|

### 第五步：等待部署完成

Railway 会自动构建并部署，大约需要 1-3 分钟。完成后会分配一个新的域名，类似：
```
https://your-project.up.railway.app
```

---

## 📡 配置微信公众号服务器

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 导航：**开发 → 基本配置 → 服务器配置**
3. 填写以下信息：

   | 配置项 | 值 |
   |--------|-----|
   | **URL** | `https://您的Railway域名/wechat` |
   | **Token** | 与 Railway 中的 `WECHAT_TOKEN` 相同（如：`mytoken123`）|
   | **EncodingAESKey** | 点击"随机生成"即可 |

4. 点击 **"提交"**  
   - 如果提示 "成功启用"，说明微信回调已连通 ✅
   - 如果失败，检查 URL 是否正确、Token 是否一致

---

## ✅ 验证步骤

### 1. 检查 Railway 服务状态
```bash
# 测试主页面
curl https://您的Railway域名/

# 测试微信回调端点（应返回 echostr）
curl "https://您的Railway域名/wechat?signature=test&timestamp=1234567890&nonce=abc123&echostr=dummy"

# 测试 API 状态
curl https://您的Railway域名/api/status
```

### 2. 查看 Railway Logs
- Railway Dashboard → **Deployments** → 点击最新部署 → **Logs**
- 应该看到类似：
  ```
  🐰 大耳兔微信链接应用已启动
  本地服务地址: http://0.0.0.0:5000
  微信回调地址: https://xxx.up.railway.app/wechat
  ```

### 3. 测试接收消息
- 关注您的公众号
- 发送一条消息给公众号
- 检查 Railway Logs，应该看到：
  ```
  INFO: 收到消息: {'from_name': '用户OpenID', 'content': '您发的内容', 'time': '2026-xx-xx xx:xx:xx'}
  ```

---

## 🆘 常见问题排查

### Q1: 提交后提示 "URL验证失败"
**原因：** URL 格式不对或 Token 不匹配  
**解决：**
- 确认 URL 以 `https://` 开头，没有多余空格
- 确认 Token 与代码中一致（区分大小写）
- 检查 Railway Logs 是否有 `微信验证成功` 日志

### Q2: Railway 一直显示 "Building"
**原因：** requirements.txt 问题或构建失败  
**解决：**
- 检查 `requirements.txt` 是否包含 `flask` 和 `gunicorn`
- 查看 Railway Logs 中的具体错误信息

### Q3: 微信能发消息，但 Flask 没收到
**原因：** 可能是消息类型不是 text  
**解决：** 代码已支持 text 类型，如需支持其他类型（图片、语音等），需要扩展 `/wechat` 的 POST 处理逻辑

---

## 📞 联系方式

如果在部署过程中遇到问题：
1. 查看 Railway Dashboard 中的 **Logs** 面板
2. 提供错误截图给我，我会帮您诊断
3. 也可在 GitHub Issues 中提问

---

*最后更新：2026-09-02*
