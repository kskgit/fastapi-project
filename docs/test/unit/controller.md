# Controller

## ファイル作成単位
1 Controllerメソッドに対して1ファイル

## ファイル名
`test_{Controllerのファイル名}_{メソッド名}.py`とする

## メソッド名
`test_{メソッド名}_{success or failure}_{理由（任意）}.py`とする

例）`test_create_subtask_success`→`test_create_todo_success_returns_response.py`

## モック対象
- Usecase

## テスト観点と主要パターン
### 正常系
- 期待するUseCaseが期待する引数で期待する回数呼ばれていること
- Usecaseから返却されたレスポンスが期待する型へ変換されてレスポンスされること
### 異常系
- 例外が発生した場合、例外を握りつぶさず FastAPI のハンドラへ伝播することを確認する。
- テスト間で同じ観点を共有するために、代表的な例外は `tests/unit/controller/exception_cases.py` の `controller_domain_exception_cases` を利用しする。

## サンプルコード
```python
ytest.mark.asyncio
async def test_create_subtask_success() -> None:
    # Arrange
    user_id = 1
    todo_id = 2
    title = "タイトル"

    request_dto = CreateSubTaskDTO(
        user_id=user_id,
        title=title,
    )

    returned_subtask = SubtaskResponseDTO(
        id=1,
        todo_id=todo_id,
        user_id=user_id,
        title=title,
        due_date=datetime(2024, 1, 10, tzinfo=UTC),
        is_completed=False,
        completed_at=None,
        created_at=datetime(2024, 1, 10, tzinfo=UTC),
        updated_at=datetime(2024, 1, 10, tzinfo=UTC),
    )

    usecase = AsyncMock(spec=CreateSubTaskUseCase)
    usecase.execute.return_value = returned_subtask

    # Act
    res = await create_subtask(todo_id=todo_id, request=request_dto, usecase=usecase)

    # Assert

    # 引数の確認
    usecase.execute.assert_awaited_once_with(
        user_id=request_dto.user_id,
        todo_id=todo_id,
        title=request_dto.title,
    )

    # レスポンスの確認
    assert res.id is not None
    assert res.todo_id == todo_id
    assert res.user_id == request_dto.user_id
    assert res.title == request_dto.title
    assert res.due_date is None
    assert not res.is_completed
    assert res.completed_at is None
    assert res.created_at is not None
    assert res.updated_at is not None
```