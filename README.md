# 紙札 Kamifuda

短い一言を、SNSやスライドに貼れる画像カード（1200×630）に変換する小さな Web アプリです。

Python / FastAPI / Pillow だけで動き、認証もデータベースも不要です。MIT ライセンスで公開しやすい構成にしています。

## できること

- 本文（最大200文字）と任意の出典から PNG カードを生成
- テーマ 3 種（Mist / Ink / Sun）
- ブラウザ上でプレビュー → PNG 保存

## 必要環境

- Python 3.11+
- 日本語フォント（推奨: `fonts-noto-cjk`。任意で `app/static/fonts/NotoSansJP.ttf` を置けます。未導入時はシステムフォントへフォールバックします）

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 起動

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8765 --reload
```

ブラウザで [http://127.0.0.1:8765](http://127.0.0.1:8765) を開きます。

ヘルスチェック: `GET /health`

## API

`POST /api/card`（`multipart/form-data`）

| フィールド | 必須 | 説明 |
|---|---|---|
| `text` | yes | 本文（1–200文字） |
| `attribution` | no | 出典・署名（最大60文字） |
| `theme` | no | `mist` / `ink` / `sun`（既定: `mist`） |

レスポンスは `image/png` です。

## ライセンス

MIT
