# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

GCP認証付きTODOアプリケーション - Identity-Aware Proxy (IAP)を使用してGCPプロジェクトメンバーのみがアクセス可能なWebアプリケーション

技術スタック:
- フロントエンド: HTML + HTMX (サーバーサイドレンダリング)
- バックエンド: Python 3.12 + Flask
- データベース: Firestore (Native mode)
- 認証: Identity-Aware Proxy (IAP)
- ホスティング: App Engine Standard

## 開発コマンド

### ローカル開発

```bash
# 仮想環境のセットアップ
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 依存関係のインストール
pip install -r requirements.txt

# ローカル実行（IAPヘッダーをモック）
export FLASK_ENV=development
export MOCK_IAP_USER="test@example.com"
python main.py

# Firestore エミュレータ（オプション）
gcloud emulators firestore start --host-port=localhost:8081
```

### デプロイ

```bash
# App Engineへデプロイ
gcloud app deploy --quiet

# デプロイ確認
gcloud app browse

# ログ確認
gcloud app logs tail -s default
```

### テスト実行

```bash
# ユニットテスト（実装時に追加予定）
python -m pytest tests/

# カバレッジ付きテスト
python -m pytest --cov=. tests/
```

## アーキテクチャ概要

### ディレクトリ構成

```
todo-app/
├── app.yaml              # App Engine設定
├── requirements.txt      # Python依存関係
├── main.py              # Flaskアプリケーション（メインエントリポイント）
├── static/
│   └── htmx.min.js      # HTMX ライブラリ（CDNも可）
└── templates/
    ├── index.html       # メインページテンプレート
    └── partials/        # HTMXで返すHTML部分テンプレート
        ├── todo_item.html
        └── todo_list.html
```

### APIエンドポイント

- `GET /` - メインページ（完全なHTML）
- `GET /todos` - TODO一覧（HTMLパーシャル、HTMX用）
- `POST /todos` - TODO作成（HTMLパーシャルを返す）
- `PUT /todos/{id}` - TODO更新（完了/未完了切替、HTMLパーシャルを返す）
- `DELETE /todos/{id}` - TODO削除（空レスポンスまたは更新されたリスト）
- `GET /api/me` - ログインユーザー情報（JSON）

### IAPからのユーザー情報取得

```python
# IAPが付与するヘッダーから取得
email = request.headers.get('X-Goog-Authenticated-User-Email')
user_id = request.headers.get('X-Goog-Authenticated-User-Id')
```

### Firestoreデータ構造

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

## 開発時の注意事項

1. **認証**: ローカル開発時は`MOCK_IAP_USER`環境変数でIAPヘッダーをモック
2. **Firestore**: App Engine経由でサービスアカウント権限を使用（セキュリティルールは不要）
3. **エラーハンドリング**: IAPヘッダーが取得できない場合の適切なエラー処理が必要
4. **スケーリング**: app.yamlで最小0インスタンス、最大2インスタンスに設定
5. **コスト**: 低トラフィックを想定（月額$0-2の範囲）

## HTMX使用時の設計方針

1. **レスポンス形式**: APIエンドポイントはHTMLパーシャルを返す（JSON APIではなく）
2. **部分更新**: TODOの追加・更新・削除時は該当部分のみHTMLを更新
3. **プログレッシブエンハンスメント**: JavaScriptが無効でも基本機能は動作
4. **HTMXアトリビュート**: 
   - `hx-get`, `hx-post`, `hx-put`, `hx-delete` でAjaxリクエスト
   - `hx-target` で更新対象要素を指定
   - `hx-swap` で更新方法を指定（innerHTML, outerHTML, beforeend等）
5. **CSRFトークン**: Flaskの`csrf_token`をフォームまたはヘッダーに含める