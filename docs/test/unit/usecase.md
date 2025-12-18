# Usecase

## ファイル作成単位
1 usecaseファイルに対して1ファイル

## ファイル名
`test_{Usecaseのファイル名}.py`とする

例）`create_todo_usecase.py`→`test_create_todo_usecase.py`


## メソッド名
`test_{usecase名の_usecaseを除く値}_{success or failure}_{理由（任意）}.py`とする

例）
- `test_create_todo_success`
- `test_create_user_failure_username_already_exists`

## モック対象
- repository
- usecase が直接依存するドメインサービスやトランザクションマネージャ（必要に応じて）
- トランザクションマネージャは `tests/unit/usecase/conftest.py::mock_transaction_manager` を使い回し、非同期コンテキスト管理の実装差異による重複を避ける
- 基本的にAsyncMockを利用してMockし、コンストラクタでUseCaseに渡す

## テスト観点と主要パターン
### 正常系
- repository やドメインサービスが期待通りの引数・回数で呼ばれることを確認
- UseCase が返却する値が想定どおりであることを確認
- 非同期メソッドは `assert_awaited_once_with` などで await されているか確認

#### 参考実装
- [`tests/unit/usecase/test_create_todo_usecase.py/test_create_todo_success`](../tests/unit/usecase/test_create_todo_usecase.py)

### ビジネスロジック例外
- ドメインサービスや UseCase 内部の検証で想定する例外が発生するか
- 例外が伝播・またはハンドリングされる挙動が仕様通りか

### 外部データ保存時の失敗
- repository が例外（例: `DataOperationException`）を送出した際の伝播・ロールバック処理を確認
