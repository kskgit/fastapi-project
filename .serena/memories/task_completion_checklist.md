# タスク完了時の実行手順

## 必須チェック項目
タスク完了時は以下を順番に実行してください：

### 1. コード品質チェック
```bash
task check-all
```
これにより以下が実行されます：
- ruff check . (リンター)
- ruff format --check . (フォーマットチェック)
- uv run lint-imports (import-linter)
- uv run mypy . (型チェック)
- uv run lizard --CCN 5 app/ (複雑度チェック)

### 2. テスト実行
```bash
task test-all
```

### 3. 統合テスト（必要に応じて）
```bash
task test-integration
```

### 4. Git操作
```bash
git add .
git commit -m "適切なコミットメッセージ"
```

## エラー対応
- **リンターエラー**: `task lint-fix` で自動修正
- **フォーマットエラー**: `task format` で自動修正
- **型エラー**: mypy出力を確認して手動修正
- **複雑度エラー**: CCN≥10の場合はリファクタリング検討

## 注意事項
- lefthookによりpre-commitフックが設定済み
- コミット前に自動でチェックが実行される
- 全チェックが通過してからコミットすること