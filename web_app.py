from flask import Flask, render_template_string, request, jsonify
import requests
import os
import hashlib
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ==================== 微信配置（需要用户填写）====================
WECHAT_APPID = "your_appid"        # 微信公众号 AppID
WECHAT_SECRET = "your_secret"       # 微信公众号 Secret
WECHAT_TOKEN = "your_token"         # 微信公众号 Token（用于验证）
BASE_URL = "https://century-app-production-dc64.up.railway.app/"   # Railway 公网地址

# ==================== 微信消息模板（HTML 页面）====================
MESSAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>大耳兔微信链接应用</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 600px;
            width: 100%;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            color: white;
            font-size: 28px;
            margin-bottom: 5px;
        }
        .header p {
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
        }
        .content {
            padding: 30px;
        }
        .message-list {
            max-height: 400px;
            overflow-y: auto;
            margin-bottom: 20px;
        }
        .message-item {
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .message-item .from {
            color: #667eea;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .message-item .content {
            color: #333;
            line-height: 1.6;
        }
        .message-item .time {
            color: #999;
            font-size: 12px;
            margin-top: 5px;
        }
        .config-panel {
            background: #fff3cd;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .config-panel h3 {
            color: #856404;
            margin-bottom: 15px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            color: #856404;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ffc107;
            border-radius: 5px;
            font-size: 14px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 30px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
        }
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #dc3545;
        }
        .dot.online {
            background: #28a745;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐰 大耳兔微信链接应用</h1>
            <p>WeChat Link Application</p>
        </div>
        
        <div class="content">
            <div class="config-panel" id="configPanel">
                <h3>⚙️ 配置信息</h3>
                
                <div class="form-group">
                    <label>微信公众号 AppID：</label>
                    <input type="text" id="appid" value="{{ appid }}" placeholder="请输入 AppID">
                </div>
                
                <div class="form-group">
                    <label>微信公众号 Secret：</label>
                    <input type="password" id="secret" value="{{ secret }}" placeholder="请输入 Secret">
                </div>
                
                <div class="form-group">
                    <label>微信公众号 Token：</label>
                    <input type="text" id="token" value="{{ token }}" placeholder="请输入 Token">
                </div>
                
                <div style="margin-top: 15px; padding: 10px; background: #e7f3ff; border-radius: 8px;">
                    <strong style="color: #004085;">📡 回调地址：</strong>
                    <input type="text" id="callbackUrl" value="{{ callback_url }}" readonly 
                           style="margin-top: 5px; background: white; color: #666;" onclick="this.select()">
                </div>
                
                <button onclick="saveConfig()">保存配置</button>
            </div>

            <h3 style="margin-bottom: 15px; color: #333;">📨 接收到的消息</h3>
            
            <div class="message-list" id="messageList">
                {% if messages %}
                    {% for msg in messages %}
                    <div class="message-item">
                        <div class="from">{{ msg.from_name }}</div>
                        <div class="content">{{ msg.content }}</div>
                        <div class="time">{{ msg.time }}</div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p style="text-align: center; color: #999; padding: 40px;">暂无消息</p>
                {% endif %}
            </div>

            <div class="status-bar">
                <div class="status-indicator">
                    <span id="statusDot" class="dot {{ 'online' if status == 'online' }}"></span>
                    <span id="statusText">{{ status_display }}</span>
                </div>
                <button onclick="refreshMessages()" style="width: auto; padding: 8px 20px;">刷新消息</button>
            </div>
        </div>
    </div>

    <script>
        function saveConfig() {
            const appid = document.getElementById('appid').value;
            const secret = document.getElementById('secret').value;
            const token = document.getElementById('token').value;
            
            fetch('/api/config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({app_id: appid, secret: secret, token: token})
            })
            .then(response => response.json())
            .then(data => {
                alert('配置已保存！');
                if (data.status === 'online') {
                    document.getElementById('statusDot').classList.add('online');
                    document.getElementById('statusText').textContent = '运行中';
                }
            })
            .catch(error => {
                alert('保存失败：' + error);
            });
        }

        function refreshMessages() {
            fetch('/api/messages')
            .then(response => response.json())
            .then(data => {
                const list = document.getElementById('messageList');
                if (data.messages.length === 0) {
                    list.innerHTML = '<p style="text-align: center; color: #999; padding: 40px;">暂无消息</p>';
                } else {
                    list.innerHTML = data.messages.map(msg => 
                        '<div class="message-item">' +
                        '<div class="from">' + msg.from_name + '</div>' +
                        '<div class="content">' + msg.content + '</div>' +
                        '<div class="time">' + msg.time + '</div>' +
                        '</div>'
                    ).join('');
                }
            });
        }

        // 每5秒自动刷新消息
        setInterval(refreshMessages, 5000);
    </script>
</body>
</html>
"""


# ==================== 数据存储（简单使用内存）====================
messages = []


@app.route('/')
def index():
    """主页，显示配置面板和消息列表"""
    # 确定状态显示
    if BASE_URL:
        status_display = "运行中"
        status_class = "online"
        full_callback_url = f"{BASE_URL}wechat"
    else:
        status_display = "等待配置..."
        status_class = ""
        full_callback_url = ""

    return render_template_string(
        MESSAGE_TEMPLATE,
        appid=WECHAT_APPID,
        secret="*" * min(len(WECHAT_SECRET), 8),  # 隐藏 Secret
        token=WECHAT_TOKEN,
        messages=messages[-20:],  # 只显示最近20条
        status_display=status_display,
        status=status_class,
        callback_url=full_callback_url
    )


@app.route('/wechat', methods=['GET', 'POST'])
def wechat_callback():
    """微信消息回调接口"""
    
    if request.method == 'GET':
        # 微信服务器验证请求
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')

        logger.info(f"微信验证请求: signature={signature}, timestamp={timestamp}, nonce={nonce}")
        
        # 简单验证（实际项目中应进行签名校验）
        temp_list = [WECHAT_TOKEN, timestamp, nonce]
        temp_list.sort()
        temp_str = ''.join(temp_list)
        hash_str = hashlib.sha1(temp_str.encode('utf-8')).hexdigest()
        
        if hash_str == signature:
            logger.info("微信验证成功")
            return echostr
        else:
            logger.warning("微信验证失败")
            return "Invalid signature", 403

    elif request.method == 'POST':
        # 接收微信消息
        from_xml = """
        <xml>
            <ToUserName><![CDATA[toUser]]></ToUserName>
            <FromUserName><![CDATA[{from_user}]]></FromUserName>
            <CreateTime>{create_time}</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[{content}]]></Content>
        </xml>
        """.format(
            from_user=request.form.get('FromUserName', 'Unknown'),
            create_time=int(time.time()),
            content=request.form.get('Content', '')
        )

        # 解析并保存消息
        msg = {
            "from_name": request.form.get('FromUserName', 'Unknown'),
            "content": request.form.get('Content', ''),
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
        messages.append(msg)
        
        logger.info(f"收到消息: {msg}")
        
        # 返回确认响应
        return jsonify({"status": "success", "message": "Message received"})


@app.route('/api/config', methods=['POST'])
def api_config():
    """API：更新配置"""
    data = request.json
    
    if 'app_id' in data:
        global WECHAT_APPID
        WECHAT_APPID = data['app_id']
    
    if 'secret' in data:
        global WECHAT_SECRET
        WECHAT_SECRET = data['secret']
    
    if 'token' in data:
        global WECHAT_TOKEN
        WECHAT_TOKEN = data['token']
    
    # 更新 ngrok URL（如果提供）
    if BASE_URL:
        return jsonify({
            "status": "online",
            "url": f"{BASE_URL}wechat",
            "message": "配置已更新"
        })
    
    return jsonify({
        "status": "offline",
        "message": "配置已保存，请启动 ngrok 隧道以激活"
    })


@app.route('/api/messages')
def api_messages():
    """API：获取消息列表"""
    return jsonify({"messages": messages[-20:]})


@app.route('/api/status')
def api_status():
    """API：检查服务状态"""
    if BASE_URL:
        return jsonify({
            "status": "online",
            "url": f"{BASE_URL}wechat",
            "port": 5000
        })
    else:
        return jsonify({
            "status": "offline",
            "message": "ngrok 隧道未启动"
        })


if __name__ == '__main__':
    print("=" * 60)
    print("🐰 大耳兔微信链接应用已启动")
    print("=" * 60)
    print(f"本地服务地址: http://localhost:{os.getenv('PORT', '5000')}")
    print(f"微信回调地址: {BASE_URL}wechat")
    print("-" * 60)
    
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=True)
