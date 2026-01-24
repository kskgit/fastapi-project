"""Composition Root layer.

This layer is responsible for assembling the entire application dependency graph.
It's the only layer allowed to depend on all other layers
(Domain, UseCase, Infrastructure, API).
"""

from .common import (
    get_subtask_repository,
    get_todo_repository,
    get_transaction_manager,
    get_user_repository,
)
from .subtask import get_create_subtask_usecase, get_subtask_domain_service
from .todo import (
    get_create_todo_usecase,
    get_delete_todo_usecase,
    get_get_todo_by_id_usecase,
    get_get_todos_usecase,
    get_update_todo_usecase,
)
from .user import (
    get_create_user_usecase,
    get_delete_user_usecase,
    get_get_user_by_id_usecase,
    get_get_users_usecase,
    get_update_user_usecase,
    get_user_domain_service,
)

__all__ = [
    "get_create_subtask_usecase",
    "get_create_todo_usecase",
    "get_create_user_usecase",
    "get_delete_todo_usecase",
    "get_delete_user_usecase",
    "get_get_todo_by_id_usecase",
    "get_get_todos_usecase",
    "get_get_user_by_id_usecase",
    "get_get_users_usecase",
    "get_subtask_domain_service",
    "get_subtask_repository",
    "get_todo_repository",
    "get_transaction_manager",
    "get_update_todo_usecase",
    "get_update_user_usecase",
    "get_user_domain_service",
    "get_user_repository",
]
