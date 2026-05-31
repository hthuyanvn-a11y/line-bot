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
  user_id = event.source.user_id
    group_id = getattr(event.source, 'group_id', None)
    
    # 這裡填入你核准過的群組 ID。如果目前還沒有，先留空像下面這樣
    APPROVED_GROUPS = [
        "C1234567890abcdef...",  # 日後有新群組，就把 C 開頭的 ID 填在這裡
    ]
    
    # 情況一：如果是群組訊息，但這個群組你還沒核准，就直接裝死
    if group_id and group_id not in APPROVED_GROUPS:
        return "OK"
        
    # 情況二：如果是私訊，但對方不是你（你在 LINE 必須是這個官方帳號的「對話管理員」或創造者）
    # 為了不要鎖死你，我們可以先不鎖私訊，或者等你在 Logs 查到你的 U 開頭 ID 後再補上：
    # if not group_id and user_id != "你的U開頭ID": return "OK"
    response = client.models.generate_content(model='gemini-2.5-flash', contents=event.message.text)
    reply_text = response.text
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
