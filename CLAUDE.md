# Project Memory

## Code Style and Patterns

### SQLAlchemy Model Style
- Use `mapped_column()` instead of `Column()` (modern SQLAlchemy 2.0+ style)
- Import specific SQLAlchemy types: `DateTime`, `Enum`, `Integer`, `String`
- Import `mapped_column` from `sqlalchemy.orm`
- Use `server_default=func.now()` for timestamps
- Use `onupdate=func.now()` for updated_at fields

### Project Structure
- Database models in `app/models/`
- Pydantic schemas in `app/schemas/`
- Database setup in `app/core/database.py`
- Import enums from schemas into models for consistency

### Task Commands
- Use Taskfile.yml for common development tasks
- Available: `task dev`, `task start`, `task lint`, `task format`, `task lint-fix`, `task check`