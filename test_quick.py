"""简化测试 - ut2ai.com 核心功能验证"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from fastapi.testclient import TestClient
from main import app, QDRANT_CONNECTED, ensure_collection

client = TestClient(app)

print("=== 云上大耳兔 v3.0 - API 测试 ===\n")

# 1. 健康检查
r = client.get("/health")
data = r.json()
print(f"[1] GET /health -> {r.status_code} (Qdrant: {data.get('qdrant')})")
assert r.status_code == 200

# 2. API状态
r = client.get("/api/status")
print(f"[2] GET /api/status -> {r.status_code}")
assert r.status_code == 200

# 3. 注册
r = client.post("/api/auth/register", json={"username": "test1", "password": "test123"})
data = r.json()
print(f"[3] POST /api/auth/register -> {r.status_code} ({data.get('message')})")
assert r.status_code == 200
token = data["token"]

# 4. 登录
r = client.post("/api/auth/login", json={"username": "test1", "password": "test123"})
data = r.json()
print(f"[4] POST /api/auth/login -> {r.status_code} ({data.get('message')})")
assert r.status_code == 200

# 5. 用户信息
r = client.get(f"/api/auth/me?token={token}")
data = r.json()
print(f"[5] GET /api/auth/me -> {r.status_code} (user: {data['username']})")
assert r.status_code == 200

# 6. 填充示例
r = client.post("/api/knowledge/seed", json={}, headers={"Content-Type": "application/json"})
data = r.json()
print(f"[6] POST /api/knowledge/seed -> {r.status_code} ({data.get('message', '')})")
assert r.status_code == 200

# 7. 文档列表
r = client.get("/api/knowledge/documents")
data = r.json()
print(f"[7] GET /api/knowledge/documents -> {r.status_code} (total: {data['total']})")
assert r.status_code == 200

# 8. AI对话
r = client.post("/api/chat", json={"question": "脑卒中康复方法？"})
data = r.json()
print(f"[8] POST /api/chat -> {r.status_code} (answer_len: {len(data['answer'])})")
assert r.status_code == 200

# 9. 前端页面
for path, name in [("/", "首页"), ("/login", "登录"), ("/dashboard", "仪表盘"), ("/chat", "AI对话")]:
    r = client.get(path)
    print(f"[9] GET {path} ({name}) -> {r.status_code}")
    assert r.status_code == 200

print("\n" + "=" * 50)
print("全部通过！云上大耳兔 v3.0 运行正常。")
print("=" * 50)
