# LINE × Dify AIチャットボット

LINEで送ったメッセージをDify AIに転送し、AIの回答をLINEに返信するチャットボットです。

## 動作フロー

```
ユーザー → LINE → Webhook → Flask (app.py) → Dify API → Flask → LINE → ユーザー
```

## 必要なもの

- Python 3.8以上
- LINE Developersアカウント（無料）
- Difyアカウントと作成済みのアプリ

## セットアップ手順

### 1. ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example` をコピーして `.env` ファイルを作成します。

```bash
cp .env.example .env
```

`.env` を開いて各値を設定してください。

| 変数名 | 取得場所 |
|--------|----------|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Developers > チャネル > Messaging API設定 > チャネルアクセストークン |
| `LINE_CHANNEL_SECRET` | LINE Developers > チャネル > チャネル基本設定 > チャネルシークレット |
| `DIFY_API_KEY` | Dify > アプリ > APIアクセス > APIキー |
| `DIFY_API_URL` | そのまま使用（変更不要） |

### 3. サーバーの起動

```bash
python app.py
```

### 4. ngrokで外部公開（ローカル開発時）

LINEのWebhookはHTTPSのURLが必要です。ローカル開発では[ngrok](https://ngrok.com/)を使います。

```bash
ngrok http 5000
```

表示された `https://xxxxxxxx.ngrok.io` をコピーしておきます。

### 5. LINE DevelopersでWebhook URLを設定

1. [LINE Developers](https://developers.line.biz/) にログイン
2. チャネルを選択 > **Messaging API設定**
3. **Webhook URL** に `https://xxxxxxxx.ngrok.io/callback` を入力
4. **Webhookの利用** をオンにする
5. **検証** ボタンで接続確認

## ファイル構成

```
line-dify-bot/
├── app.py            # メインプログラム
├── requirements.txt  # 必要なライブラリ一覧
├── .env.example      # 環境変数のサンプル
├── .env              # 環境変数（自分で作成・Gitに含めない）
└── README.md         # このファイル
```

## 本番環境へのデプロイ

以下のサービスに無料でデプロイできます。

- [Render](https://render.com/)
- [Railway](https://railway.app/)
- [Heroku](https://heroku.com/)

デプロイ後、Webhook URLをそのサービスのURLに変更してください。

## 注意事項

- `.env` ファイルはGitに含めないでください（APIキーが漏洩します）
- `line-bot-sdk` のバージョンは `2.x` を使用しています
