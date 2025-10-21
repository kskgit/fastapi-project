# テスト戦略

このプロジェクトでは、テストを読みやすく、意図が伝わりやすい形で保守するために以下の指針を採用します。

# テストを書くタイミング
- UseCase、ドメインサービス、例外ハンドラなど、ビジネスロジックが分岐する箇所にはユニットテストを用意する。
- テスト名は意図が伝わる形（例: `test_create_user_failure_username_already_exists`）。
- 複数レイヤーを跨ぐ動作を確認したい場合は、統合テストを追加する。

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

# Usecase

## ファイル名
`test_{ユースケース名}.py`とする

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

## ファイル名
`test_{Repositoryファイル名}_{メソッド名}.py`とする

例）`sqlalchemy_todo_repository.py/create`→`test_sqlalchemy_todo_repository_create.py`


## メソッド名
`test_{メソッド名}_{success or failure}_{理由（任意）}.py`とする

例）
- `test_create_success`

## モック対象
- dbはテスト用のインメモリdbを利用する

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
