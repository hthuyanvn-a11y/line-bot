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
    
    # 這裡填入你核准過的群組 ID。如果目前沒有，就先維持這樣
    APPROVED_GROUPS = [
        "C1234567890abcdef...", 
    ]
    
    # 防護鎖：如果是群組訊息，且不在核准名單內，直接已讀不回，不執行任何後續程式
    if group_id and group_id not in APPROVED_GROUPS:
        return "OK"
        
    try:
        # 呼叫 Gemini 產生回覆
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=event.message.text
        )
        reply_text = response.text
        
        # 用最安全、不會因為漏掉 import 報錯的官方內建方式回覆文字
        from linebot.models import TextSendMessage
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        
    except Exception as e:
        print(f"發生錯誤: {e}")
        return "OK"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
