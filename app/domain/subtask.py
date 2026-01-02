from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SubTask:
    title: str

    @classmethod
    def create(cls, title: str) -> SubTask:
        return cls(title=title)
