# GCP認証付きTODOアプリ 開発仕様書

## 1. 概要

### 1.1 目的

GCPプロジェクト内のユーザーのみがアクセス可能な認証付きWebアプリケーションの構成を検証する。

### 1.2 検証ポイント

| 項目 | 検証内容 |
|------|----------|
| IAP認証 | プロジェクトメンバーのみアクセス可能か |
| App Engine | Standard環境でのデプロイ・スケーリング |
| Firestore | App Engineからの読み書き |
| ユーザー識別 | IAPヘッダーからログインユーザーを取得できるか |

### 1.3 技術スタック

- **フロントエンド**: HTML + Vanilla JS（シンプルさ優先）
- **バックエンド**: Python 3.12 + Flask
- **データベース**: Firestore（Native mode）
- **認証**: Identity-Aware Proxy (IAP)
- **ホスティング**: App Engine Standard

---

## 2. 機能要件

### 2.1 機能一覧

| 機能 | 説明 | 優先度 |
|------|------|--------|
| TODO一覧表示 | ログインユーザーのTODOを表示 | 必須 |
| TODO追加 | 新しいTODOを作成 | 必須 |
| TODO完了/未完了切替 | ステータスをトグル | 必須 |
| TODO削除 | TODOを削除 | 必須 |
| ユーザー情報表示 | ログイン中のユーザーを表示 | 必須 |

### 2.2 画面仕様

```
+------------------------------------------+
| 📝 TODO App                              |
| ログイン中: akira@example.com            |
+------------------------------------------+
| [ 新しいTODOを入力...          ] [追加]  |
+------------------------------------------+
| ☐ 牛乳を買う                    [削除]   |
| ☑ 請求書を送る                  [削除]   |
| ☐ ミーティング資料作成          [削除]   |
+------------------------------------------+
```

---

## 3. データ設計

### 3.1 Firestoreコレクション構造

```
todos/
  └── {todoId}/
        ├── userId: string      # IAPから取得したユーザーID
        ├── email: string       # ユーザーのメールアドレス
        ├── title: string       # TODOのタイトル
        ├── completed: boolean  # 完了フラグ
        ├── createdAt: timestamp
        └── updatedAt: timestamp
```

### 3.2 セキュリティルール

Firestoreセキュリティルールは使用しない（App Engine経由のアクセスのみのため、サービスアカウント権限で制御）。

---

## 4. API設計

### 4.1 エンドポイント一覧

| メソッド | パス | 説明 |
|----------|------|------|
| GET | `/` | フロントエンドHTML |
| GET | `/api/todos` | TODO一覧取得 |
| POST | `/api/todos` | TODO作成 |
| PUT | `/api/todos/{id}` | TODO更新（完了切替） |
| DELETE | `/api/todos/{id}` | TODO削除 |
| GET | `/api/me` | ログインユーザー情報 |

### 4.2 IAPヘッダーからのユーザー情報取得

IAPが付与するヘッダー:

```python
# ユーザーのメールアドレス
email = request.headers.get('X-Goog-Authenticated-User-Email')
# 例: "accounts.google.com:akira@example.com"

# ユーザーID
user_id = request.headers.get('X-Goog-Authenticated-User-Id')
# 例: "accounts.google.com:1234567890"
```

### 4.3 APIリクエスト/レスポンス例

#### TODO一覧取得
```
GET /api/todos

Response 200:
{
  "todos": [
    {
      "id": "abc123",
      "title": "牛乳を買う",
      "completed": false,
      "createdAt": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### TODO作成
```
POST /api/todos
Content-Type: application/json

{
  "title": "新しいタスク"
}

Response 201:
{
  "id": "def456",
  "title": "新しいタスク",
  "completed": false,
  "createdAt": "2024-01-15T11:00:00Z"
}
```

#### TODO更新（完了切替）
```
PUT /api/todos/abc123
Content-Type: application/json

{
  "completed": true
}

Response 200:
{
  "id": "abc123",
  "title": "牛乳を買う",
  "completed": true,
  "updatedAt": "2024-01-15T12:00:00Z"
}
```

#### TODO削除
```
DELETE /api/todos/abc123

Response 204: No Content
```

---

## 5. GCP構成

### 5.1 必要なGCPサービス

| サービス | 用途 | 設定 |
|----------|------|------|
| App Engine | アプリホスティング | Standard / F1インスタンス |
| Firestore | データベース | Native mode / asia-northeast1 |
| IAP | 認証 | OAuth同意画面設定必要 |

### 5.2 app.yaml

```yaml
runtime: python312
instance_class: F1

automatic_scaling:
  min_instances: 0
  max_instances: 2
  min_idle_instances: 0
  target_cpu_utilization: 0.65

handlers:
  - url: /.*
    script: auto
    secure: always

env_variables:
  GOOGLE_CLOUD_PROJECT: "your-project-id"
```

### 5.3 必要なIAMロール

| 対象 | ロール | 目的 |
|------|--------|------|
| App Engineサービスアカウント | Cloud Datastore User | Firestore読み書き |
| アクセスユーザー | IAP-secured Web App User | IAPを通過してアプリにアクセス |

---

## 6. ディレクトリ構成

```
todo-app/
├── app.yaml              # App Engine設定
├── requirements.txt      # Python依存関係
├── main.py              # Flaskアプリケーション
├── static/
│   └── app.js           # フロントエンドJS
└── templates/
    └── index.html       # メインページ
```

---

## 7. デプロイ手順

### 7.1 事前準備

```bash
# 1. GCPプロジェクト作成 & 選択
gcloud projects create todo-app-verify --name="TODO App Verify"
gcloud config set project todo-app-verify

# 2. 課金アカウント紐付け（コンソールから）

# 3. 必要なAPIを有効化
gcloud services enable \
  appengine.googleapis.com \
  firestore.googleapis.com \
  iap.googleapis.com

# 4. Firestoreデータベース作成
gcloud firestore databases create \
  --location=asia-northeast1 \
  --type=firestore-native

# 5. App Engine初期化
gcloud app create --region=asia-northeast1
```

### 7.2 アプリデプロイ

```bash
# アプリをデプロイ
gcloud app deploy --quiet

# デプロイ確認
gcloud app browse
```

### 7.3 IAP設定

```bash
# 1. OAuth同意画面を設定（コンソールから）
#    - APIs & Services > OAuth consent screen
#    - Internal（組織内）または External を選択
#    - アプリ名、サポートメール等を入力

# 2. IAPを有効化（コンソールから）
#    - Security > Identity-Aware Proxy
#    - App Engineのアプリを選択してIAPをON

# 3. アクセス権限を付与
gcloud iap web add-iam-policy-binding \
  --member="user:your-email@example.com" \
  --role="roles/iap.httpsResourceAccessUser" \
  --resource-type=app-engine
```

---

## 8. ローカル開発

### 8.1 環境構築

```bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# Firestore エミュレータ（オプション）
gcloud emulators firestore start --host-port=localhost:8081
```

### 8.2 ローカル実行

```bash
# IAPヘッダーをモックして実行
export FLASK_ENV=development
export MOCK_IAP_USER="test@example.com"
python main.py
```

---

## 9. 検証チェックリスト

### 9.1 IAP認証

- [ ] 未認証ユーザーがアクセスするとGoogleログイン画面にリダイレクトされる
- [ ] IAP権限のないユーザーはアクセス拒否される
- [ ] IAP権限のあるユーザーはアプリにアクセスできる
- [ ] ログインユーザーのメールアドレスが画面に表示される

### 9.2 App Engine

- [ ] デプロイが成功する
- [ ] アクセスがない時間帯はインスタンスが0になる
- [ ] エラーログがCloud Loggingで確認できる

### 9.3 Firestore

- [ ] TODOの作成ができる
- [ ] TODO一覧が取得できる
- [ ] TODOの更新ができる
- [ ] TODOの削除ができる
- [ ] ユーザーごとにTODOが分離されている

### 9.4 コスト

- [ ] 1週間運用後、請求額が想定内（$0〜5）である

---

## 10. 想定コスト

| 項目 | 月額見込み |
|------|-----------|
| App Engine（F1、低トラフィック） | $0〜2 |
| Firestore（無料枠内） | $0 |
| IAP | $0 |
| ネットワーク（下り） | $0 |
| **合計** | **$0〜2** |

---

## 11. 今後の拡張案（スコープ外）

- TODO期限日の設定
- TODOのカテゴリ/タグ
- 他ユーザーとの共有
- Slack通知連携
- カレンダー連携

---

## 変更履歴

| バージョン | 日付 | 内容 |
|-----------|------|------|
| 0.1 | 2025-01-09 | 初版作成 |
