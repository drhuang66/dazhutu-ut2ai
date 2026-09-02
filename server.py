"""
智慧康复知识库 API v3.0 - 最终稳定版
不依赖 qdrant-client（避免版本兼容问题），直接用 requests + Qdrant HTTP API
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from typing import List, Optional
import requests, os, uuid, hashlib, json
from datetime import datetime

app = FastAPI(title="智慧康复知识库 API v3.0")

QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:16333")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:8081")
COLLECTION_NAME = "rehab_knowledge"

# ==================== 向量工具 ====================
def make_vec(text: str, dim=768):
    """基于文本生成固定维度的向量"""
    raw = hashlib.sha512(text.encode()).digest()
    return [(raw[i % len(raw)] / 255.0) * 2 - 1 for i in range(dim)]

def cosine_sim(a: list, b: list) -> float:
    dot = sum(x*y for x,y in zip(a,b))
    na = (sum(x*x for x in a)) ** 0.5
    nb = (sum(x*x for x in b)) ** 0.5
    return dot / (na * nb + 1e-9)

# ==================== Qdrant HTTP API ====================
def qdrant_scroll(path, data=None):
    """Qdrant scroll 查询（POST + JSON body）"""
    r = requests.post(f"{QDRANT_URL}{path}", json=data or {}, timeout=30)
    r.raise_for_status()
    return r.json()

def qdrant_post(path, data=None):
    """Qdrant HTTP POST"""
    r = requests.post(f"{QDRANT_URL}{path}", json=data or {}, timeout=30)
    r.raise_for_status()
    return r.json()

# ==================== 初始化集合 ====================
try:
    # 创建集合（如果不存在）
    qdrant_get("/collections")
except: pass

try:
    qdrant_post(f"/collections/{COLLECTION_NAME}", {
        "vectors": {"size": 768, "distance": "Cosine"}
    })
except Exception as e:
    print(f"Collection creation result: {e}")

# ==================== LLM ====================
def llm_reply(question: str, ctx: str = "") -> str:
    prompt = f"你是一名康复医学AI助手。请基于以下知识库内容回答用户问题。\n\n[知识库]:\n{ctx}\n\n[问题]: {question}"
    try:
        r = requests.post(f"{OLLAMA_BASE_URL}/v1/chat/completions",
            headers={"Content-Type":"application/json"},
            json={
                "model": os.getenv("LLM_MODEL","Qwen3.6-35B-A3B-Q8_0"),
                "messages":[{"role":"user","content":prompt}],
                "max_tokens":800, "temperature":0.7
            }, timeout=90)
        if r.status_code == 200: return r.json()["choices"][0]["message"]["content"]
    except Exception as e: pass
    return f"(LLM 暂时无法响应：{e})"

# ==================== API 路由 ====================
@app.get("/health")
async def health(): return {"ok": True}

# 上传文本
@app.post("/upload-text")
def upload_text(text: str = Form(...), title: str = Form("文档"), category: str = Form("general")):
    vec = make_vec(text)
    md = {
        "title": title, "category": category,
        "date": datetime.now().isoformat(),
        "text": text,
        "preview": (text[:200] + "...") if len(text) > 200 else text
    }
    pid = str(uuid.uuid4())
    try:
        qdrant_post(f"/collections/{COLLECTION_NAME}/points", {
            "points": [{"id": pid, "vector": vec, "payload": md}]
        })
    except Exception as e: print(f"Upload Qdrant error: {e}")
    return {"id": pid, "title": title, "msg": "ok"}

# 上传文件
@app.post("/upload-file")
def upload_file(file: UploadFile = File(...), category: str = Form("general")):
    t = file.read().decode(errors="ignore")
    return upload_text(text=t, title=file.filename or "", category=category)

# 列出文档
@app.get("/api-docs")
def list_docs():
    ds = []
    try:
        res = qdrant_scroll(f"/collections/{COLLECTION_NAME}/points/scroll", {"limit": 200})
        for p in (res.get("result", {}) or {}).get("points", []):
            d = p.get("payload", {}) or {}
            ds.append({
                "id": str(p.get("id","")),
                "title": d.get("title",""),
                "category": d.get("category",""),
                "preview": (d.get("preview","") or "")[:120]
            })
    except Exception as e: print(f"List error: {e}")
    return {"total": len(ds), "docs": ds}

# 删除文档
@app.delete("/doc/{pid}")
def del_doc(pid: str):
    try:
        qdrant_post(f"/collections/{COLLECTION_NAME}/points/delete", {"points": [pid]})
        return {"ok": True}
    except Exception as e: raise HTTPException(404, str(e))

# 搜索
@app.post("/api-search")
def search(q: str = Form("q"), limit: int = 5):
    results = []
    q_vec = make_vec(q)

    # 1. Qdrant 向量搜索
    try:
        res = qdrant_post(f"/collections/{COLLECTION_NAME}/points/search", {
            "vector": q_vec, "limit": limit * 2, "with_payload": True
        })
        for r in res.get("result", []):
            d = r.get("payload") or {}
            results.append({
                "id": str(r.get("id","")),
                "score": round(float(r.get("score",0)), 4),
                "type": "vector",
                "payload": {k:v for k,v in d.items() if k != "text"}
            })
    except Exception as e: print(f"Vector search error: {e}")

    # 2. 全文匹配（兜底）
    try:
        scroll_res = qdrant_get(f"/collections/{COLLECTION_NAME}/points/scroll", {"limit": 100})
        q_lower = q.lower()
        for p in (scroll_res.get("result") or []):
            payload = p.get("payload", {}) or {}
            txt = (payload.get("text","") or "").lower()
            title = (payload.get("title","") or "").lower()
            preview = (payload.get("preview","") or "").lower()
            match_score = 0
            if q_lower in title: match_score = 100
            elif q_lower in preview: match_score = 80
            elif q_lower in txt: match_score = 50
            if match_score > 0:
                pid = str(p.get("id",""))
                existing_ids = {r["id"] for r in results}
                if pid not in existing_ids:
                    results.append({
                        "id": pid,
                        "score": round(match_score/100, 4),
                        "type": "text_match",
                        "payload": {k:v for k,v in payload.items() if k != "text"}
                    })
    except Exception as e: print(f"Text match error: {e}")

    results.sort(key=lambda x: x["score"], reverse=True)
    return {"query": q, "results": results[:limit]}

# AI对话（RAG）
@app.post("/chat")
def chat(req: dict):
    q = req.get("question", "")
    ctx = ""
    try:
        scroll_res = qdrant_scroll(f"/collections/{COLLECTION_NAME}/points/scroll", {"limit": 50})
        keywords = [c for c in q if c.isalnum()][:10]
        points = (scroll_res.get("result", {}) or {}).get("points", [])
        for p in points:
            payload = p.get("payload", {}) or {}
            txt = (payload.get("text","") or "").lower()
            preview = (payload.get("preview","") or "").lower()
            if any(kw in txt or kw in preview for kw in keywords):
                ctx += f"[{payload.get('title','')}] {txt[:400]}\n"
    except Exception as e: print(f"Context extract error: {e}")
    return {"question": q, "answer": llm_reply(q, ctx)}

# 填充示例数据
@app.post("/seed")
def seed_data():
    samples = [
        ("脑卒中康复临床路径", "clinical",
         "脑卒中康复评估包括Brunnstrom分期、Fugl-Meyer评分。早期康复治疗应在发病后48小时内开始，通过体位摆放和关节活动度训练预防并发症。"),
        ("脊髓损伤康复指南", "clinical",
         "脊髓损伤康复目标包括恢复独立生活能力、预防并发症、社会功能重建。主要治疗手段：物理治疗PT、作业治疗OT、言语治疗ST、心理康复。"),
        ("老年康复护理SOP", "sop",
         "老年康复护理标准流程：生命体征监测、压疮预防（每2小时翻身）、营养评估、深静脉血栓预防、呼吸道感染预防、跌倒风险评估。"),
        ("运动损伤康复方案", "research",
         "常见运动损伤：韧带损伤采用RICE原则（休息、冰敷、加压包扎、抬高患肢）；肌肉拉伤进行拉伸按摩与力量恢复训练。渐进性关节活动度训练和本体感觉训练辅助康复。"),
    ]
    out = []
    for t, c, s in samples:
        try:
            r = upload_text(text=s, title=t, category=c)
            out.append(r)
        except Exception as e: print(f"Seed error {t}: {e}")
    return {"seeded": len(out), "docs": out}
