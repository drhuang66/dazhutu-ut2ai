import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export const api = axios.create({
  baseURL: API_BASE,
});

// 上传文档
export const uploadDocument = async (file: File, category: string) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('category', category);
  
  return api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

// 搜索知识库
export const searchKnowledge = async (query: string, limit: number = 5) => {
  return api.post('/search', { query, limit });
};

// 与知识库对话
export const chatWithKnowledge = async (question: string, contextId?: string) => {
  return api.post('/chat', { question, context_id: contextId });
};

// 列出文档
export const listDocuments = async () => {
  return api.get('/documents');
};

// 删除文档
export const deleteDocument = async (docId: string) => {
  return api.delete(`/document/${docId}`);
};
