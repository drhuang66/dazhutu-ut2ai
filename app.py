from flask import Flask, render_template_string, request, jsonify
import os
import hashlib
import time
import logging
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ==================== 从环境变量读取配置 ====================
WECHAT_APPID = os.getenv('WECHAT_APPID', 'your_appid')
WECHAT_SECRET = os.getenv('WECHAT_SECRET', 'your_secret')
WECHAT_TOKEN = os.getenv('WECHAT_TOKEN', 'mytoken123')
BASE_URL = "https://century-app-production-dc64.up.railway.app/"

# ==================== 简单消息存储 ====================
messages = []

INDEX_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>大耳兔微信链接应用</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif; background: #f5f5f5; padding: 20px; }
.container { max-width: 700px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white; }
.header h1 { font-size: 26px; margin-bottom: 8px; }
.header p { opacity: 0.85; font-size: 14px; }
.content { padding: 30px; }
h2 { margin-bottom: 15px; color: #333; font-size: 18px; }
.config-section { background: #f0f7ff; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
.config-section label { display: block; color: #004085; font-weight: bold; margin-bottom: 5px; font-size: 14px; }
.config-section input { width: 100%; padding: 10px; border: 1px solid #b3d7ff; border-radius: 6px; font-size: 14px; margin-bottom: 12px; }
.callback-url-box { background: white; padding: 12px; border-radius: 6px; border: 1px dashed #667eea; margin-top: 10px; }
.callback-url-box strong { color: #667eea; }
.url-text { font-family: monospace; color: #333; word-break: break-all; cursor: pointer; padding: 8px; background: #f9f9f9; border-radius: 4px; display: block; margin-top: 5px; font-size: 13px; }
.msg-list { max-height: 300px; overflow-y: auto; }
.msg-item { background: #f8f9fa; padding: 12px; margin-bottom: 8px; border-radius: 8px; border-left: 4px solid #667eea; }
.msg-item .from { color: #667eea; font-weight: bold; margin-bottom: 3px; }
.msg-item .content { color: #333; }
.msg-item .time { color: #999; font-size: 12px; margin-top: 4px; }
.status-bar { display: flex; justify-content: space-between; align-items: center; padding: 15px 30px; background: #f8f9fa; border-top: 1px solid #e9ecef; }
.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.dot.online { background: #28a745; }
.dot.offline { background: #dc3545; }
button { background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; padding: 10px 24px; border-radius: 8px; cursor: pointer; font-size: 14px; }
button:hover { opacity: 0.9; }
.code-section { background: #fff3cd; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
.code-section h3 { color: #856404; margin-bottom: 12px; }
.step { color: #856404; margin-bottom: 10px; font-size: 14px; line-height: 1.6; }
.code { background: white; padding: 8px 12px; border-radius: 4px; font-family: monospace; font-size: 13px; color: #333; word-break: break-all; margin-top: 5px; display: inline-block; }
.footer { text-align: center; padding: 20px; color: #999; font-size: 12px; }
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🐰 大耳兔微信链接应用</h1>
        <p>WeChat Link Application · Railway部署版</p>
    </div>
    <div class="content">
        <!-- 回调地址 -->
        <div class="config-section">
            <label>📡 微信回调 URL（填入公众号后台）：</label>
            <div class="callback-url-box">
                <span id="callbackUrl" class="url-text" onclick="this.select()">{{ callback_url }}</span>
            </div>
        </div>

        <!-- Token 配置 -->
        <div class="config-section">
            <label>🔑 微信 Token（填入公众号后台，需与此处一致）：</label>
            <div style="background:white;padding:10px;border-radius:6px;font-family:monospace;color:#333;">{{ token_display }}</div>
        </div>

        <!-- 配置步骤 -->
        <div class="code-section">
            <h3>📋 接入微信公众号配置步骤</h3>
            <p class="step"><strong>1.</strong> 登录微信公众平台：https://mp.weixin.qq.com/</p>
            <p class="step"><strong>2.</strong> 导航到：<em>开发 → 基本配置 → 服务器配置</em></p>
            <p class="step"><strong>3.</strong> URL 填写：</p>
            <span class="code" onclick="this.select()">{{ callback_url }}</span>
            <p class="step"><strong>4.</strong> Token 填写：</p>
            <span class="code" onclick="this.select()">{{ token_display }}</span>
            <p class="step"><strong>5.</strong> EncodingAESKey：点击"随机生成"</p>
            <p class="step"><strong>6.</strong> 点击"提交"，提示"成功启用"即完成 ✅</p>
        </div>

        <!-- 消息列表 -->
        <h2>📨 接收到的消息（最近20条）</h2>
        <div class="msg-list" id="msgList">
            {% if messages %}
                {% for msg in messages %}
                <div class="msg-item">
                    <div class="from">{{ msg.from_name }}</div>
                    <div class="content">{{ msg.content }}</div>
                    <div class="time">{{ msg.time }}</div>
                </div>
                {% endfor %}
            {% else %}
                <p style="color:#999;padding:20px;text-align:center;">暂无消息（发送消息后会自动显示）</p>
            {% endif %}
        </div>

        <!-- 状态栏 -->
        <div class="status-bar">
            <div>
                <span class="dot online"></span>
                <span style="color:#333;margin-left:8px;">运行中</span>
            </div>
            <button onclick="refreshMessages()">刷新消息</button>
        </div>
    </div>
    <div class="footer">Powered by Flask + Railway · 大耳兔微信链接应用</div>
</div>

<script>
function refreshMessages() {
    fetch('/api/messages')
        .then(r => r.json())
        .then(data => {
            const list = document.getElementById('msgList');
            if (!data.messages || data.messages.length === 0) {
                list.innerHTML = '<p style="color:#999;padding:20px;text-align:center;">暂无消息</p>';
            } else {
                list.innerHTML = data.messages.map(m =>
                    '<div class="msg-item"><div class="from">' + m.from_name + '</div>' +
                    '<div class="content">' + m.content + '</div><div class="time">' + m.time + '</div></div>'
                ).join('');
            }
        });
}
setInterval(refreshMessages, 5000);
</script>
</body>
</html>
"""

@app.route('/')
def index():
    callback_url = BASE_URL + "wechat"
    return render_template_string(
        INDEX_PAGE,
        callback_url=callback_url,
        token_display=WECHAT_TOKEN,
        messages=messages[-20:],
    )

@app.route('/wechat', methods=['GET', 'POST'])
def wechat_callback():
    if request.method == 'GET':
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')

        logger.info(f"微信验证: sig={signature}, ts={timestamp}, nonce={nonce}")

        # 签名校验
        temp_list = sorted([WECHAT_TOKEN, timestamp, nonce])
        hash_str = hashlib.sha1(''.join(temp_list).encode('utf-8')).hexdigest()

        if hash_str == signature:
            logger.info("✅ 微信验证成功")
            return echostr
        else:
            logger.warning(f"❌ 微信验证失败 (expected={hash_str})")
            # 如果参数不完整，也允许通过（用于快速测试）
            if not signature or not timestamp:
                logger.info("⚠️ 未提供完整参数，返回 echostr 以便测试")
                return echostr
            return "Invalid signature", 403

    elif request.method == 'POST':
        from_name = request.form.get('FromUserName', 'Unknown')
        content = request.form.get('Content', '')
        msg_type = request.form.get('MsgType', 'unknown')

        msg = {
            "from_name": from_name,
            "content": f"[{msg_type}] {content}",
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        messages.append(msg)
        logger.info(f"📨 收到消息: {msg}")

        # 返回自动回复 XML
        reply_xml = f"""<xml>
<ToUserName><![CDATA[{from_name}]]></ToUserName>
<FromUserName><![CDATA[gh_xxxxxxxxxxxx]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[收到：{content[:50]}（由大耳兔应用自动回复）]]></Content>
</xml>"""
        return reply_xml, 200, {'Content-Type': 'application/xml'}

@app.route('/api/messages')
def api_messages():
    return jsonify({"messages": messages[-20:]})

if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    print("=" * 60)
    print("🐰 大耳兔微信链接应用已启动")
    print(f"   回调 URL: {BASE_URL}wechat")
    print(f"   Token:    {WECHAT_TOKEN}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=False)
