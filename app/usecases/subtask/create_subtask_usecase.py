class CreateSubTaskUseCase:
    """UseCase for creating a new Todo.

    Single Responsibility: Handle the creation of a new Todo with proper
    business logic validation and error handling using async/await.

    Dependencies:
    - Only depends on Domain layer (TodoRepository and UserRepository interfaces)
    - No dependencies on API, Services, or Infrastructure layers
    """

    async def execute(
        self,
        user_id: int,
        todo_id: int,
        title: str,
    ):
        pass
