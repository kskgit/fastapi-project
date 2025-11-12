# テスト戦略

このプロジェクトでは、テストを読みやすく、意図が伝わりやすい形で保守するために以下の指針を採用します。

# テストを書くタイミング
- パブリックメソッドに対して全てテストを記述する

# 命名規約
- 特に失敗時のテストにおいては接続後を利用しない（by,with,when,doe_toなどばらつきが出ることを防ぐため）

# ファイル作成単位
- コンテキストを最小限にするために、基本的にはテスト対象に対して1テストファイルとする

# Arrange-Act-Assert (AAA) パターン
- すべてのテストを Arrange（準備）→ Act（実行）→ Assert（検証）の3段階で記述する。
- フェーズの境界が分かるように、 `# Arrange` ・`# Act`・`# Assert`コメントを各フェーズ毎の先頭に記述する。

## Arrange
必要なモックの設定やテスト対象（System Under Test）の初期化を行う。

## Act
検証したい操作を1回だけ呼び出すことを意識する。

## Assert
戻り値や副作用を明確に検証する。

# 非同期処理のテスト
非同期のリポジトリやサービスをMockする場合は以下の点を留意する
- モック化する際は、`AsyncMock` もしくは `return_value` に await 可能なオブジェクトを設定する。
- 呼び出し回数の確認は`assert_awaited_XX`シリーズ（`assert_awaited_once_with`など）を利用する。これにより、実装でawaitの記述漏れがあった場合にテストが失敗するため、非同期処理の実装ミスを防げる。

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

## テスト観点と主要パターン
### 正常系
- repository やドメインサービスが期待通りの引数・回数で呼ばれることを確認
- UseCase が返却する値が想定どおりであることを確認
- 非同期メソッドは `assert_awaited_once_with` などで await されているか確認

### ビジネスロジック例外
- ドメインサービスや UseCase 内部の検証で想定する例外が発生するか
- 例外が伝播・またはハンドリングされる挙動が仕様通りか

### 外部データ保存時の失敗
- repository が例外（例: `DataOperationException`）を送出した際の伝播・ロールバック処理を確認


# Repository
## ファイル作成単位
1 Repositoryメソッドに対して1ファイル

## ファイル名
`test_{Repositoryのファイル名}_{メソッド名}.py`とする

例）`sqlalchemy_todo_repository.py/create`→`test_sqlalchemy_todo_repository_create.py`


## メソッド名
`test_{メソッド名}_{success or failure}_{理由（任意）}.py`とする

例）
- `test_create_success`

## モック対象
- dbはテスト用のインメモリdbを利用する
- 例外の場合は例外用のフィクスチャを利用すること

## テスト観点と主要パターン
### 正常系
- 返却値が期待する値であることを確認
- 返却値の型がドメインモデルであることを確認
- 更新系の場合、保存結果が期待通りか確認
  - 他メソッドの影響をうけないようにするため、repository の他メソッドを使わず DB から直接取得して照合すること。


### 未存在／空結果
-  `find_by_id` が `None`、`find_all...` が空リストを返すケースを確認


### ドメインモデル変換
- `_to_domain_entity` / `_to_model` がフィールド欠落なく相互変換できるかを個別に確認


### SQL例外ラップ
- DB接続エラーやユニーク制約違反などを想定し、`DataOperationException` にラップされるか確認
-  `details["operation_context"]` が対象メソッドを指すことを確認する。
※ Repository レイヤではビジネスロジック起因のエラーは原則発生させない

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
