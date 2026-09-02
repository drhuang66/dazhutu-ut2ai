import { useState } from 'react';
import { uploadDocument, listDocuments, deleteDocument, searchKnowledge, chatWithKnowledge } from '../lib/api';

export default function Home() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [chatInput, setChatInput] = useState('');
  const [chatResult, setChatResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  // 加载文档列表
  const loadDocuments = async () => {
    try {
      setLoading(true);
      const response = await listDocuments();
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('加载文档失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 上传文档
  const handleUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const file = formData.get('file') as File;
    const category = formData.get('category') as string;

    if (!file) return;

    try {
      setUploading(true);
      await uploadDocument(file, category);
      loadDocuments();
      (e.target as HTMLFormElement).reset();
      alert('文档上传成功！');
    } catch (error) {
      console.error('上传失败:', error);
      alert('上传失败，请重试');
    } finally {
      setUploading(false);
    }
  };

  // 搜索知识
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      setLoading(true);
      const response = await searchKnowledge(searchQuery);
      setDocuments(response.data.results || []);
    } catch (error) {
      console.error('搜索失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 对话
  const handleChat = async () => {
    if (!chatInput.trim()) return;

    try {
      setLoading(true);
      const response = await chatWithKnowledge(chatInput);
      setChatResult(response.data);
    } catch (error) {
      console.error('对话失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 删除文档
  const handleDelete = async (docId: string) => {
    if (!confirm('确定要删除这个文档吗？')) return;

    try {
      await deleteDocument(docId);
      loadDocuments();
      alert('文档已删除');
    } catch (error) {
      console.error('删除失败:', error);
      alert('删除失败，请重试');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* 顶部导航 */}
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-indigo-600 flex items-center gap-2">
            🏛️ 百年AI - 智慧康复知识库
          </h1>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="container mx-auto px-4 py-8">
        {/* 文档上传 */}
        <section className="mb-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">📤 上传知识库文档</h2>
          <form onSubmit={handleUpload} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">文档分类</label>
                <select
                  name="category"
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                  defaultValue="general"
                >
                  <option value="general">通用康复知识</option>
                  <option value="clinical">临床路径</option>
                  <option value="research">科研教学</option>
                  <option value="sop">SOP流程</option>
                </select>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">选择文件</label>
                <input
                  type="file"
                  name="file"
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                  accept=".pdf,.doc,.docx,.txt,.md"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={uploading}
              className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
            >
              {uploading ? '上传中...' : '📎 上传到知识库'}
            </button>
          </form>
        </section>

        {/* 搜索知识 */}
        <section className="mb-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">🔍 知识库智能搜索</h2>
          <div className="flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="输入查询关键词..."
              className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button
              onClick={handleSearch}
              disabled={loading || !searchQuery.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading ? '搜索中...' : '🔍 搜索'}
            </button>
          </div>
        </section>

        {/* AI对话 */}
        <section className="mb-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">🤖 知识库智能问答</h2>
          <div className="space-y-4">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="问我任何康复医学相关的问题..."
              className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 text-lg"
              onKeyDown={(e) => e.key === 'Enter' && handleChat()}
            />
            <button
              onClick={handleChat}
              disabled={loading || !chatInput.trim()}
              className="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white py-3 rounded-lg hover:from-green-600 hover:to-emerald-700 transition-all font-semibold disabled:opacity-50"
            >
              {loading ? '🤔 AI思考中...' : '💬 提问'}
            </button>
          </div>

          {/* 对话结果 */}
          {chatResult && (
            <div className="mt-6 space-y-4">
              <div className="bg-indigo-50 rounded-lg p-4">
                <h3 className="font-semibold text-indigo-700 mb-2">📝 我的问题：</h3>
                <p className="text-gray-800">{chatResult.question}</p>
              </div>
              
              <div className="bg-green-50 rounded-lg p-4">
                <h3 className="font-semibold text-green-700 mb-2">🤖 AI回答：</h3>
                <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">{chatResult.answer}</p>
              </div>

              {chatResult.sources?.length > 0 && (
                <div className="bg-yellow-50 rounded-lg p-4">
                  <h3 className="font-semibold text-yellow-700 mb-2">📚 引用来源：</h3>
                  <ul className="list-disc list-inside text-gray-600">
                    {chatResult.sources.map((source: string, index: number) => (
                      <li key={index}>{source}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </section>

        {/* 文档列表 */}
        <section className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">📋 知识库文档</h2>
          {documents.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg">暂无文档</p>
              <p className="text-sm mt-2">请上传康复医学相关文档到知识库</p>
            </div>
          ) : (
            <div className="space-y-3">
              {documents.map((doc: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                  <div>
                    <h3 className="font-medium text-gray-800">{doc.payload?.title || doc.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">
                      分类: {doc.payload?.category || 'general'} | 
                      上传于: {doc.payload?.upload_date || '未知时间'}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDelete(doc.id || doc.payload?.title)}
                    className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                  >
                    删除
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      {/* 底部 */}
      <footer className="bg-white border-t py-4 mt-8">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>智慧康复解决方案 v2.0 | 百年AI × 云上大耳兔</p>
        </div>
      </footer>
    </div>
  );
}
