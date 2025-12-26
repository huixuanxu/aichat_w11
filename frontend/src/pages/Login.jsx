import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

const handleLogin = async (e) => {
    e.preventDefault(); 
    setIsLoading(true);

    try {
        const API_BASE_URL = window.location.origin;
        const response = await axios.post(`${API_BASE_URL}/api/login`, 
            new URLSearchParams({ 'username': username, 'password': password }), 
            { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
        );
        
        localStorage.setItem('token', response.data.access_token);
        navigate('/chat'); 
    } catch (error) {
        // 這裡可以增加對 401 或 500 錯誤的區分
        console.error("登入出錯了：", error.response?.data || error.message);
        alert('登入失敗：請確認帳號密碼，或檢查伺服器狀態');
    } finally {
        setIsLoading(false); 
    }
};

  return (
    <div style={{ backgroundColor: '#E5E2DF', height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ width: '350px', padding: '40px', backgroundColor: '#F8F6F4', borderRadius: '30px', boxShadow: '20px 20px 60px #bebebe', textAlign: 'center' }}>
        <h2 style={{ color: '#545454', fontWeight: '400', letterSpacing: '2px' }}>歡迎回來</h2>
        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginTop: '20px' }}>
          <input 
            placeholder="帳號" 
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{ padding: '12px 20px', borderRadius: '25px', border: '1px solid #C9C2BC', outline: 'none' }}
          />
          <input 
            type="password" 
            placeholder="密碼" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ padding: '12px 20px', borderRadius: '25px', border: '1px solid #C9C2BC', outline: 'none' }}
          />
          <button 
            type="submit" 
            disabled={isLoading}
            style={{ 
              backgroundColor: '#D9A78B', color: 'white', border: 'none', padding: '12px', borderRadius: '25px', cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(217,167,139,0.3)',
              fontWeight: 'bold',
              transition: 'all 0.2s ease',
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