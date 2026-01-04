from app.core.transaction_manager import TransactionManager
from app.domain.subtask import SubTask


class CreateSubTaskUseCase:
    """UseCase for creating a new Todo.

    Single Responsibility: Handle the creation of a new Todo with proper
    business logic validation and error handling using async/await.

    Dependencies:
    - Only depends on Domain layer (TodoRepository and UserRepository interfaces)
    - No dependencies on API, Services, or Infrastructure layers
    """

    transaction_manager: TransactionManager

    def __init__(
        self,
        transaction_manager: TransactionManager,
    ):
        self.transaction_manager = transaction_manager

    async def execute(
        self,
        user_id: int,
        todo_id: int,
        title: str,
    ):
        async with self.transaction_manager.begin_transaction():
            # TODO Userの権限確認
            # Userの存在
            # 親のTodoの所有者がuser_idと一致していること
            # Userのロールがmember以上であること
            # TODO 親のTodo存在チェック
            return SubTask.create(
                user_id=user_id,
                todo_id=todo_id,
                title=title,
            )
            # TODO Repository経由で永続化
