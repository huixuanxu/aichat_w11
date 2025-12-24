from google import genai

API_KEY = "AIzaSyDx1uSNYznEkCMc8fZFzrh03X1RhdAcsuM"
client = genai.Client(api_key=API_KEY)

print("--- 正在檢查你可以使用的模型清單 ---")
try:
    # 列出所有可用的模型
    for m in client.models.list():
        print(f"可用模型: {m.name}")
except Exception as e:
    print(f"無法取得清單，錯誤原因: {e}")