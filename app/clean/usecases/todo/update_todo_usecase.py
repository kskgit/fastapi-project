from datetime import datetime

from app.clean.domain.entities.todo import Todo, TodoPriority, TodoStatus
from app.clean.domain.repositories.todo_repository import TodoRepository
from app.clean.domain.repositories.user_repository import UserRepository


class UpdateTodoUseCase:
    """UseCase for updating an existing Todo.

    Single Responsibility: Handle the update of a todo with proper
    business logic validation, ownership checks, and user existence validation.

    Dependencies:
    - Only depends on Domain layer (TodoRepository and UserRepository interfaces)
    - No dependencies on API, Services, or Infrastructure layers
    """

    def __init__(
        self, todo_repository: TodoRepository, user_repository: UserRepository
    ):
        """Initialize with repository dependencies.

        Args:
            todo_repository: TodoRepository interface implementation
            user_repository: UserRepository interface implementation
        """
        self.todo_repository = todo_repository
        self.user_repository = user_repository

    def execute(
        self,
        todo_id: int,
        user_id: int,
        title: str | None = None,
        description: str | None = None,
        due_date: datetime | None = None,
        status: TodoStatus | None = None,
        priority: TodoPriority | None = None,
    ) -> Todo:
        """Execute the update todo use case.

        Args:
            todo_id: ID of the todo to update
            user_id: ID of the user requesting the update
            title: Optional new title
            description: Optional new description
            due_date: Optional new due date
            status: Optional new status
            priority: Optional new priority

        Returns:
            Todo: Updated todo entity

        Raises:
            ValueError: If todo not found, user not found, or ownership validation fails
            RuntimeError: If todo update fails

        Note:
            Only the todo owner can update their todos.
            At least one field must be provided for update.
        """
        try:
            # Validate that user exists
            if not self.user_repository.exists(user_id):
                raise ValueError(f"User with id {user_id} not found")

            # Get the existing todo
            todo = self.todo_repository.find_by_id(todo_id)
            if not todo:
                raise ValueError(f"Todo with id {todo_id} not found")

            # Validate ownership
            if todo.user_id != user_id:
                raise ValueError(
                    f"Todo with id {todo_id} not found"
                )  # Don't reveal existence

            # Check that at least one field is being updated
            if all(
                param is None
                for param in [title, description, due_date, status, priority]
            ):
                raise ValueError("At least one field must be provided for update")

            # Update fields if provided
            if title is not None:
                todo.title = title
            if description is not None:
                todo.description = description
            if due_date is not None:
                todo.due_date = due_date
            if status is not None:
                todo.status = status
            if priority is not None:
                todo.priority = priority

            return self.todo_repository.save(todo)
        except ValueError:
            # Re-raise ValueError as-is for proper API error handling
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to update todo: {str(e)}") from e
