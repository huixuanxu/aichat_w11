import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

# --- 1. 安全性設定 ---
load_dotenv() 
# Vercel 環境會直接抓取後台設定的 Key
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    # 這裡稍微改寫，避免在部署時因為找不到檔案而崩潰
    API_KEY = "TEMP_KEY" 

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

chat_sessions = {}

# --- 3. 初始化 FastAPI ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FAKE_USERS_DB = {"user123": "password123"}
# 重要：這裡的路徑要跟前端呼叫的 /api/login 對齊
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

class ChatRequest(BaseModel):
    message: str

# --- 4. API 路由定義 ---

@app.post("/api/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # 確保這裡的邏輯與 FAKE_USERS_DB 匹配
    if form_data.username in FAKE_USERS_DB and FAKE_USERS_DB[form_data.username] == form_data.password:
        return {"access_token": f"token_{form_data.username}", "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="帳號或密碼錯誤")

@app.post("/api/chat")
async def chat(request: ChatRequest, token: str = Depends(oauth2_scheme)):
    try:
        if token not in chat_sessions:
            chat_sessions[token] = client.chats.create(
                model="gemini-1.5-flash", # 改用更穩定的模型名稱
                config=types.GenerateContentConfig(
                    system_instruction=CHARACTER_SETTING
                )
            )
        
        current_chat = chat_sessions[token]
        response = current_chat.send_message(request.message)
        
        return {"reply": response.text}
        
    except Exception as e:
        print(f"Error: {e}")
        return {"reply": "我現在有點累了，可以稍後再跟我說話嗎？😊"}

# Vercel 部署不需要 if __name__ == "__main__" 這段，但留著也沒關係

