# E2Eテスト
## ファイル作成単位
1 エンドポイントに対して1ファイル

## ファイル名
`test_{endpointsのファイル名}_{endpointsのメソッド名}_{条件（任意）}.py`とする

例）`todo.py/get_todo`→`test_todo_get_todo.py`

## テスト観点と主要パターン
- 仕様上返却し得る代表的な以下のステータス種別を最低1ケースずつテストする。
  - 200系
    - 必須
  - 400系
    - 存在する場合のみ
  - 500系
    - 必須
- 500系レスポンスは `unexpected_exception` シナリオでのみモック利用を許可する。`app.dependency_overrides` で Repository 依存（例: `get_user_repository`, `get_todo_repository`）だけを `AsyncMock` に差し替え、`Exception` を送出させて 500 のハンドリングを確認する。UseCase や他レイヤをモックしたり、DB構造を壊すようなセットアップは行わない。
- 500系レスポンスを除き、モックは利用しない。
- レスポンスのステータスコードと、レスポンスのデータを確認する
  - 異常系の場合`detail`の中身を確認すると良い

## メソッド名
`test_{endpointsのメソッド名}_{success or failure}_{理由（任意）}.py`とする

例）
- `test_create_todo_success`
- `test_create_todo_failer_missing_user_id`
