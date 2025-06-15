# FastAPI Project

A FastAPI project template using uv for dependency management and ruff for code formatting and linting.

## Setup

### Prerequisites

- [uv](https://docs.astral.sh/uv/) - Python package manager
- [Task](https://taskfile.dev/) - Task runner
- [lefthook](https://github.com/evilmartians/lefthook) - Git hooks manager

### Installation

1. Install dependencies:
```bash
uv install
```

2. Start PostgreSQL database:
```bash
task db-up
```

3. Run database migrations:
```bash
task migrate
```

4. Install Git hooks:
```bash
lefthook install
```

## Available Commands

- `task dev` - Start development server with hot reload
- `task start` - Start production server
- `task lint` - Run ruff linter
- `task format` - Format code with ruff
- `task lint-fix` - Fix linting issues automatically
- `task check` - Run all checks (lint + format check)
- `task db-up` - Start PostgreSQL container
- `task db-down` - Stop PostgreSQL container
- `task migrate` - Run database migrations
- `task migrate-auto` - Generate migration from model changes