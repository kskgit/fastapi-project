# 推奨コマンド一覧

## 開発サーバー
```bash
task dev                    # 開発サーバー起動（ホットリロード）
task start                  # 本番サーバー起動
task kill-port-8000        # ポート8000のプロセス終了
```

## コード品質チェック
```bash
task lint                   # ruffリンター実行
task format                 # ruffフォーマット実行
task lint-fix              # リンターエラー自動修正
task check-all             # 全チェック実行（lint, format, import-linter, mypy, lizard）
task lizard-complexity     # 複雑度チェック
```

## テスト
```bash
task test                   # 単体テスト実行
task test-coverage         # カバレッジ付きテスト実行
task test-all              # 全テスト実行
task test-integration      # 統合テスト実行
```

## データベース
```bash
task db-up                 # PostgreSQLコンテナ起動
task db-down               # PostgreSQLコンテナ停止
task migrate               # マイグレーション実行
task migrate-auto          # 自動マイグレーション生成
task migrate-create        # 空のマイグレーションファイル作成
task db-rest               # データベースリセット
```

## システムコマンド（macOS）
```bash
ls -la                     # ファイル一覧表示
find . -name "*.py"        # Pythonファイル検索
grep -r "pattern" .        # パターン検索
git status                 # Git状態確認
```