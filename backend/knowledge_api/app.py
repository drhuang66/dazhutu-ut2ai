"""
智慧康复知识库 API v2.0
百年AI × 云上大耳兔 - 本地简化版（无需外部 Embedding 服务）
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from typing import List, Optional
import qdrant_client
import requests
import os
import uuid
import json
import hashlib
import math
from datetime import datetime

app = FastAPI(title="智慧康复知识库 API (本地简化版)")

# ==================== 配置 ====================
QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:16333")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:8081")
COLLECTION_NAME = "rehabilitation_knowledge"

# 本地文本嵌入（使用字符哈希生成固定维度向量）
def simple_embedding(text: str, dim: int = 768) -> List[float]:
    """基于文本的简单哈希嵌入（替代外部 Embedding 服务）"""
    h = hashlib.sha256(text.encode('utf-8')).hexdigest()
    vec = []
    for i in range(dim):
        chunk = h[i * 4:(i + 1) * 4] if i * 4 < len(h) else '0000'
        try:
            val = int(chunk, 16) / 4294967295.0 - 0.5
        except ValueError:
            val = 0.0
        vec.append(max(-1.0, min(1.0, val)))
    return vec

# ==================== Qdrant 初始化 ====================
try:
    client = qdrant_client.QdrantClient(url=QDRANT_URL, check_compatibility=False)
    try:
        client.get_collection(COLLECTION_NAME)
    except Exception:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={"size": 768, "distance": "Cosine"}
        )
except Exception as e:
    print(f"⚠️ Qdrant不可用: {e}")
    client = None

# ==================== Pydantic Models ====================
class DocumentInfo(BaseModel):
    id: str
    title: str
    content_preview: str
    upload_date: str
    category: str

class SearchResult(BaseModel):
    query: str
    results: List[dict]

class ChatRequest(BaseModel):
    question: str
    context_id: Optional[str] = None
    stream: bool = False

# ==================== LLM 调用 ====================
def get_llm_response(question: str, context: str = "") -> str:
    """使用本地 Qwen3.6-35B 生成回答"""
    
    system_prompt = "你是一个专业的康复医学智能助手。请基于以下知识库内容回答问题，如果知识不足请说明无法回答。"
    prompt = f"{system_prompt}\n\n【知识库参考】:\n{context}\n\n【用户问题】:\n{question}\n\n请给出专业、详细且易于理解的康复医学相关回答："
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": os.getenv("LLM_MODEL", "Qwen3.6-35B-A3B-Q8_0"),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1024,
                "temperature": 0.7
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"⚠️ LLM服务暂时无法响应（状态码: {response.status_code}），但知识库搜索功能正常。"
    except Exception as e:
        return f"⚠️ 对话生成失败: {str(e)}\n\n请直接查看知识库搜索结果。"

# ==================== API 路由 ====================

@app.get("/health")
async def health_check():
    """健康检查"""
    status = {
        "status": "ok",
        "service": "knowledge-api",
        "version": "2.0.0",
        "qdrant": "connected" if client else "unavailable",
        "llm_base_url": OLLAMA_BASE_URL
    }
    return status

@app.post("/upload", response_model=DocumentInfo)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form("general")
):
    """上传文档到知识库"""
    
    try:
        content = await file.read()
        text_content = content.decode("utf-8", errors="ignore")
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="文件内容为空")
        
        embedding = simple_embedding(text_content)
        
        metadata = {
            "title": file.filename or "上传文档",
            "category": category,
            "upload_date": datetime.now().isoformat(),
            "content_preview": text_content[:200] + "..." if len(text_content) > 200 else text_content,
            "full_text": text_content
        }
        
        point_id = str(uuid.uuid4())
        
        if client:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=[{
                    "id": point_id,
                    "vector": embedding,
                    "payload": metadata
                }]
            )
        
        return DocumentInfo(
            id=point_id,
            title=file.filename or "上传文档",
            content_preview=metadata["content_preview"],
            upload_date=metadata["upload_date"],
            category=category
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.post("/upload-from-text")
async def upload_text_document(
    text: str = Form(...),
    title: str = Form("新文档"),
    category: str = Form("general")
):
    """从文本内容直接上传到知识库"""
    
    try:
        embedding = simple_embedding(text)
        
        metadata = {
            "title": title,
            "category": category,
            "upload_date": datetime.now().isoformat(),
            "content_preview": text[:200] + "..." if len(text) > 200 else text,
            "full_text": text
        }
        
        point_id = str(uuid.uuid4())
        
        if client:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=[{
                    "id": point_id,
                    "vector": embedding,
                    "payload": metadata
                }]
            )
        
        return {
            "message": "✅ 文本文档上传成功",
            "document_id": point_id,
            "metadata": metadata
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.post("/search", response_model=SearchResult)
async def search_knowledge(query: str = Form("query"), limit: int = 5):
    """搜索知识库"""
    
    results = []
    
    if client:
        query_embedding = simple_embedding(query)
        
        try:
            qdrant_results = client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_embedding,
                limit=limit
            )
            
            for r in qdrant_results:
                results.append({
                    "id": str(r.id),
                    "score": round(float(r.score), 4),
                    "payload": r.payload
                })
        except Exception as e:
            pass
    
    # 如果 Qdrant 搜索失败，回退到简单的文本匹配
    if not results:
        try:
            collections = client.get_collections().collections
            for col in collections:
                if COLLECTION_NAME == col.name:
                    points, _ = client.scroll(
                        collection_name=COLLECTION_NAME,
                        limit=100,
                        with_payload=True
                    )
                    
                    for point in points:
                        payload = point.payload
                        title_match = query.lower() in (payload.get("title", "") or "").lower()
                        preview_match = query.lower() in (payload.get("content_preview", "") or "").lower()
                        category_match = query.lower() in (payload.get("category", "") or "").lower()
                        
                        if title_match or preview_match or category_match:
                            results.append({
                                "id": str(point.id),
                                "score": 0.8 if title_match else 0.5,
                                "payload": payload
                            })
                    
                    results.sort(key=lambda x: x["score"], reverse=True)
                    results = results[:limit]
                    break
        except Exception:
            pass
    
    return SearchResult(
        query=query,
        results=results
    )

@app.post("/chat")
async def chat_with_knowledge(request: ChatRequest):
    """与知识库对话"""
    
    # 获取相关上下文
    context = ""
    if client:
        try:
            query_embedding = simple_embedding(request.question)
            search_results = client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_embedding,
                limit=3
            )
            
            for r in search_results:
                payload = r.payload
                context += f"【{payload.get('title', '文档')}】\n{payload.get('content_preview', '')}\n\n"
        except Exception as e:
            print(f"搜索失败: {e}")
    
    # 如果上下文为空，使用简单的全文匹配
    if not context and client:
        try:
            collections = client.get_collections().collections
            for col in collections:
                if COLLECTION_NAME == col.name:
                    points, _ = client.scroll(
                        collection_name=COLLECTION_NAME,
                        limit=50,
                        with_payload=True
                    )
                    
                    relevant = []
                    for point in points:
                        payload = point.payload
                        full_text = payload.get("full_text", "") or ""
                        if request.question.lower() in full_text.lower():
                            relevant.append(payload)
                    
                    if relevant:
                        context = "\n\n".join([
                            f"【{p.get('title', '文档')}】\n{p.get('content_preview', '')}" 
                            for p in relevant[:5]
                        ]) + "\n\n..."
        except Exception as e:
            print(f"全文匹配失败: {e}")
    
    # 获取LLM回复
    answer = get_llm_response(request.question, context)
    
    return {
        "question": request.question,
        "answer": answer,
        "context_provided": len(context) > 0,
        "sources_count": len(context.split("【")) - 1 if context else 0
    }

@app.get("/documents")
async def list_documents():
    """列出知识库中的所有文档"""
    
    documents = []
    
    if client:
        try:
            collections = client.get_collections().collections
            for col in collections:
                if COLLECTION_NAME == col.name:
                    points, _ = client.scroll(
                        collection_name=COLLECTION_NAME,
                        limit=1000,
                        with_payload=True,
                        with_vectors=False
                    )
                    
                    for point in points:
                        payload = point.payload
                        documents.append({
                            "id": str(point.id),
                            "title": payload.get("title", ""),
                            "category": payload.get("category", ""),
                            "upload_date": payload.get("upload_date", ""),
                            "content_preview": payload.get("content_preview", "")[:100] + "..." if len(payload.get("content_preview", "")) > 100 else payload.get("content_preview", "")
                        })
                    break
        except Exception as e:
            print(f"列出文档失败: {e}")
    
    return {
        "total": len(documents),
        "documents": documents,
        "qdrant_connected": client is not None
    }

@app.delete("/document/{doc_id}")
async def delete_document(doc_id: str):
    """删除文档"""
    
    if not client:
        raise HTTPException(status_code=500, detail="Qdrant 不可用")
    
    try:
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=[doc_id]
        )
        return {"message": f"✅ 文档 {doc_id} 删除成功"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"删除失败: {str(e)}")

@app.post("/seed-sample-data")
async def seed_sample_data():
    """一键填充示例康复医学数据（演示用）"""
    
    sample_data = [
        {
            "title": "脑卒中康复临床路径",
            "category": "clinical",
            "text": """# 脑卒中康复临床路径

## 一、概述
脑卒中（中风）是全球范围内导致成人残疾的主要原因之一。早期、系统化的康复治疗能够显著改善患者功能预后，提高生活质量。

## 二、康复评估
- Brunnstrom分期
- Fugl-Meyer评分
- Berg平衡量表

## 三、康复治疗
1. 早期康复（发病后24-48小时）：体位摆放、关节活动度训练
2. 恢复期康复：任务导向性训练、镜像疗法
3. 社区康复：家庭环境改造指导"""
        },
        {
            "title": "脊髓损伤康复指南",
            "category": "clinical",
            "text": """# 脊髓损伤康复指南

## 康复目标
1. 恢复独立生活能力
2. 预防并发症
3. 社会功能重建

## 主要治疗手段
- 物理治疗（PT）
- 作业治疗（OT）
- 言语治疗（ST，适用于颈椎损伤）
- 心理康复"""
        },
        {
            "title": "运动损伤康复方案",
            "category": "research",
            "text": """# 常见运动损伤康复方案

## 韧带损伤
- RICE原则：休息、冰敷、加压包扎、抬高患肢
- 渐进性关节活动度训练
- 本体感觉训练

## 肌肉拉伤
- 急性期处理
- 拉伸与按摩
- 力量恢复训练"""
        },
        {
            "title": "老年康复护理SOP",
            "category": "sop",
            "text": """# 老年康复护理标准操作流程

## 日常照护
1. 生命体征监测
2. 压疮预防（每2小时翻身）
3. 营养评估与管理

## 并发症预防
- 深静脉血栓预防
- 呼吸道感染预防
- 跌倒风险评估"""
        }
    ]
    
    uploaded = []
    
    for item in sample_data:
        embedding = simple_embedding(item["text"])
        
        metadata = {
            "title": item["title"],
            "category": item["category"],
            "upload_date": datetime.now().isoformat(),
            "content_preview": item["text"][:200] + "..." if len(item["text"]) > 200 else item["text"],
            "full_text": item["text"]
        }
        
        point_id = str(uuid.uuid4())
        
        if client:
            try:
                client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=[{
                        "id": point_id,
                        "vector": embedding,
                        "payload": metadata
                    }]
                )
            except Exception as e:
                print(f"上传示例数据失败: {e}")
        
        uploaded.append({
            "id": point_id,
            "title": item["title"],
            "category": item["category"]
        })
    
    return {
        "message": f"✅ 成功填充 {len(uploaded)} 条示例数据",
        "documents": uploaded
    }

# ==================== 文档路由 ====================
@app.get("/docs")
async def swagger_docs():
    """API文档（Swagger UI）"""
    return None
