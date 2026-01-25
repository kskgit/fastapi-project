from app.domain.entities import UserRole
from app.domain.exceptions import (
    TodoNotFoundException,
    UserNotFoundException,
    UserPermissionDeniedException,
)
from app.domain.repositories import TodoRepository, UserRepository


class SubTaskDomainService:
    async def ensure_todo_user_can_modify_subtask(
        self,
        user_id: int,
        todo_id: int,
        user_repository: UserRepository,
        todo_repository: TodoRepository,
    ) -> None:
        # First, verify user exists and has permission
        user = await user_repository.find_by_id(user_id=user_id)

        if user is None:
            raise UserNotFoundException(user_id=user_id)

        if user.role == UserRole.VIEWER:
            raise UserPermissionDeniedException(user_id=user_id)

        # Then, verify todo exists and belongs to the user
        todo = await todo_repository.find_by_id(todo_id=todo_id)

        if todo is None:
            raise TodoNotFoundException(todo_id=todo_id)

        if todo.user_id != user_id:
            raise TodoNotFoundException(todo_id=todo_id)
