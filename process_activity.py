import os
import json
import google.generativeai as genai
from datetime import datetime

# 1. 設定環境變數 (由 GitHub Secrets 提供)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# 2. 定義 AI 指令 (即您剛才測試成功的 Prompt)
SYSTEM_INSTRUCTION = """
你是一位「綠色森林守護者」。請辨識照片是否符合當日減塑主題。
僅回傳嚴格的 JSON 格式：
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
    
    # 模擬讀取圖片
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    contents = [
        f"今日活動主題：{theme}",
        {"mime_type": "image/jpeg", "data": image_data}
    ]
    
    response = model.generate_content(contents)
    
    # 確保只擷取 JSON 部分
    result_text = response.text.strip().replace("```json", "").replace("
```", "")
    return json.loads(result_text)

def update_database(user_id, result):
    db_path = "data/progress.json"
    
    # 讀取現有資料
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    # 更新使用者進度
    if user_id not in data:
        data[user_id] = {"total_growth": 0, "history": []}
    
    if result["status"] == "success":
        data[user_id]["total_growth"] += result["tree_growth"]
        data[user_id]["history"].append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "reason": result["reason"]
        })

    # 寫回 JSON 檔案 (GitHub 儲存層)
    os.makedirs("data", exist_ok=True)
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # 這裡的參數通常由 GitHub Actions 或 Webhook 傳入
    # 範例：處理一位使用者的上傳
    test_user = "USER_LINE_ID_123"
    current_theme = "裸妝運動" 
    image_to_process = "temp_upload.jpg"
    
    try:
        analysis_result = analyze_image(image_to_process, current_theme)
        update_database(test_user, analysis_result)
        print(f"處理成功：{analysis_result['reason']}")
    except Exception as e:
        print(f"處理失敗：{e}")
