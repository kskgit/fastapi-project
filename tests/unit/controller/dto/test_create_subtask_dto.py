"""Unit tests for TodoCreateDTO user_id validation."""

from typing import Any

import pytest
from pydantic import ValidationError

from app.controller.dto import CreateSubTaskDTO


def test_create_subtask_dto_user_id_required() -> None:
    """user_idが必須項目であることを検証する."""
    # Arrange
    payload: dict[str, Any] = {
        "title": "Valid todo title",
    }

    # Act
    with pytest.raises(ValidationError) as exc_info:
        CreateSubTaskDTO(**payload)

    # Assert
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("user_id",) for error in errors)


def test_create_subtask_dto_title_required() -> None:
    # Arrange
    payload: dict[str, Any] = {
        "user_id": 1,
    }

    # Act
    with pytest.raises(ValidationError) as exc_info:
        CreateSubTaskDTO(**payload)

    # Assert
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("title",) for error in errors)


def test_create_subtask_dto_title_empty() -> None:
    # Arrange
    payload: dict[str, Any] = {
        "user_id": 1,
        "title": "",
    }

    # Act
    with pytest.raises(ValidationError) as exc_info:
        CreateSubTaskDTO(**payload)

    # Assert
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("title",) for error in errors)


def test_create_subtask_dto_title_too_short() -> None:
    # Arrange
    payload: dict[str, Any] = {
        "user_id": 1,
        "title": "a",
    }

    # Act
    with pytest.raises(ValidationError) as exc_info:
        CreateSubTaskDTO(**payload)

    # Assert
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("title",) for error in errors)
