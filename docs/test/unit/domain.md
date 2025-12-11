# Domain

## ファイル作成単位
1 ドメインエンティティに対して1ファイル(例: `user.py` → `test_user_entity.py`)

## メソッド名
`test_{ドメイン名}_{メソッド名}_{success or failure}_{理由（任意）}.py` を基本とする  
例: `test_user_create_success_keep_specified_role`

## テスト観点
- Entityのファクトリ（`create` 等）が引数を正しく保持するか
- ドメイン固有ルールの副作用（例: 所有権チェック）が期待通りか
- 外部依存を持たないため、基本的にpureなassertで完結させる
