"""Tests for SQLAlchemySubTaskRepository.find_by_todo_id."""

import pytest

from app.domain.entities import SubTask
from app.domain.exceptions import DataOperationException
from app.infrastructure.repositories import SQLAlchemySubTaskRepository

pytestmark = pytest.mark.anyio("asyncio")


async def test_find_by_todo_id_success_returns_subtasks(repo_db_session) -> None:
    """指定したtodo_idに紐づくSubTaskのリストを返すことを確認する."""
    # Arrange
    repository = SQLAlchemySubTaskRepository(repo_db_session)
    subtask1 = await repository.create(
        SubTask.create(user_id=1, todo_id=10, title="Subtask 1")
    )
    subtask2 = await repository.create(
        SubTask.create(user_id=1, todo_id=10, title="Subtask 2")
    )
    # Different todo_id - should not be returned
    await repository.create(
        SubTask.create(user_id=1, todo_id=99, title="Other Subtask")
    )
    await repo_db_session.commit()

    # Act
    result = await repository.find_by_todo_id(10)

    # Assert
    assert len(result) == 2
    assert all(isinstance(s, SubTask) for s in result)
    result_ids = {s.id for s in result}
    assert subtask1.id in result_ids
    assert subtask2.id in result_ids
    assert all(s.todo_id == 10 for s in result)


async def test_find_by_todo_id_success_returns_empty_list_when_not_found(
    repo_db_session,
) -> None:
    """SubTaskが存在しない場合に空リストを返すことを確認する."""
    # Arrange
    repository = SQLAlchemySubTaskRepository(repo_db_session)

    # Act
    result = await repository.find_by_todo_id(999)

    # Assert
    assert result == []


async def test_find_by_todo_id_failure_sqlalchemy_error_raises_data_operation_exception(
    repo_db_session_execute_sqlalchemy_error,
) -> None:
    """SQLAlchemyError発生時にDataOperationExceptionへラップされることを確認する."""
    # Arrange
    repository = SQLAlchemySubTaskRepository(repo_db_session_execute_sqlalchemy_error)

    # Act / Assert
    with pytest.raises(DataOperationException) as exc_info:
        await repository.find_by_todo_id(1)

    assert (
        exc_info.value.details.get("operation_context")
        == "SQLAlchemySubTaskRepository.find_by_todo_id"
    )
