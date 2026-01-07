import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

# --- 1. 初始化與安全設定 ---
load_dotenv() 
API_KEY = os.getenv("GEMINI_API_KEY")

# 若環境變數未設定，給予預設值以防啟動崩潰
if not API_KEY:
    API_KEY = "TEMP_KEY" 

client = genai.Client(api_key=API_KEY)

# 🌟  請把測試程式碼貼在這裡 (CHARACTER_SETTING 之前)
try:
    print("🔍 正在檢查您的 API Key 權限...")
    # 注意：SDK 1.56.0 版的 list 語法
    for m in client.models.list():
        print(f"✅ 可用模型: {m.name}")
except Exception as e:
    print(f"❌ 無法列出模型，請檢查 Key 是否正確或 API 是否啟用: {e}")

# --- 2. 陪伴者性格與記憶管理 ---

CHARACTER_SETTING = """
# Role
你是一位陪伴者。你的特質是溫暖、成熟且富有同理心，擅長傾聽並給予情感支持。

# Style & Tone
1. 語氣：親切且自然，像是認識很久的老友或是體貼的大人。
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
# 用於儲存對話 Session
chat_sessions = {}

# --- 3. 初始化 FastAPI ---
# 🌟 redirect_slashes=False 是為了防止 Vercel 強制跳轉導致 POST 變 GET
app = FastAPI(redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 測試用帳密
FAKE_USERS_DB = {"user123": "password123"}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

class ChatRequest(BaseModel):
    message: str

# --- 4. API 路由定義 (雙路由策略) ---

# 診斷用路由：解決空白畫面問題
@app.get("/api/health")
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running!"}

# 登入 API：改成標準 @app.post
@app.post("/api/login")
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    
    if username in FAKE_USERS_DB and FAKE_USERS_DB[username] == password:
        return {"access_token": f"token_{username}", "token_type": "bearer"}
    
    raise HTTPException(status_code=400, detail="帳號或密碼錯誤")

# 聊天 API
@app.post("/api/chat")
@app.post("/chat")
async def chat(request: ChatRequest, token: str = Depends(oauth2_scheme)):
    try:
        # 🌟 修改點 1：如果 token 不在紀錄中，使用 1.56.0 正確語法建立 chat session
        if token not in chat_sessions:
            print(f"📢 找不到 Session，正在為 {token} 重新建立對話...")
            # 使用 client.chats.create 並注入性格設定 (system_instruction)
            chat_sessions[token] = client.chats.create(
                model="gemini-3-flash-preview",
                config=types.GenerateContentConfig(
                    system_instruction=CHARACTER_SETTING,
                    temperature=0.7
                )
            )
        
        current_chat = chat_sessions[token]
        
        # 🌟 修改點 2：調用 send_message 發送用戶訊息
        response = current_chat.send_message(request.message)
        
        # 返回 AI 生成的純文字回覆
        return {"reply": response.text}
        
    except Exception as e:
        # 這裡會印出真正的詳細錯誤 (例如: API Key 限制、網路連線等)
        print(f"❌ 發生詳細錯誤: {type(e).__name__}: {str(e)}")
        
        # 針對常見的 403 錯誤提供更精確的終端機提示
        if "403" in str(e):
            print("⚠️ 提示：這通常是 Google Cloud 的『網站限制』阻擋了 localhost。請將限制改為『無』。")
            
        return {"reply": "抱歉，我現在思緒有點亂，可以重新說一次嗎？"}

# 本地 / Render 執行
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)



