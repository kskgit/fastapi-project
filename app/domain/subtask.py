from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SubTask:
    user_id: int
    todo_id: int
    title: str
    is_compleated: bool
    id: int | None = None

    @classmethod
    def create(cls, user_id: int, todo_id: int, title: str) -> SubTask:
        return cls(
            user_id=user_id,
            todo_id=todo_id,
            title=title,
            is_compleated=False,
            id=None,
        )
