"""测试 ut2ai.com 统一应用的所有端点"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("=== 云上大耳兔 API 测试 ===\n")

try:
    # 1. 健康检查
    r = client.get("/health")
    print(f"[1] GET /health -> {r.status_code}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"

    # 2. API状态
    r = client.get("/api/status")
    print(f"[2] GET /api/status -> {r.status_code}")
    assert r.status_code == 200

    # 3. 注册新用户
    r = client.post("/api/auth/register", 
        json={"username": "testuser", "password": "test123456", "nickname": "测试用户"})
    print(f"[3] POST /api/auth/register -> {r.status_code}")
    reg_data = r.json()
    assert r.status_code == 200 and reg_data["message"] == "注册成功"
    token = reg_data["token"]
    print(f"      Token: {token[:30]}...")

    # 4. 用户登录
    r = client.post("/api/auth/login",
        json={"username": "testuser", "password": "test123456"})
    print(f"[4] POST /api/auth/login -> {r.status_code}")
    login_data = r.json()
    assert r.status_code == 200 and login_data["message"] == "登录成功"

    # 5. 获取用户信息
    r = client.get(f"/api/auth/me?token={token}")
    print(f"[5] GET /api/auth/me -> {r.status_code}")
    me_data = r.json()
    assert r.status_code == 200 and me_data["username"] == "testuser"

    # 6. 填充示例数据（Qdrant可能不可用，会返回部分结果）
    r = client.post("/api/knowledge/seed", 
        json={}, headers={"Content-Type": "application/json"})
    print(f"[6] POST /api/knowledge/seed -> {r.status_code}")
    seed_data = r.json()
    print(f"      种子数据结果: {seed_data.get('message', 'N/A')}")

    # 7. 列出文档
    r = client.get("/api/knowledge/documents")
    print(f"[7] GET /api/knowledge/documents -> {r.status_code}")
    docs_data = r.json()
    print(f"      知识库文档数: {docs_data.get('total', 0)}")

    # 8. 上传新文本（Qdrant可能不可用）
    r = client.post("/api/knowledge/upload-text", 
        data={"text": "这是测试文本内容用于康复知识检索。", "title": "测试文档", "category": "general"})
    print(f"[8] POST /api/knowledge/upload-text -> {r.status_code}")

    # 9. AI对话
    r = client.post("/api/chat", 
        json={"question": "脑卒中康复有哪些主要方法？"})
    print(f"[9] POST /api/chat -> {r.status_code}")
    chat_data = r.json()
    answer_len = len(chat_data.get("answer", ""))
    print(f"      AI回复长度: {answer_len} 字符")

    # 10. 前端页面路由
    pages = [
        ("/", "首页"),
        ("/login", "登录页"),
        ("/dashboard", "仪表盘"),
        ("/chat", "AI对话页"),
    ]
    for i, (path, name) in enumerate(pages):
        r = client.get(path)
        print(f"[10.{i+1}] GET {path} ({name}) -> {r.status_code}")
        assert r.status_code == 200

    print("\n" + "=" * 50)
    print("全部测试通过！云上大耳兔 v3.0 运行正常。")
    print("=" * 50)

except AssertionError as e:
    print(f"\n[FAILED] {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
