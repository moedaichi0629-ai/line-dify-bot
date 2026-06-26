# LINE × Dify AIチャットボット
# LINEでユーザーが送ったメッセージをDify APIに転送し、返答をLINEに返信する

import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage as LineTextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import requests
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

app = Flask(__name__)

# LINE Messaging APIの設定
configuration = Configuration(access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# Dify APIの設定
DIFY_API_KEY = os.getenv("DIFY_API_KEY")
DIFY_API_URL = os.getenv("DIFY_API_URL", "https://api.dify.ai/v1/chat-messages")


@app.route("/")
def index():
    # ヘルスチェック用。サーバーが動いているか確認するためのエンドポイント
    return "OK"


@app.route("/callback", methods=["POST"])
def callback():
    # LINEからWebhookリクエストが届いたときに呼ばれる
    # X-Line-Signature ヘッダーでリクエストの正当性を検証する（セキュリティ対策）
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        # 署名が一致しない場合は不正なリクエストとして拒否する
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    # テキストメッセージが届いたときに呼ばれる（スタンプや画像は無視される）

    # ユーザーが送ったテキストを取得する
    user_message = event.message.text

    # LINEのユーザーIDをDify APIのユーザー識別子として使う
    user_id = event.source.user_id

    # Dify APIにメッセージを送信して回答を受け取る
    reply_text = ask_dify(user_message, user_id)

    # LINEにメッセージを返信する
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[LineTextMessage(type="text", text=reply_text)],
            )
        )


def ask_dify(user_message: str, user_id: str) -> str:
    # Dify APIにユーザーのメッセージを送り、回答テキストを返す関数

    # リクエストヘッダーにAPIキーを設定する
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json",
    }

    # Dify APIに送るデータ
    payload = {
        "inputs": {},
        "query": user_message,          # ユーザーが送った文章
        "response_mode": "blocking",    # 回答が完成するまで待つ同期モード
        "user": user_id,                # ユーザーを識別するID（LINEのユーザーIDを使用）
    }

    try:
        # Dify APIにPOSTリクエストを送信する（タイムアウトは30秒）
        response = requests.post(DIFY_API_URL, headers=headers, json=payload, timeout=30)

        # HTTPエラー（4xx, 5xx）が返ってきた場合は例外を発生させる
        response.raise_for_status()

        # レスポンスをJSON形式で解析する
        data = response.json()

        # Difyのレスポンスから回答テキストを取り出して返す
        return data.get("answer", "回答を取得できませんでした。")

    except Exception:
        # 何らかのエラーが発生した場合はエラーメッセージを返す
        return "エラーが発生しました。少し時間をおいて試してください。"


if __name__ == "__main__":
    # サーバーを起動する（PORTが環境変数に設定されていればそれを使う）
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
