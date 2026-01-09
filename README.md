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

## GCP初期設定

### 1. App Engine アプリケーションの作成

デプロイ前に、App Engineアプリケーションを作成する必要があります。

#### 方法1: gcloud CLIを使用

```bash
# gcloud CLIで認証
gcloud auth login

# プロジェクト設定
gcloud config set project coit-digital-sandbox-202511

# 必要なAPIを有効化
gcloud services enable appengine.googleapis.com
gcloud services enable firestore.googleapis.com

# App Engine アプリケーション作成（初回のみ）
gcloud app create --region=asia-northeast1
```

#### 方法2: GCPコンソールを使用

1. [App Engine コンソール](https://console.cloud.google.com/appengine)にアクセス
2. プロジェクト`coit-digital-sandbox-202511`を選択
3. 「アプリケーションを作成」をクリック
4. リージョン`asia-northeast1`（東京）を選択

### 2. Firestoreデータベースの作成

```bash
# Firestoreデータベース作成（初回のみ）
gcloud firestore databases create \
  --location=asia-northeast1 \
  --type=firestore-native
```

## デプロイ

### GitHub Actions経由（推奨）

1. GitHubリポジトリのSettings > Secrets and variablesで`SERVICE_ACCOUNT_JSON`を設定
2. mainブランチにプッシュすると自動デプロイが実行されます

### 手動デプロイ

```bash
# App Engineへデプロイ
gcloud app deploy --quiet
```