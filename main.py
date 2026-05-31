from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from google import genai
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET"))

client = genai.Client()
@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    group_id = getattr(event.source, 'group_id', None)
    
  # 關鍵的一行：如果這是在群組裡，直接把 ID 顯示在後台 Logs
    if group_id:
        print(f"DEBUG_GROUP_ID: {group_id}")
    
    APPROVED_GROUPS = [
        "Cb83e12539de8e31cc5e11783389ed646", 
    ]
    if group_id and group_id not in APPROVED_GROUPS:
        return "OK"
        
try:
        from linebot.models import TextSendMessage
        
        # --- 新增關鍵字限制 ---
        # 只有訊息內容包含「分析」兩個字，才會呼叫 Gemini
        if "分析" not in event.message.text:
        return "OK"
    ```
    （確保 `return` 前面有正確的四個空格縮排）

如果還是報錯，請點擊 `image_a68980.jpg` 畫面上的 **「deploy logs」**，然後把那裡顯示的錯誤訊息截圖給我看，我馬上就能告訴你哪一行出錯了！
        
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=event.message.text
        )
        reply_text = response.text
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    except Exception as e:
        print(f"Error: {e}")
        return "OK"
