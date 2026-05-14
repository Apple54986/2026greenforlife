import os
import json
import google.generativeai as genai
from datetime import datetime
# 設定 Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
# 定義 AI 辨識指令
SYSTEM_INSTRUCTION = """
你是一位「綠色森林守護者」。請辨識照片是否符合當日減塑主題。
僅回傳嚴格的 JSON 格式:
{
"status": "success" 或 "fail",
"reason": "繁體中文鼓勵話語",
"tree_growth": 20 或 0
}
"""

def analyze_image(image_path, theme):
model = genai.GenerativeModel(
model_name="gemini-1.5-flash",
system_instruction=SYSTEM_INSTRUCTION
)
with open(image_path, "rb") as f:
image_data = f.read()
contents = [
f"今日活動主題:{theme}",
{"mime_type": "image/jpeg", "data": image_data}

]
response = model.generate_content(contents)
result_text = response.text.strip().replace("```json", "").replace("```", "")
return json.loads(result_text)
def update_database(user_id, result):
db_path = "data/progress.json"
if os.path.exists(db_path):
with open(db_path, "r", encoding="utf-8") as f:
data = json.load(f)
else:
data = {}
if user_id not in data:
data[user_id] = {"total_growth": 0, "history": []}
if result["status"] == "success":
data[user_id]["total_growth"] += result["tree_growth"]
data[user_id]["history"].append({
"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
"reason": result["reason"],
"points": result["tree_growth"]
})
os.makedirs("data", exist_ok=True)
with open(db_path, "w", encoding="utf-8") as f:
json.dump(data, f, ensure_ascii=False, indent=2)
if __name__ == "__main__":
# 測試用範例 (正式運作時可由 Actions 傳入環境變數)
USER_ID = os.getenv("USER_ID", "TEST_USER")
THEME = os.getenv("ACTIVITY_THEME", "環保杯")
IMAGE_PATH = "temp_upload.jpg"
if os.path.exists(IMAGE_PATH):
try:
res = analyze_image(IMAGE_PATH, THEME)
update_database(USER_ID, res)
print(f"Success: {res['reason']}")
except Exception as e:
print(f"Error: {e}")

else:
print("Waiting for image upload...")
