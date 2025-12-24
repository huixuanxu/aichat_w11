import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

# --- 1. 安全性設定：隱藏 API 金鑰 ---
# 從 .env 檔案讀取金鑰，避免將私密資訊直接寫在程式碼中
load_dotenv() 
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("錯誤：找不到 API Key，請檢查 backend/.env 檔案設定")

# 初始化 Gemini 3 客戶端
client = genai.Client(api_key=API_KEY)

# --- 2. 陪伴者性格與記憶管理 ---
CHARACTER_SETTING = """
# Role
你是一位陪伴者。你的特質是溫暖、成熟且富有同理心，擅長傾聽並給予情感支持。

# Style & Tone
1. 語氣：親切且自然，像是認識很久的老友。
2. 用詞：多使用溫暖的詞彙（如：辛苦了、我陪你、沒關係）。
3. 表情：適時使用溫馨的表情符號（如：😊, ✨, 🌿, ☕）。

# Constraints & Guidelines
1. **分段與換行**：
   - 嚴禁所有文字擠成一大塊。
   - 每 2-3 句話或是轉換話題時，必須使用「兩個換行」來分開段落。
2. **字數限制**：
   - 一般對話回覆建議在 100 字以內。
3. **條列式規則**：
   - 如果內容需要超過 100 字，請「強迫」使用 Markdown 條列式（* 或 1.）呈現。
4. **Markdown 語法**：
   - 重要詞彙可以使用 **粗體**。

# Example
- 使用者：我今天工作被老闆罵了，好難過。
- AI：抱抱你，聽起來真的委屈了。辛苦努力了一整天卻換來指責，難過是很正常的。今晚先別想工作了，泡個熱水澡休息一下好嗎？我會一直在這裡陪你。✨
不管發生什麼事，我都會在這裡陪著你。✨
"""

# 使用字典儲存對話實例 (Chat Session)
# key: token (使用者標記), value: Google 的 Chat 物件
chat_sessions = {}

# --- 3. 初始化 FastAPI 應用程式 ---
app = FastAPI()

# 設定跨來源資源共享 (CORS)，讓前端網頁 (localhost:5173) 可以安全連線
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模擬使用者資料庫與認證系統
FAKE_USERS_DB = {"user123": "password123"}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# 定義前端請求的 JSON 資料格式
class ChatRequest(BaseModel):
    message: str

# --- 4. API 路由定義 ---

# 登入 API：驗證帳密並發放暫時的 Token
@app.post("/api/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username in FAKE_USERS_DB and FAKE_USERS_DB[form_data.username] == form_data.password:
        return {"access_token": f"token_{form_data.username}", "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="帳號或密碼錯誤")

# 聊天 API：處理對話並維護記憶
@app.post("/api/chat")
async def chat(request: ChatRequest, token: str = Depends(oauth2_scheme)):
    try:
        # 🌟 記憶功能實現：檢查此使用者是否已有開啟中的對話
        if token not in chat_sessions:
            print(f"--- 🆕 為使用者 {token} 初始化新對話 ---")
            chat_sessions[token] = client.chats.create(
                model="gemini-3-flash-preview", 
                config=types.GenerateContentConfig(
                    system_instruction=CHARACTER_SETTING
                )
            )
        
        current_chat = chat_sessions[token]
        
        # 發送目前訊息，Gemini SDK 會自動在後台處理歷史對話 (Context)
        response = current_chat.send_message(request.message)
        
        # 🌟 相容性修正：偵測 SDK 的屬性名稱 (部分版本為 history，部分為 _history)
        history_count = 0
        if hasattr(current_chat, 'history'):
            history_count = len(current_chat.history)
        elif hasattr(current_chat, '_history'):
            history_count = len(current_chat._history)
            
        print(f"--- ✅ AI 回覆成功 (對話歷史數: {history_count}) ---")
        
        return {"reply": response.text}
        
    except Exception as e:
        # 當發生錯誤時印出詳細資訊，並回傳友善的訊息給前端
        print(f"--- ❌ 發生錯誤: {e} ---")
        return {"reply": f"系統診斷訊息: {str(e)[:50]}... 請檢查 API 或模型狀態。"}

# --- 5. 啟動伺服器 ---
if __name__ == "__main__":
    import uvicorn
    # 執行在 8000 埠，reload=True 代表修改程式碼存檔後會自動重啟
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)