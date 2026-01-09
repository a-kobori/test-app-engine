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

### 0. サービスアカウント権限の設定

GitHub Actionsでデプロイを行うサービスアカウントに必要な権限を追加します。

```bash
# プロジェクトID設定
PROJECT_ID="coit-digital-sandbox-202511"
SERVICE_ACCOUNT="mcp-google-sheets@${PROJECT_ID}.iam.gserviceaccount.com"

# 必要な権限を追加
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/appengine.deployer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/artifactregistry.writer"
```

#### GCPコンソールでの設定方法

1. [IAM コンソール](https://console.cloud.google.com/iam-admin/iam)にアクセス
2. プロジェクト`coit-digital-sandbox-202511`を選択  
3. サービスアカウント`mcp-google-sheets@coit-digital-sandbox-202511.iam.gserviceaccount.com`を検索
4. 編集ボタン（鉛筆アイコン）をクリック
5. 以下のロールを追加：
   - `App Engine 管理者` または `App Engine デプロイ担当者`
   - `Cloud Build サービス アカウント`
   - `ストレージ管理者`
   - `Artifact Registry 書き込み`

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
5. デフォルト権限で作成 ※本運用時は権限をしぼったアカウントが望ましい

### 2. Firestoreデータベースの作成

#### 方法1: gcloud CLIを使用

```bash
# Firestoreデータベース作成（初回のみ）
gcloud firestore databases create \
  --location=asia-northeast1 \
  --type=firestore-native
```

#### 方法2: GCPコンソールを使用

1. [Firestore コンソール](https://console.cloud.google.com/firestore)にアクセス
2. プロジェクト`coit-digital-sandbox-202511`を選択
3. 「データベースを作成」をクリック
4. **Select your edition**で「Firestore」を選択
5. **Choose the mode for your database**で「Native mode」を選択
6. **Secure your database**で「Start in test mode」を選択
   - セキュリティルールは後で設定可能
   - 本番環境では「Start in production mode」を推奨
7. **Set a location for your database**で「asia-northeast1 (Tokyo)」を選択
8. 「作成」をクリック

> **注意**: 
> - DatastoreモードではなくNative modeを選択してください。一度作成すると変更できません
> - Test modeは誰でもアクセス可能なので、本番環境では必ずProduction modeにしてセキュリティルールを設定してください

## デプロイ

### GitHub Actions経由（推奨）

1. GitHubリポジトリのSettings > Secrets and variablesで`SERVICE_ACCOUNT_JSON`を設定
2. mainブランチにプッシュすると自動デプロイが実行されます

### 手動デプロイ

```bash
# App Engineへデプロイ
gcloud app deploy --quiet
```
