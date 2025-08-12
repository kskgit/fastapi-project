"""E2E Integration tests for CreateTodoUseCase.

Tests the complete async flow from UseCase → Repository → Database
using real database connections and async SQLAlchemy implementations.
"""

from datetime import datetime, timedelta

import pytest

from app.domain.entities.todo import TodoPriority, TodoStatus
from app.domain.entities.user import User
from app.domain.exceptions.business import UserNotFoundException
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository
from app.usecases.todo.create_todo_usecase import CreateTodoUseCase


@pytest.mark.asyncio
@pytest.mark.integration
class TestCreateTodoUseCaseE2E:
    """E2E integration tests for CreateTodoUseCase."""

    async def test_create_todo_success_minimal_data(
        self,
        async_todo_repository: TodoRepository,
        async_user_repository: UserRepository,
        async_test_user_id: int,
    ):
        """Test successful todo creation with minimal required data."""
        # Arrange
        usecase = CreateTodoUseCase(async_todo_repository, async_user_repository)
        title = "Complete project documentation"

        # Act
        created_todo = await usecase.execute(
            title=title,
            user_id=async_test_user_id,
        )

        # Assert - Verify returned todo
        assert created_todo is not None
        assert created_todo.id is not None
        assert created_todo.title == title
        assert created_todo.user_id == async_test_user_id
        assert created_todo.description is None
        assert created_todo.due_date is None
        assert created_todo.priority == TodoPriority.medium  # default
        assert created_todo.status == TodoStatus.pending
        assert created_todo.created_at is not None
        assert created_todo.updated_at is not None

        # Assert - Verify database persistence
        assert created_todo.id is not None
        persisted_todo = await async_todo_repository.find_by_id(created_todo.id)
        assert persisted_todo is not None
        assert persisted_todo.title == title
        assert persisted_todo.user_id == async_test_user_id

    async def test_create_todo_success_complete_data(
        self,
        async_todo_repository: TodoRepository,
        async_user_repository: UserRepository,
        async_test_user_id: int,
    ):
        """Test successful todo creation with all optional fields."""
        # Arrange
        usecase = CreateTodoUseCase(async_todo_repository, async_user_repository)
        title = "Implement new feature"
        description = "Detailed implementation of user authentication system"
        due_date = datetime.now() + timedelta(days=7)
        priority = TodoPriority.high

        # Act
        created_todo = await usecase.execute(
            title=title,
            user_id=async_test_user_id,
            description=description,
            due_date=due_date,
            priority=priority,
        )

        # Assert - Verify returned todo with complete data
        assert created_todo.title == title
        assert created_todo.description == description
        assert created_todo.due_date == due_date
        assert created_todo.priority == priority
        assert created_todo.status == TodoStatus.pending
        assert created_todo.user_id == async_test_user_id

        # Assert - Verify database persistence with all fields
        assert created_todo.id is not None
        persisted_todo = await async_todo_repository.find_by_id(created_todo.id)
        assert persisted_todo is not None
        assert persisted_todo.description == description
        assert persisted_todo.due_date == due_date
        assert persisted_todo.priority == priority

    async def test_create_multiple_todos_for_same_user(
        self,
        async_todo_repository: TodoRepository,
        async_user_repository: UserRepository,
        async_test_user_id: int,
    ):
        """Test creating multiple todos for the same user."""
        # Arrange
        usecase = CreateTodoUseCase(async_todo_repository, async_user_repository)
        titles = ["Todo 1", "Todo 2", "Todo 3"]

        # Act
        created_todos = []
        for title in titles:
            todo = await usecase.execute(title=title, user_id=async_test_user_id)
            created_todos.append(todo)

        # Assert - Verify all todos were created with unique IDs
        assert len(created_todos) == 3
        todo_ids = [todo.id for todo in created_todos]
        assert len(set(todo_ids)) == 3  # All IDs should be unique

        # Assert - Verify all todos exist in database
        user_todos = await async_todo_repository.find_all_by_user_id(async_test_user_id)
        assert len(user_todos) == 3
        user_todo_titles = [todo.title for todo in user_todos]
        assert set(user_todo_titles) == set(titles)

    async def test_create_todo_failure_user_not_found(
        self,
        async_todo_repository: TodoRepository,
        async_user_repository: UserRepository,
    ):
        """Test todo creation failure when user does not exist."""
        # Arrange
        usecase = CreateTodoUseCase(async_todo_repository, async_user_repository)
        non_existent_user_id = 9999
        title = "This should fail"

        # Act & Assert
        with pytest.raises(UserNotFoundException, match="User with id 9999 not found"):
            await usecase.execute(
                title=title,
                user_id=non_existent_user_id,
            )

        # Assert - Verify no todo was created in database
        all_todos = await async_todo_repository.find_all_by_user_id(
            non_existent_user_id
        )
        assert len(all_todos) == 0

    async def test_create_todo_with_past_due_date(
        self,
        async_todo_repository: TodoRepository,
        async_user_repository: UserRepository,
        async_test_user_id: int,
    ):
        """Test creating todo with past due date (should be allowed)."""
        # Arrange
        usecase = CreateTodoUseCase(async_todo_repository, async_user_repository)
        title = "Overdue task"
        past_due_date = datetime.now() - timedelta(days=1)

        # Act
        created_todo = await usecase.execute(
            title=title,
            user_id=async_test_user_id,
            due_date=past_due_date,
        )

        # Assert - Todo should be created even with past due date
        assert created_todo.due_date == past_due_date
        assert created_todo.status == TodoStatus.pending

        # Verify persistence
        assert created_todo.id is not None
        persisted_todo = await async_todo_repository.find_by_id(created_todo.id)
        assert persisted_todo is not None
        assert persisted_todo.due_date == past_due_date

    async def test_create_todo_priority_variations(
        self,
        async_todo_repository: TodoRepository,
        async_user_repository: UserRepository,
        async_test_user_id: int,
    ):
        """Test creating todos with different priority levels."""
        # Arrange
        usecase = CreateTodoUseCase(async_todo_repository, async_user_repository)
        priorities = [TodoPriority.low, TodoPriority.medium, TodoPriority.high]

        # Act & Assert
        for priority in priorities:
            title = f"Priority {priority.value} task"
            created_todo = await usecase.execute(
                title=title,
                user_id=async_test_user_id,
                priority=priority,
            )

            assert created_todo.priority == priority

            # Verify database persistence
            assert created_todo.id is not None
            persisted_todo = await async_todo_repository.find_by_id(created_todo.id)
            assert persisted_todo is not None
            assert persisted_todo.priority == priority

    async def test_database_transaction_integrity(
        self,
        async_todo_repository: TodoRepository,
        async_user_repository: UserRepository,
        async_test_user_id: int,
    ):
        """Test that todo creation maintains database transaction integrity."""
        # Arrange
        usecase = CreateTodoUseCase(async_todo_repository, async_user_repository)

        # Get initial count
        initial_todos = await async_todo_repository.find_all_by_user_id(
            async_test_user_id
        )
        initial_count = len(initial_todos)

        # Act - Create todo
        created_todo = await usecase.execute(
            title="Transaction test",
            user_id=async_test_user_id,
        )

        # Assert - Verify count increased by exactly 1
        final_todos = await async_todo_repository.find_all_by_user_id(
            async_test_user_id
        )
        assert len(final_todos) == initial_count + 1

        # Verify the created todo is in the list
        assert created_todo.id is not None
        todo_ids = [todo.id for todo in final_todos]
        assert created_todo.id in todo_ids

    async def test_create_todo_with_multiple_users(
        self,
        async_todo_repository: TodoRepository,
        async_user_repository: UserRepository,
        async_test_user_id: int,
        async_test_db_session,
    ):
        """Test creating todos for multiple users."""
        # Arrange - Create additional test user
        user2 = User.create(
            username="async_test_user_2",
            email="asynctest2@example.com",
            full_name="Async Test User 2",
        )
        saved_user2 = await async_user_repository.save(user2)

        usecase = CreateTodoUseCase(async_todo_repository, async_user_repository)

        # Act - Create todos for different users
        todo1 = await usecase.execute(title="User 1 todo", user_id=async_test_user_id)

        assert saved_user2.id is not None
        todo2 = await usecase.execute(title="User 2 todo", user_id=saved_user2.id)

        # Assert - Verify todos were created with correct user_id
        assert todo1.user_id == async_test_user_id
        assert todo2.user_id == saved_user2.id

        # Verify todos exist in database
        assert todo1.id is not None
        assert todo2.id is not None
        persisted_todo1 = await async_todo_repository.find_by_id(todo1.id)
        persisted_todo2 = await async_todo_repository.find_by_id(todo2.id)

        assert persisted_todo1 is not None
        assert persisted_todo2 is not None
        assert persisted_todo1.user_id == async_test_user_id
        assert persisted_todo2.user_id == saved_user2.id
        assert persisted_todo1.title == "User 1 todo"
        assert persisted_todo2.title == "User 2 todo"
