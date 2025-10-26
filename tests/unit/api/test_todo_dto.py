import pytest
from pydantic import ValidationError

from app.api.dtos.todo_dto import TodoCreateDTO, TodoUpdateDTO
from app.domain.exceptions.business import ValidationException


def test_todo_create_dto_title_is_stripped() -> None:
    # Arrange
    raw_title = "  Write documentation  "

    # Act
    dto = TodoCreateDTO(title=raw_title)

    # Assert
    assert dto.title == "Write documentation"


def test_todo_create_dto_title_too_short_after_strip_raises_validation_exception() -> None:
    # Arrange
    short_title = "  ab "

    # Act & Assert
    with pytest.raises(ValidationException):
        TodoCreateDTO(title=short_title)


def test_todo_update_dto_title_none_passes_validation() -> None:
    # Arrange
    # Act
    dto = TodoUpdateDTO(title=None)

    # Assert
    assert dto.title is None


def test_todo_update_dto_title_blank_after_strip_raises_validation_exception() -> None:
    # Arrange
    blank_title = "   "

    # Act & Assert
    with pytest.raises(ValidationException):
        TodoUpdateDTO(title=blank_title)


def test_todo_update_dto_title_min_length_guard_raises_pydantic_validation_error() -> None:
    # Arrange
    too_short_title = "ab"

    # Act & Assert
    with pytest.raises(ValidationError):
        TodoUpdateDTO(title=too_short_title)
