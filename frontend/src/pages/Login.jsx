import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault(); // 防止網頁刷新
    setIsLoading(true);
    console.log("嘗試登入中..."); // 偵錯用

    // 使用 URLSearchParams 確保符合 FastAPI 要求的 Form Data 格式
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    try {
      const response = await axios.post('http://127.0.0.1:8000/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      console.log("登入成功！");
      localStorage.setItem('token', response.data.access_token);
      navigate('/chat'); 
    } catch (error) {
      console.error("登入出錯了：", error.response?.data || error.message);
      alert('帳號或密碼錯誤，請檢查後端是否開啟');
    } finally {
      // ✨ 重要：無論成功或失敗，都要關閉載入狀態，否則按鈕會一直卡在驗證中
      setIsLoading(false); 
    }
  };

  return (
    <div style={{ backgroundColor: '#E5E2DF', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ width: '350px', padding: '40px', backgroundColor: '#F8F6F4', borderRadius: '30px', boxShadow: '20px 20px 60px #bebebe', textAlign: 'center' }}>
        <h2 style={{ color: '#545454' }}>歡迎回來</h2>
        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginTop: '20px' }}>
          <input 
            placeholder="帳號" 
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{ padding: '12px', borderRadius: '20px', border: '1px solid #C9C2BC' }}
          />
          <input 
            type="password" 
            placeholder="密碼" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ padding: '12px', borderRadius: '20px', border: '1px solid #C9C2BC' }}
          />
          <button 
            type="submit" 
            disabled={isLoading}
            style={{ 
              backgroundColor: '#D9A78B', color: 'white', border: 'none', padding: '12px', borderRadius: '20px', cursor: 'pointer',
              opacity: isLoading ? 0.7 : 1
            }}
          >
            {isLoading ? '驗證中...' : '登入'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;