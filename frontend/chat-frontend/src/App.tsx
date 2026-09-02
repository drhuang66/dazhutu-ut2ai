import { useState } from 'react';
import axios from 'axios';

const API_BASE = process.env.VITE_API_URL || 'http://127.0.0.1:8000';

export default function App() {
  const [messages, setMessages] = useState<any[]>([
    { role: 'assistant', content: '你好！我是云上大耳兔 🐰，你的康复医学助手。有什么可以帮你的吗？' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    // 添加用户消息
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/chat`, { question: input });
      
      // 添加AI回复
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data.answer 
      }]);
    } catch (error) {
      console.error('发送失败:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: '抱歉，系统出现了一些问题。请稍后重试。' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-purple-50 to-pink-50">
      {/* 顶部 */}
      <header className="bg-white shadow-sm p-4 text-center">
        <h1 className="text-xl font-bold text-purple-600">🐰 云上大耳兔</h1>
        <p className="text-sm text-gray-500">康复医学智能助手</p>
      </header>

      {/* 聊天区域 */}
      <main className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-lg p-4 ${
              msg.role === 'user' 
                ? 'bg-purple-500 text-white' 
                : 'bg-white shadow-md'
            }`}>
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 rounded-lg p-3">
              <p className="text-sm text-gray-500">🤔 思考中...</p>
            </div>
          </div>
        )}
      </main>

      {/* 输入区域 */}
      <footer className="bg-white border-t p-4">
        <div className="flex gap-2 max-w-4xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="输入康复医学相关问题..."
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-6 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors disabled:opacity-50"
          >
            📨 发送
          </button>
        </div>
      </footer>
    </div>
  );
}
