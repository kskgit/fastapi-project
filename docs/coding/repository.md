# Repository
## 例外処理

- Infrastructureのリポジトリは SQLAlchemy を介してデータベースにアクセスする。ドメイン層へドライバ依存の例外を漏らさないため、SQLAlchemy が投げる `SQLAlchemyError`（接続エラー、制約違反、トランザクション失敗など）をキャッチし、`DataOperationException` などのシステム系カスタム例外に置き換える。
- 例外へは `operation_context` を必ず渡し、どの操作（例: `todo_repository.create`）で失敗したのかを記録する。グローバル例外ハンドラがこの情報をログに出力し、トラブルシュートしやすくなる。
  ```python
  # 実装例
  DataOperationException(operation_context=self)
  ```
- `SQLAlchemyError` で拾えない問題（プロセス外のネットワーク断など）は上位へ到達するが、上記方針により DB レイヤ由来の一般的な障害は一貫してシステム例外として扱える。

## データ反映

- Repository での書き込み系操作（`create` / `update` / `delete`）は、`self.db.add()` や `self.db.delete()` の後に必ず `await self.db.flush()` まで実行し、同一セッション内で状態が即座に反映されるようにする。UseCase 側で `commit()` するまで DB には確定しないが、flush しておくことでレイヤテストが他メソッドを介さず直接 DB 状態を検証でき、実装の整合性が保ちやすくなる。

## バリデーション設計
- データベース制約（NOT NULL、UNIQUE など）で最終防衛線を敷き、DTO やドメインで取り逃した異常を捕捉する。
- DB 例外は `DataOperationException` などに変換し、システム系エラーとして扱う。ログには操作名を含める。
