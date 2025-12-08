# Controller

## ファイル作成単位
1 Controllerメソッドに対して1ファイル

## ファイル名
`test_{Controllerのファイル名}_{メソッド名}.py`とする

## メソッド名

## ファイル名
`test_{メソッド名}_{success or failure}_{理由（任意）}.py`とする

例）`sqlalchemy_todo_repository.py/create`→`test_create_todo_success_returns_response.py`

## モック対象
- Usecase

## テスト観点と主要パターン
### 正常系
- 期待するUseCaseが期待する引数で期待する回数呼ばれていること
- Usecaseから返却されたレスポンスが期待する型へ変換されてレスポンスされること
### 異常系
- 例外が発生した場合、例外を握りつぶさず FastAPI のハンドラへ伝播することを確認する。
- テスト間で同じ観点を共有するために、代表的な例外は `tests/unit/controller/exception_cases.py` の `controller_domain_exception_cases` を利用しする。
