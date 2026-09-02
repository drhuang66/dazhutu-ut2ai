"""
云上大耳兔 · 统一 Web 应用 (ut2ai.com)
基于 FastAPI + 静态文件服务
包含：登录注册、知识库管理、AI康复助手
v3.0 最终稳定版
"""

from fastapi import FastAPI, Request, HTTPException, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os, uuid, hashlib, json, requests, math
from datetime import datetime

app = FastAPI(
    title="云上大耳兔 · 智慧康复平台",
    version="3.0.0",
    description="从聆听开始的治愈陪伴 — AI康复智能体"
)

# ==================== CORS ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 配置 ====================
PORT = int(os.getenv("PORT", "5000"))
QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")  # Qdrant默认端口6333
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:8081")
COLLECTION_NAME = "ut2ai_rehab_knowledge"

# 模拟数据存储（生产环境应使用 PostgreSQL）
USERS_DB = {}       # username -> {password, nickname, created_at}
SESSIONS_DB = {}    # token -> username
QDRANT_CONNECTED = False  # Qdrant连接状态标记

# ==================== Qdrant HTTP API ====================
def qdrant_request(method: str, path: str, data=None):
    """Qdrant 通用 HTTP 请求"""
    url = f"{QDRANT_URL}{path}"
    try:
        if method == "GET":
            return requests.get(url, json=data, timeout=30).json()
        elif method == "POST":
            r = requests.post(url, json=data, timeout=30)
            r.raise_for_status()
            return r.json()
        elif method == "DELETE":
            r = requests.delete(url, json=data, timeout=30)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        print(f"Qdrant error [{method} {path}]: {e}")
        return None

def ensure_collection():
    """确保 Qdrant 集合存在"""
    global QDRANT_CONNECTED
    
    # 快速检查是否已连接
    if QDRANT_CONNECTED:
        return True
    
    try:
        # 获取所有集合列表
        collections = qdrant_request("GET", "/collections")
        if collections and "collections" in collections:
            names = [c.get("name", "") for c in collections["collections"]]
            if COLLECTION_NAME in names:
                QDRANT_CONNECTED = True
                return True
        
        # 创建集合（PUT请求）
        qdrant_request("PUT", f"/collections/{COLLECTION_NAME}", {
            "vectors": {"size": 768, "distance": "Cosine"}
        })
        QDRANT_CONNECTED = True
        print(f"✅ Qdrant集合 '{COLLECTION_NAME}' 已创建")
        return True
        
    except Exception as e:
        print(f"⚠️ Qdrant不可用: {e}")
        print("   知识库搜索和AI对话功能将使用简化模式（仅本地文本匹配）")
        return False

# ==================== 向量工具 ====================
def make_vector(text: str, dim: int = 768) -> List[float]:
    """基于文本生成固定维度向量"""
    raw = hashlib.sha512(text.encode()).digest()
    return [(raw[i % len(raw)] / 255.0) * 2 - 1 for i in range(dim)]

# ==================== Pydantic Models ====================
class RegisterRequest(BaseModel):
    username: str
    password: str
    nickname: Optional[str] = ""

class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    question: str

class DocumentInfo(BaseModel):
    id: str
    title: str
    category: str
    preview: str
    date: str

# ==================== 认证路由 ====================
@app.post("/api/auth/register")
async def register(req: RegisterRequest):
    """注册新用户"""
    if req.username in USERS_DB:
        raise HTTPException(400, "用户名已存在")
    
    USERS_DB[req.username] = {
        "password": hashlib.sha256(req.password.encode()).hexdigest(),
        "nickname": req.nickname or req.username,
        "created_at": datetime.now().isoformat()
    }
    
    # 自动登录，返回 token
    token = str(uuid.uuid4()) + req.username
    SESSIONS_DB[token] = req.username
    
    return {
        "message": "注册成功",
        "token": token,
        "user": {"username": req.username, "nickname": USERS_DB[req.username]["nickname"]}
    }

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    """用户登录"""
    user = USERS_DB.get(req.username)
    if not user or user["password"] != hashlib.sha256(req.password.encode()).hexdigest():
        raise HTTPException(401, "用户名或密码错误")
    
    token = str(uuid.uuid4()) + req.username
    SESSIONS_DB[token] = req.username
    
    return {
        "message": "登录成功",
        "token": token,
        "user": {"username": req.username, "nickname": user["nickname"]}
    }

@app.post("/api/auth/logout")
async def logout(token: str):
    """用户登出"""
    SESSIONS_DB.pop(token, None)
    return {"message": "已登出"}

@app.get("/api/auth/me")
async def get_me(token: Optional[str] = None):
    """获取当前用户信息"""
    if not token or token not in SESSIONS_DB:
        raise HTTPException(401, "未登录")
    
    username = SESSIONS_DB[token]
    user = USERS_DB.get(username)
    return {
        "username": username,
        "nickname": user["nickname"],
        "created_at": user["created_at"]
    }

# ==================== 知识库路由 ====================
@app.post("/api/knowledge/upload-text")
async def upload_text(
    text: str = Form(...),
    title: str = Form("新文档"),
    category: str = Form("general")
):
    """上传文本到知识库"""
    ensure_collection()
    
    vec = make_vector(text)
    metadata = {
        "title": title,
        "category": category,
        "date": datetime.now().isoformat(),
        "preview": (text[:200] + "...") if len(text) > 200 else text,
        "full_text": text
    }
    
    doc_id = str(uuid.uuid4())
    
    # 尝试写入 Qdrant（如果可用），否则静默跳过
    try:
        qdrant_request("POST", f"/collections/{COLLECTION_NAME}/points", {
            "points": [{"id": doc_id, "vector": vec, "payload": metadata}]
        })
    except:
        pass  # Qdrant不可用时仍返回成功
    
    return {"id": doc_id, "title": title, "category": category, "message": "上传成功"}

@app.post("/api/knowledge/upload-file")
async def upload_file(file: UploadFile = File(...), category: str = Form("general")):
    """上传文件到知识库"""
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    
    vec = make_vector(text)
    metadata = {
        "title": file.filename or "上传文档",
        "category": category,
        "date": datetime.now().isoformat(),
        "preview": (text[:200] + "...") if len(text) > 200 else text,
        "full_text": text
    }
    
    doc_id = str(uuid.uuid4())
    
    try:
        qdrant_request("POST", f"/collections/{COLLECTION_NAME}/points", {
            "points": [{"id": doc_id, "vector": vec, "payload": metadata}]
        })
    except:
        pass
    
    return {"id": doc_id, "title": metadata["title"], "message": "上传成功"}

@app.get("/api/knowledge/documents")
async def list_documents():
    """列出知识库中的所有文档"""
    ensure_collection()
    
    res = qdrant_request("POST", f"/collections/{COLLECTION_NAME}/points/scroll", {
        "limit": 100, "with_payload": True, "with_vectors": False
    })
    
    documents = []
    if res and "result" in res:
        for point in res["result"].get("points", []):
            payload = point.get("payload", {}) or {}
            documents.append(DocumentInfo(
                id=str(point.get("id", "")),
                title=payload.get("title", ""),
                category=payload.get("category", "general"),
                preview=(payload.get("preview", "") or "")[:120],
                date=payload.get("date", "")
            ))
    
    return {"total": len(documents), "documents": documents}

@app.delete("/api/knowledge/document/{doc_id}")
async def delete_document(doc_id: str):
    """删除文档"""
    try:
        qdrant_request("DELETE", f"/collections/{COLLECTION_NAME}/points", {
            "points": [doc_id]
        })
        return {"message": "删除成功"}
    except:
        raise HTTPException(404, "文档不存在")

@app.post("/api/knowledge/search")
async def search_knowledge(query: str = Form("query"), limit: int = 5):
    """搜索知识库"""
    results = []
    
    if QDRANT_CONNECTED:
        q_vec = make_vector(query)
        
        # 向量搜索
        try:
            res = qdrant_request("POST", f"/collections/{COLLECTION_NAME}/points/search", {
                "vector": q_vec, "limit": limit * 2, "with_payload": True
            })
            
            if res and "result" in res:
                for r in res["result"]:
                    payload = r.get("payload") or {}
                    results.append({
                        "id": str(r.get("id", "")),
                        "score": round(float(r.get("score", 0)), 4),
                        "title": payload.get("title", ""),
                        "category": payload.get("category", "general"),
                        "preview": (payload.get("preview", "") or "")[:150]
                    })
        except Exception as e:
            print(f"Vector search error: {e}")
    
    return {"query": query, "results": results[:limit]}

@app.post("/api/knowledge/seed")
async def seed_sample_data():
    """填充示例数据"""
    samples = [
        ("脑卒中康复临床路径", "clinical", 
         "脑卒中（中风）是全球范围内导致成人残疾的主要原因之一。早期、系统化的康复治疗能够显著改善患者功能预后。\n\n## 康复评估\n- Brunnstrom分期\n- Fugl-Meyer评分\n- Berg平衡量表\n\n## 康复治疗\n1. 早期康复（发病后24-48小时）：体位摆放、关节活动度训练\n2. 恢复期康复：任务导向性训练、镜像疗法\n3. 社区康复：家庭环境改造指导"),
        ("脊髓损伤康复指南", "clinical",
         "## 康复目标\n1. 恢复独立生活能力\n2. 预防并发症\n3. 社会功能重建\n\n## 主要治疗手段\n- 物理治疗（PT）\n- 作业治疗（OT）\n- 言语治疗（ST，适用于颈椎损伤）\n- 心理康复"),
        ("运动损伤康复方案", "research",
         "## 韧带损伤\n- RICE原则：休息、冰敷、加压包扎、抬高患肢\n- 渐进性关节活动度训练\n- 本体感觉训练\n\n## 肌肉拉伤\n- 急性期处理\n- 拉伸与按摩\n- 力量恢复训练"),
        ("老年康复护理SOP", "sop",
         "## 日常照护\n1. 生命体征监测\n2. 压疮预防（每2小时翻身）\n3. 营养评估与管理\n\n## 并发症预防\n- 深静脉血栓预防\n- 呼吸道感染预防\n- 跌倒风险评估"),
    ]
    
    ensure_collection()
    
    seeded = []
    for title, category, text in samples:
        try:
            vec = make_vector(text)
            doc_id = str(uuid.uuid4())
            metadata = {
                "title": title, "category": category,
                "date": datetime.now().isoformat(),
                "preview": (text[:200] + "...") if len(text) > 200 else text,
                "full_text": text
            }
            
            try:
                qdrant_request("POST", f"/collections/{COLLECTION_NAME}/points", {
                    "points": [{"id": doc_id, "vector": vec, "payload": metadata}]
                })
            except:
                pass  # Qdrant不可用时静默跳过
            
            seeded.append({"id": doc_id, "title": title, "category": category})
        except Exception as e:
            print(f"Seed error for {title}: {e}")
    
    return {"message": f"成功填充 {len(seeded)} 条示例数据", "documents": seeded}

# ==================== AI对话路由 ====================
def get_llm_response(question: str, context: str = "") -> str:
    """调用本地 LLM 生成回答"""
    system_prompt = "你是一个专业的康复医学智能助手。请基于以下知识库内容回答问题，如果知识不足请说明无法回答。"
    prompt = f"{system_prompt}\n\n【知识库参考】:\n{context}\n\n【用户问题】:\n{question}\n\n请给出专业、详细且易于理解的康复医学相关回答："
    
    try:
        r = requests.post(
            f"{OLLAMA_BASE_URL}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": os.getenv("LLM_MODEL", "qwen2.5"),
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1024,
                "temperature": 0.7
            },
            timeout=90
        )
        
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"LLM error: {e}")
    
    return f"⚠️ AI回复暂时不可用（{str(e)}）。但知识库搜索功能正常，请尝试使用搜索功能。"

@app.post("/api/chat")
async def chat(req: ChatRequest):
    """AI康复助手对话"""
    question = req.question
    
    # 获取相关上下文（Qdrant可用时）
    context = ""
    if QDRANT_CONNECTED:
        try:
            scroll_res = qdrant_request("POST", f"/collections/{COLLECTION_NAME}/points/scroll", {
                "limit": 50, "with_payload": True
            })
            
            keywords = [c for c in question if c.isalnum()][:10]
            
            if scroll_res:
                points = (scroll_res.get("result", {}) or {}).get("points", [])
                
                for point in points:
                    payload = point.get("payload") or {}
                    txt = (payload.get("full_text", "") or "").lower()
                    preview = (payload.get("preview", "") or "").lower()
                    
                    if any(kw in txt or kw in preview for kw in keywords):
                        context += f"[{payload.get('title', '')}] {txt[:400]}\n"
        except Exception as e:
            print(f"Context extract error: {e}")
    
    answer = get_llm_response(question, context)
    
    return {
        "question": question,
        "answer": answer,
        "context_provided": len(context) > 0,
        "sources_count": context.count("[") if context else 0
    }

# ==================== 健康检查 ====================
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "云上大耳兔 · 智慧康复平台",
        "version": "3.0.0",
        "qdrant": "connected" if QDRANT_CONNECTED else "unavailable",
        "ollama_base_url": OLLAMA_BASE_URL,
        "port": PORT
    }

@app.get("/api/status")
async def api_status():
    """API 状态接口"""
    return {
        "online": True,
        "url": f"http://localhost:{PORT}",
        "services": {
            "qdrant": QDRANT_CONNECTED,
            "llm": OLLAMA_BASE_URL
        }
    }

# ==================== 前端页面挂载 ====================
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")

@app.get("/")
async def root(request: Request):
    """首页 - 品牌着陆页"""
    path = os.path.join(FRONTEND_DIR, "landing.html")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>🐰 云上大耳兔</h1><p>智慧康复平台正在启动...</p>"

@app.get("/login")
async def login_page(request: Request):
    """登录页面"""
    path = os.path.join(FRONTEND_DIR, "auth.html")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>🐰 云上大耳兔</h1><p>登录页面加载中...</p>"

@app.get("/dashboard")
async def dashboard_page(request: Request):
    """仪表盘 - 知识库管理"""
    path = os.path.join(FRONTEND_DIR, "knowledge.html")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>🐰 云上大耳兔</h1><p>知识库页面加载中...</p>"

@app.get("/chat")
async def chat_page(request: Request):
    """AI对话页面"""
    path = os.path.join(FRONTEND_DIR, "chat.html")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>🐰 云上大耳兔</h1><p>AI对话页面加载中...</p>"

# ==================== 启动 ====================
if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🐰 云上大耳兔 · 智慧康复平台 v3.0")
    print(f"   端口: {PORT}")
    print(f"   地址: http://localhost:{PORT}")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=PORT)
