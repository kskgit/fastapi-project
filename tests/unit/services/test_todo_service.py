from datetime import datetime
from unittest.mock import Mock

import pytest

from app.domain.entities.todo import Todo, TodoPriority, TodoStatus
from app.domain.repositories.todo_repository import TodoRepository
from app.services.todo_service import TodoService


class TestTodoService:
    """Unit tests for TodoService class.

    These tests focus on business logic by mocking the repository layer.
    """

    def setup_method(self):
        """Set up test dependencies."""
        self.mock_repository = Mock(spec=TodoRepository)
        self.service = TodoService(self.mock_repository)

    def test_create_todo_success_with_minimal_data(self):
        """Test successful todo creation with minimal required data."""
        # Arrange
        title = "Test Todo"
        expected_todo = Todo(
            id=1,
            title=title,
            description=None,
            due_date=None,
            status=TodoStatus.pending,
            priority=TodoPriority.medium,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_repository.save.return_value = expected_todo

        # Act
        result = self.service.create_todo(title=title)

        # Assert
        assert result == expected_todo
        self.mock_repository.save.assert_called_once()

        # Verify the Todo entity passed to repository.save()
        saved_todo_call = self.mock_repository.save.call_args[0][0]
        assert saved_todo_call.title == title
        assert saved_todo_call.description is None
        assert saved_todo_call.due_date is None
        assert saved_todo_call.status == TodoStatus.pending
        assert saved_todo_call.priority == TodoPriority.medium
        assert saved_todo_call.id is None  # Not set until saved

    def test_create_todo_success_with_all_data(self):
        """Test successful todo creation with all optional fields."""
        # Arrange
        title = "Comprehensive Test Todo"
        description = "This is a test description"
        due_date = datetime(2024, 12, 31, 23, 59, 59)
        priority = TodoPriority.high

        expected_todo = Todo(
            id=2,
            title=title,
            description=description,
            due_date=due_date,
            status=TodoStatus.pending,
            priority=priority,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_repository.save.return_value = expected_todo

        # Act
        result = self.service.create_todo(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
        )

        # Assert
        assert result == expected_todo
        self.mock_repository.save.assert_called_once()

        # Verify the Todo entity passed to repository.save()
        saved_todo_call = self.mock_repository.save.call_args[0][0]
        assert saved_todo_call.title == title
        assert saved_todo_call.description == description
        assert saved_todo_call.due_date == due_date
        assert saved_todo_call.status == TodoStatus.pending
        assert saved_todo_call.priority == priority

    def test_create_todo_with_default_priority(self):
        """Test that default priority is medium when not specified."""
        # Arrange
        title = "Default Priority Todo"
        expected_todo = Todo(
            id=3,
            title=title,
            status=TodoStatus.pending,
            priority=TodoPriority.medium,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_repository.save.return_value = expected_todo

        # Act
        self.service.create_todo(title=title)

        # Assert
        saved_todo_call = self.mock_repository.save.call_args[0][0]
        assert saved_todo_call.priority == TodoPriority.medium

    def test_create_todo_repository_exception_handling(self):
        """Test that repository exceptions are properly wrapped."""
        # Arrange
        title = "Exception Test Todo"
        repository_error = Exception("Database connection failed")
        self.mock_repository.save.side_effect = repository_error

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            self.service.create_todo(title=title)

        assert "Failed to create todo: Database connection failed" in str(
            exc_info.value
        )
        assert exc_info.value.__cause__ == repository_error

    def test_create_todo_calls_domain_entity_create(self):
        """Test that the service properly uses Domain Entity creation."""
        # Arrange
        title = "Domain Entity Test"
        description = "Testing domain entity creation"
        due_date = datetime(2024, 6, 15, 10, 30)
        priority = TodoPriority.low

        expected_todo = Todo(
            id=4,
            title=title,
            description=description,
            due_date=due_date,
            status=TodoStatus.pending,
            priority=priority,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_repository.save.return_value = expected_todo

        # Act
        self.service.create_todo(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
        )

        # Assert
        self.mock_repository.save.assert_called_once()
        saved_todo = self.mock_repository.save.call_args[0][0]

        # Verify that Todo.create() was used (status is pending by default)
        assert saved_todo.status == TodoStatus.pending
        assert saved_todo.id is None  # ID is None until saved by repository

    def test_create_todo_user_id_parameter_unused(self):
        """Test that user_id parameter exists but is currently unused.

        This test documents current behavior and will need updating
        when user-based filtering is implemented.
        """
        # Arrange
        title = "User ID Test Todo"
        user_id = 123
        expected_todo = Todo(
            id=5,
            title=title,
            status=TodoStatus.pending,
            priority=TodoPriority.medium,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_repository.save.return_value = expected_todo

        # Act
        result = self.service.create_todo(title=title, user_id=user_id)

        # Assert
        assert result == expected_todo
        # Currently, user_id doesn't affect the created todo
        # This behavior may change when user-based features are implemented
        saved_todo = self.mock_repository.save.call_args[0][0]
        assert saved_todo.title == title

    def test_create_todo_title_trimming_handled_by_dto(self):
        """Test that title trimming is expected to be handled by DTO layer.

        The service layer assumes title is already validated and trimmed.
        """
        # Arrange
        title = "Valid Todo Title"  # Already trimmed
        expected_todo = Todo(
            id=6,
            title=title,
            status=TodoStatus.pending,
            priority=TodoPriority.medium,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_repository.save.return_value = expected_todo

        # Act
        self.service.create_todo(title=title)

        # Assert
        saved_todo = self.mock_repository.save.call_args[0][0]
        assert saved_todo.title == title
        # Service layer does not perform validation - that's DTO's responsibility
