# Usecase
## 役割
- Domain Entityを組み立てて、**ビジネスロジック**を実現する
- 必要に応じてInfrastructure呼び出し
    - トランザクション境界の管理

## ファイル作成単位
1 usecaseファイルに対して1ファイル

## ファイル名
`{ユースケース名}_usecase.py`とする

## ユースケースの単位の考え方
- その名の通り、APIの利用者視点でのユースケース単位とする
  - 例）ユーザ情報の更新→update_user_info_usecase

## メソッド名
`execute`とする

## バリデーション設計
- ビジネスフローや他コンポーネント連携に依存する検証を行う。例：同一ユーザの Todo タイトル重複判定、参照リソースの存在確認。
- 例外はドメインのカスタム例外へ握り替え、HTTP ステータスが意図通りになるよう制御する。

## トランザクション管理

UseCaseはトランザクション境界を管理する責務を持つ。ただし、すべてのUseCaseでトランザクションが必要なわけではない。

### トランザクションが必要なケース

| ケース | 理由 | 例 |
|--------|------|-----|
| 複数のWRITE操作 | 原子性（Atomicity）の保証。一部失敗時に全体をロールバック | TodoとSubTaskを同時に作成 |
| READ → WRITE パターン | 読み取った値に基づく更新の一貫性を保証 | 在庫確認後の注文処理、Todoステータス更新 |
| 複数エンティティの整合性 | データ整合性の保証 | ユーザー削除時の関連Todo一括削除 |

```python
# トランザクションが必要な例: UpdateTodoUseCase
class UpdateTodoUseCase:
    async def execute(self, todo_id: int, user_id: int, **updates) -> Todo:
        async with self.transaction_manager.begin():
            # READ: 現在の状態を取得
            todo = await self.todo_repository.find_by_id(todo_id)
            if not todo:
                raise TodoNotFoundException(todo_id)

            # 検証
            self.todo_domain_service.validate_todo_ownership(todo, user_id)

            # WRITE: 更新を永続化
            todo.update(**updates)
            return await self.todo_repository.update(todo)
```

### トランザクションが不要なケース

| ケース | 理由 | 例 |
|--------|------|-----|
| 純粋なREAD操作 | 書き込みがないため原子性が不要。パフォーマンスオーバーヘッドを避ける | Todo一覧取得、Todo詳細取得 |
| 単一のWRITE操作（条件付き） | 単一操作は暗黙的に原子的。ただし事前検証がある場合は要検討 | シンプルなログ記録 |

```python
# トランザクション不要な例: GetTodoByIdUseCase
class GetTodoByIdUseCase:
    async def execute(self, todo_id: int, user_id: int) -> Todo:
        # すべてREAD操作のためトランザクション不要
        todo = await self.todo_repository.find_by_id(todo_id)
        if not todo:
            raise TodoNotFoundException(todo_id)

        await self.todo_domain_service.validate_user(user_id, self.user_repository)
        self.todo_domain_service.validate_todo_ownership(todo, user_id)

        return todo
```

### 判断基準

1. **WRITE操作があるか？** → なければトランザクション不要
2. **複数のWRITE操作があるか？** → あればトランザクション必要
3. **READ後にWRITEするか？** → 読み取り値に依存する更新ならトランザクション必要
4. **整合性が壊れた場合の影響は？** → 影響が大きければトランザクション必要

## サンプルコード
```py
async def execute(
    self,
    user_id: int,
    todo_id: int,
    title: str,
):
    async with self.transaction_manager.begin_transaction():
        await self.subtask_domain_service.ensure_todo_user_can_modify_subtask(
            user_id=user_id,
            todo_id=todo_id,
            user_repository=self.user_repository,
            todo_repository=self.todo_repository,
        )

        subtask = SubTask.create(
            user_id=user_id,
            todo_id=todo_id,
            title=title,
        )
        return await self.subtask_repository.create(subtask)
```
