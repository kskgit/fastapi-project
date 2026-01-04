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
        user = await user_repository.find_by_id(user_id=user_id)  # noqa: F841 TODO 利用後削除
        todo = await todo_repository.find_by_id(todo_id=todo_id)  # noqa: F841 TODO 利用後削除
        return True
