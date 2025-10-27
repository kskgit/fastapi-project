"""Unit tests for TodoCreateDTO user_id validation."""

import pytest
from pydantic import ValidationError

from app.api.dtos.todo_dto import CreateTodoDTO
from app.domain.exceptions import ValidationException


def test_todo_create_dto_user_id_required() -> None:
    """user_idが必須項目であることを検証する."""
    # Arrange
    payload = {
        "title": "Valid todo title",
    }

    # Act
    with pytest.raises(ValidationError) as exc_info:
        CreateTodoDTO(**payload)

    # Assert
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("user_id",) for error in errors)


def test_todo_create_dto_user_id_must_be_positive() -> None:
    """user_idは正の整数でなければならない."""
    # Arrange
    payload = {
        "user_id": 0,
        "title": "Valid todo title",
    }

    # Act
    with pytest.raises(ValidationException) as exc_info:
        CreateTodoDTO(**payload)

    # Assert
    assert str(exc_info.value) == "User ID must be a positive integer"
