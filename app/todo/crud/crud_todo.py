from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.todo.models.todo import Todo
from app.todo.schemas.todo import TodoCreate, TodoPriority, TodoStatus, TodoUpdate


class TodoCRUD:
    """CRUD operations for Todo model."""

    def get(self, db: Session, todo_id: int) -> Todo | None:
        """Get todo by ID."""
        return db.query(Todo).filter(Todo.id == todo_id).first()

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: TodoStatus | None = None,
        priority: TodoPriority | None = None,
    ) -> list[Todo]:
        """Get multiple todos with optional filters."""
        query = db.query(Todo)

        filters = []
        if status:
            filters.append(Todo.status == status)
        if priority:
            filters.append(Todo.priority == priority)

        if filters:
            query = query.filter(and_(*filters))

        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: TodoCreate) -> Todo:
        """Create new todo."""
        db_obj = Todo(
            title=obj_in.title,
            description=obj_in.description,
            due_date=obj_in.due_date,
            priority=obj_in.priority,
            status=obj_in.status,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Todo, obj_in: TodoUpdate) -> Todo:
        """Update existing todo."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, todo_id: int) -> Todo | None:
        """Delete todo by ID."""
        db_obj = db.query(Todo).filter(Todo.id == todo_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

    def get_by_status(self, db: Session, status: TodoStatus) -> list[Todo]:
        """Get todos by status."""
        return db.query(Todo).filter(Todo.status == status).all()

    def count(self, db: Session) -> int:
        """Count total todos."""
        return db.query(Todo).count()


todo = TodoCRUD()
