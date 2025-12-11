# E2Eテスト
## ファイル作成単位
1 エンドポイントに対して1ファイル

## ファイル名
`test_{endpointsのファイル名}_{endpointsのメソッド名}_{条件（任意）}.py`とする

例）`todo.py/get_todo`→`test_todo_get_todo.py`

## テスト観点と主要パターン
- エンドポイントが返却するレスポンスの種別（例: 200, 4xx, 5xx）を必ず1ケースずつテストする。
- `unexpected_exception` シナリオを除き、モックは利用しない。
- レスポンスのステータスコードと、レスポンスのデータを確認する
  - 異常系の場合`detail`の中身を確認すると良い

## メソッド名
`test_{endpointsのメソッド名}_{success or failure}_{理由（任意）}.py`とする

例）
- `test_create_todo_success`
- `test_create_todo_failer_missing_user_id`
