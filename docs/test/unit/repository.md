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
- `details["operation_context"]` が対象メソッドを指すことを確認する。
※ Repository レイヤではビジネスロジック起因のエラーは原則発生させない
