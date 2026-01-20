from app.core.transaction_manager import TransactionManager
from app.domain.repositories.subtask_repository import SubTaskRepository
from app.domain.repositories.todo_repository import TodoRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.services.subtask_domain_service import SubTaskDomainService
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
    user_repository: UserRepository
    todo_repository: TodoRepository
    subtask_repository: SubTaskRepository
    subtask_domain_service: SubTaskDomainService

    def __init__(
        self,
        transaction_manager: TransactionManager,
        user_repository: UserRepository,
        todo_repository: TodoRepository,
        subtask_repository: SubTaskRepository,
        subtask_domain_service: SubTaskDomainService,
    ):
        self.transaction_manager = transaction_manager
        self.user_repository = user_repository
        self.todo_repository = todo_repository
        self.subtask_repository = subtask_repository
        self.subtask_domain_service = subtask_domain_service

    async def execute(
        self,
        user_id: int,
        todo_id: int,
        title: str,
    ):
        async with self.transaction_manager.begin_transaction():
            await self.subtask_domain_service.ensure_todo_user_can_modify_subtask(
                user_id=user_id,
                todo_id=todo_id,
                user_repository=self.user_repository,
                todo_repository=self.todo_repository,
            )

            subtask = SubTask.create(
                user_id=user_id,
                todo_id=todo_id,
                title=title,
            )
            return await self.subtask_repository.create(subtask)
