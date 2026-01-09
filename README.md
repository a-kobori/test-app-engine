# GCP認証付きTODOアプリケーション

Identity-Aware Proxy (IAP) を使用してGCPプロジェクトメンバーのみがアクセス可能なWebアプリケーション

## 技術スタック

- フロントエンド: HTML + HTMX
- バックエンド: Python 3.12 + Flask
- データベース: Firestore (Native mode)
- 認証: Identity-Aware Proxy (IAP)
- ホスティング: App Engine Standard

## ローカル開発

```bash
# 依存関係のインストール
uv sync

# アプリケーション起動
uv run python main.py
```

## デプロイ

```bash
# App Engineへデプロイ
gcloud app deploy --quiet
```