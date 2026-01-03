"""Unit tests for SubtaskResponseDTO conversion."""

from datetime import UTC, datetime

import pytest

from app.controller.dto.subtask_dto import SubtaskResponseDTO, SubtaskResult
from app.domain.exceptions import ValidationException


def _build_result(
    *,
    id_value: int | None = 1,
    created_at_value: datetime | None = datetime(2024, 1, 1, tzinfo=UTC),
    updated_at_value: datetime | None = datetime(2024, 1, 2, tzinfo=UTC),
) -> SubtaskResult:
    """Helper to create a SubtaskResult with overridable fields for tests."""
    return SubtaskResult(
        id=id_value,
        todo_id=10,
        user_id=5,
        title="Write docs",
        is_completed=False,
        completed_at=None,
        created_at=created_at_value,
        updated_at=updated_at_value,
    )


def test_subtask_response_dto_from_result_success() -> None:
    """正常系: SubtaskResultからレスポンスDTOへ変換できる."""
    # Arrange
    result = _build_result()

    # Act
    dto = SubtaskResponseDTO.from_result(result)

    # Assert
    assert dto.id == result.id
    assert dto.todo_id == result.todo_id
    assert dto.user_id == result.user_id
    assert dto.title == result.title
    assert dto.is_completed is False
    assert dto.completed_at is None
    assert dto.created_at == result.created_at
    assert dto.updated_at == result.updated_at


@pytest.mark.parametrize(
    "id_value,created_at_value,updated_at_value,expected_message",
    [
        (
            None,
            datetime(2024, 1, 1, tzinfo=UTC),
            datetime(2024, 1, 2, tzinfo=UTC),
            "ID",
        ),
        (
            1,
            None,
            datetime(2024, 1, 2, tzinfo=UTC),
            "created_at",
        ),
        (
            1,
            datetime(2024, 1, 1, tzinfo=UTC),
            None,
            "updated_at",
        ),
    ],
)
def test_subtask_response_dto_from_result_missing_required_fields(
    id_value: int | None,
    created_at_value: datetime | None,
    updated_at_value: datetime | None,
    expected_message: str,
) -> None:
    """IDやタイムスタンプ欠如時はValidationExceptionを送出する."""
    # Arrange
    result = _build_result(
        id_value=id_value,
        created_at_value=created_at_value,
        updated_at_value=updated_at_value,
    )

    # Act / Assert
    with pytest.raises(ValidationException) as exc_info:
        SubtaskResponseDTO.from_result(result)

    assert expected_message.lower() in str(exc_info.value).lower()
