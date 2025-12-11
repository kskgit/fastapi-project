# Domain Service

## ファイル作成単位
1 ドメインサービスの1メソッドに対して1ファイル  
例: `user_domain_service.validate_user_uniqueness` → `test_user_domain_service_validate_user_uniqueness.py`

## ファイル名・メソッド名
- ファイル: `test_{domain_service名}_{メソッド名}.py`
- メソッド: `test_{ドメインサービス名またはメソッド名}_{success or failure}_{理由（任意）}`

## モック対象
- Repository など外部 I/O は `AsyncMock(spec=RepositoryInterface)` で表現する
- 複数の非同期呼び出し有無を明示するため `assert_awaited_once_with` や `assert_not_awaited` を活用する

## テスト観点
- ビジネスロジックの検証のみ実施する
  - インフラの例外をどう扱うかについては、基本的にハンドリングせずそのままthrowする前提であるため、テストのシンプルさを優先しテスト対象外とする
- ドメインサービスが担う複合的なユースケース／ユニーク制約判定などを検証する
- repositoryが期待通りの引数・回数で呼ばれることを確認

### 参考実装
- [`tests/unit/domain/test_user_domain_service_validate_user_uniqueness.py::test_validate_user_uniqueness_failure_duplicate_username`](../tests/unit/domain/test_user_domain_service_validate_user_uniqueness.py)
- [`tests/unit/domain/test_user_domain_service_validate_user_uniqueness.py::test_validate_user_uniqueness_success_allows_existing_values`](../tests/unit/domain/test_user_domain_service_validate_user_uniqueness.py)
