from typing import Protocol

from fastapi import Depends
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.todo.models.todo import Todo as TodoModel
from app.todo.schemas.todo import Todo as TodoDTO
from app.todo.schemas.todo import TodoCreate, TodoPriority, TodoStatus, TodoUpdate


class TodoCRUDInterface(Protocol):
    """Interface for Todo CRUD operations."""

    def get(self, todo_id: int) -> TodoDTO | None: ...

    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        status: TodoStatus | None = None,
        priority: TodoPriority | None = None,
    ) -> list[TodoDTO]: ...

    def create(self, obj_in: TodoCreate) -> TodoDTO: ...

    def update(self, db_obj: TodoDTO, obj_in: TodoUpdate) -> TodoDTO: ...

    def delete(self, todo_id: int) -> TodoDTO | None: ...

    def get_by_status(self, status: TodoStatus) -> list[TodoDTO]: ...

    def count(self) -> int: ...


class TodoCRUD(TodoCRUDInterface):
    """CRUD operations for Todo model."""

    def __init__(self, db: Session):
        self.db = db

    def get(self, todo_id: int) -> TodoDTO | None:
        """Get todo by ID."""
        db_obj = self.db.query(TodoModel).filter(TodoModel.id == todo_id).first()
        return TodoDTO.model_validate(db_obj) if db_obj else None

    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        status: TodoStatus | None = None,
        priority: TodoPriority | None = None,
    ) -> list[TodoDTO]:
        """Get multiple todos with optional filters."""
        query = self.db.query(TodoModel)

        filters = []
        if status:
            filters.append(TodoModel.status == status)
        if priority:
            filters.append(TodoModel.priority == priority)

        if filters:
            query = query.filter(and_(*filters))

        db_objs = query.offset(skip).limit(limit).all()
        return [TodoDTO.model_validate(obj) for obj in db_objs]

    def create(self, obj_in: TodoCreate) -> TodoDTO:
        """Create new todo."""
        db_obj = TodoModel(
            title=obj_in.title,
            description=obj_in.description,
            due_date=obj_in.due_date,
            priority=obj_in.priority,
            status=obj_in.status,
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return TodoDTO.model_validate(db_obj)

    def update(self, db_obj: TodoDTO, obj_in: TodoUpdate) -> TodoDTO:
        """Update existing todo."""
        # DTOからDBモデルに変換
        todo_model = TodoModel(
            id=db_obj.id,
            title=db_obj.title,
            description=db_obj.description,
            due_date=db_obj.due_date,
            priority=db_obj.priority,
            status=db_obj.status,
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at,
        )

        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(todo_model, field, value)

        self.db.add(todo_model)
        self.db.commit()
        self.db.refresh(todo_model)
        return TodoDTO.model_validate(todo_model)

    def delete(self, todo_id: int) -> TodoDTO | None:
        """Delete todo by ID."""
        db_obj = self.db.query(TodoModel).filter(TodoModel.id == todo_id).first()
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return TodoDTO.model_validate(db_obj)
        return None

    def get_by_status(self, status: TodoStatus) -> list[TodoDTO]:
        """Get todos by status."""
        db_objs = self.db.query(TodoModel).filter(TodoModel.status == status).all()
        return [TodoDTO.model_validate(obj) for obj in db_objs]

    def count(self) -> int:
        """Count total todos."""
        return self.db.query(TodoModel).count()


# todo dbセッションを渡す
def getTodoCRID(db: Session = Depends(get_db)) -> TodoCRUD:
    return TodoCRUD(db)


__all__ = [
    "TodoCRUD",
    "getTodoCRID",
]
