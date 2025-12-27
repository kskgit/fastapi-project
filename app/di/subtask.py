from app.usecases.subtask.create_subtask_usecase import CreateSubTaskUseCase


def get_create_subtask_usecase() -> CreateSubTaskUseCase:
    return CreateSubTaskUseCase()
