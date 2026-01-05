from app.domain.exceptions import TodoNotFoundException, UserNotFoundException
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository


class SubTaskDomainService:
    async def ensure_todo_user_can_modify_subtask(
        self,
        user_id: int,
        todo_id: int,
        user_repository: UserRepository,
        todo_repository: TodoRepository,
    ) -> bool:
        todo = await todo_repository.find_by_id(todo_id=todo_id)
        if todo is None:
            raise TodoNotFoundException(todo_id=todo_id)

        # TODO todoのuseridと引数のuseridの一致確認

        user = await user_repository.find_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundException(user_id=user_id)

        # TODO userの権限確認

        return True
