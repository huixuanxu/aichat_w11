import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

function Chat() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef(null);

  // 當 messages 陣列更新時，自動執行滾動動作，確保看到最新訊息
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const token = localStorage.getItem('token');
    
    // 1. 將使用者的訊息加入對話框
    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    const currentInput = input; // 暫存目前的輸入
    setInput('');
    setIsLoading(true);

   try {
    const API_BASE_URL = window.location.origin; // 🌟 自動獲取
    const res = await axios.post(`${API_BASE_URL}/api/chat`,
      { message: currentInput },
      { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // 3. 取得 AI 回應並加入對話紀錄
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.reply }]);
    } catch (err) {
      console.error("聊天連線出錯：", err);
      // 如果是 401 錯誤，通常是 Token 過期
      if (err.response?.status === 401) {
        alert("登入逾時，請重新登入");
      } else {
        alert("連線中斷，請稍後再試");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // 莫蘭迪暖色調調色盤
  const colors = {
    pageBg: '#E5E2DF',      // 莫蘭迪深米灰
    containerBg: '#F8F6F4', // 淺奶茶色
    userBubble: '#D9A78B',   // 莫蘭迪暖橙
    aiBubble: '#98A69F',     // 莫蘭迪湖水綠
    text: '#545454',         // 深灰色文字
    inputBorder: '#C9C2BC'   // 輸入框邊框色
  };

  return (
    <div style={{ 
      backgroundColor: colors.pageBg, 
      height: '100vh', 
      width: '100vw',
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      margin: 0,
      padding: 0,
      boxSizing: 'border-box',
      overflow: 'hidden', 
      position: 'fixed', 
      top: 0,
      left: 0
    }}>
      
      <style>{`
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
      `}</style>

      {/* 對話主視窗 */}
      <div style={{ 
        width: '90%', 
        maxWidth: '850px', 
        height: '85vh', 
        backgroundColor: colors.containerBg,
        borderRadius: '35px', 
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '20px 20px 60px #bebebe, -20px -20px 60px #ffffff',
        overflow: 'hidden', 
        border: '1px solid rgba(255,255,255,0.3)',
        position: 'relative'
      }}>
        
        {/* 頂部標題 */}
        <div style={{ 
          padding: '20px', 
          textAlign: 'center', 
          background: 'rgba(255,255,255,0.5)', 
          borderBottom: '1px solid #E0DCD9',
          backdropFilter: 'blur(5px)'
        }}>
          <h2 style={{ margin: 0, color: colors.text, fontWeight: '400', fontSize: '1.1rem', letterSpacing: '2px' }}>
            ✨ 專屬夥伴 ‧ 溫暖陪伴
          </h2>
        </div>

        {/* 訊息顯示區 */}
        <div className="hide-scrollbar" style={{ 
          flex: 1, 
          overflowY: 'auto', 
          padding: '30px',
          display: 'flex',
          flexDirection: 'column',
          gap: '20px'
        }}>
          {messages.map((msg, i) => (
            <div key={i} style={{ 
              display: 'flex', 
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start'
            }}>
              <div style={{
                maxWidth: '75%',
                padding: '14px 20px',
                borderRadius: msg.role === 'user' ? '22px 22px 5px 22px' : '22px 22px 22px 5px',
                backgroundColor: msg.role === 'user' ? colors.userBubble : colors.aiBubble,
                color: '#FFFFFF',
                boxShadow: '4px 4px 12px rgba(0,0,0,0.06)',
                lineHeight: '1.6',
                fontSize: '15.5px',
                whiteSpace: 'pre-wrap', 
                wordBreak: 'break-word',
                overflowWrap: 'break-word'
              }}>
                {msg.content}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
              <div style={{ color: colors.aiBubble, fontSize: '13px', fontStyle: 'italic' }}>
                夥伴正在思考中...
              </div>
            </div>
          )}
          
          <div ref={scrollRef} />
        </div>

        {/* 底部輸入區 */}
        <div style={{ 
          padding: '25px 30px', 
          background: 'rgba(255,255,255,0.5)', 
          borderTop: '1px solid #E0DCD9' 
        }}>
          <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
            <input 
              value={input} 
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="說些悄悄話吧..."
              style={{ 
                flex: 1, 
                padding: '14px 22px', 
                borderRadius: '30px', 
                border: `1px solid ${colors.inputBorder}`,
                backgroundColor: 'rgba(255, 255, 255, 0.51)',
                outline: 'none',
                fontSize: '15px',
                color: colors.text,
                boxShadow: 'inset 2px 2px 5px rgba(0,0,0,0.03)'
              }}
            />
            <button 
              onClick={sendMessage}
              style={{ 
                backgroundColor: colors.userBubble, 
                color: 'white', 
                fontSize: '15px',
                border: 'none', 
                padding: '14px 28px', 
                borderRadius: '30px', 
                cursor: 'pointer',
                fontWeight: 'bold',
                boxShadow: '0 4px 12px rgba(217,167,139,0.3)',
                transition: 'all 0.2s ease'
              }}
            >
              傳送
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}

export default Chat;