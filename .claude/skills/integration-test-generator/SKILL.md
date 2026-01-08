---
name: integration-test-generator
description: Generate FastAPI integration tests following project-specific conventions. Use when the user requests to create, write, or add integration tests for endpoints, controllers, or APIs. Triggered by phrases like "create integration test for X", "write tests for the Y endpoint", "add test coverage for Z", or "generate integration tests".
---

# Integration Test Generator

## Overview

This skill generates integration tests for FastAPI endpoints following this project's specific testing conventions, naming patterns, and structural requirements.

## Workflow

When asked to create integration tests, follow these steps:

### Step 1: Understand the Target Endpoint

Read the endpoint/controller file to understand:
- Endpoint path and HTTP method
- Request/response schemas (DTOs)
- Expected status codes (200, 400, 404, 422, 500, etc.)
- Business logic and validation rules
- Dependencies (UseCases, Repositories, DomainServices)

### Step 2: Read Testing Guidelines

Read `references/integration.md` to understand:
- File naming conventions
- Test method naming conventions
- Required test scenarios (200系, 400系, 500系)
- Mock usage rules (only for 500 系 unexpected_exception scenarios)
- Response validation requirements

### Step 3: Review Example Tests

Review existing test files in `references/examples/`:
- `conftest.py` - Test fixtures and client setup
- `test_todo_create_todo.py` - Comprehensive example with success and failure cases
- `test_user_create_user.py` - Additional pattern examples

Pay attention to:
- Import statements and their structure
- Test class naming (`TestXxxxIntegration`)
- Fixture usage (`test_client`, `test_user`)
- Arrange-Act-Assert pattern
- Response validation patterns
- Database verification patterns
- Mock setup for 500 系 tests

### Step 4: Generate Test File

Create the test file following these conventions:

**File naming:** `test_{controller_file}_{method_name}_{condition}.py`
- Example: `test_todo_create_todo.py` for `todo_controller.py/create_todo`

**Test class naming:** `TestXxxxIntegration` where Xxxx matches the operation
- Example: `TestCreateTodoIntegration`

**Test method naming:** `test_{method_name}_{success|failure}_{reason}`
- Success examples: `test_create_todo_success_minimal_data`
- Failure examples: `test_create_todo_failure_missing_user_id`

**Required test scenarios:**
1. **200系 Success Cases** (Required)
   - At least one successful operation test
   - Verify response status code and data
   - Verify data persistence by reading back from database

2. **400系 Validation/Business Logic Errors**
   - **422** Pydantic validation errors (required fields, type mismatches)
   - **400** Business logic errors (custom validation, domain rules)
   - **404** Not found errors (missing entities)
   - Verify `detail` field in error responses

3. **500系 Unexpected Errors** (Required)
   - Use `unexpected_exception` scenario
   - Mock ONLY the Repository dependency using `AsyncMock`
   - Use `app.dependency_overrides` to replace `get_xxx_repository`
   - Make repository raise `Exception("unexpected_exception")`
   - DO NOT mock UseCases or other layers
   - Verify 500 status and "Internal Server Error" in detail
   - Clean up override in `finally` block

**Code structure:**
```python
"""Integration tests for XxxUseCase via HTTP endpoints."""

from unittest.mock import AsyncMock
import pytest
from httpx import AsyncClient
from app.di.common import get_xxx_repository
from app.domain.repositories.xxx_repository import XxxRepository
from main import app

ENDPOINT = "/path/"

@pytest.mark.asyncio
class TestXxxIntegration:
    """Integration tests for xxx via HTTP API."""

    async def test_xxx_success(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """Test successful operation."""
        # Arrange
        data = {...}

        # Act
        response = await test_client.post(ENDPOINT, json=data)

        # Assert - HTTP response
        assert response.status_code == 201
        response_data = response.json()

        # Assert - Response structure
        assert "id" in response_data
        assert response_data["field"] == data["field"]

        # Assert - Verify persistence
        get_response = await test_client.get(f"{ENDPOINT}{response_data['id']}")
        assert get_response.status_code == 200

    async def test_xxx_failure_validation_error(
        self, test_client: AsyncClient
    ) -> None:
        """Test 422 validation error."""
        # Arrange
        data = {}  # Missing required field

        # Act
        response = await test_client.post(ENDPOINT, json=data)

        # Assert
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "Field required"

    async def test_xxx_failure_unexpected_exception(
        self, test_client: AsyncClient, test_user: User
    ) -> None:
        """Test 500 error handling."""
        # Arrange
        data = {...}
        failing_repository = AsyncMock(spec=XxxRepository)
        failing_repository.create.side_effect = Exception("unexpected_exception")
        app.dependency_overrides[get_xxx_repository] = lambda: failing_repository

        try:
            # Act
            response = await test_client.post(ENDPOINT, json=data)

            # Assert
            assert response.status_code == 500
            assert "Internal Server Error" in response.json()["detail"]
        finally:
            app.dependency_overrides.pop(get_xxx_repository, None)
```

## Important Rules

1. **No mocks except for 500 系 tests** - All other tests use real database and dependencies
2. **Mock only Repository layer** - For 500 tests, mock ONLY the repository, not UseCases or DomainServices
3. **Use app.dependency_overrides** - Proper way to replace dependencies in tests
4. **Clean up overrides** - Always use try/finally to remove overrides
5. **Verify responses thoroughly** - Check both status codes and response body structure
6. **Follow existing patterns** - Match the style and structure of example tests

## Resources

### references/integration.md
Complete testing guidelines including:
- File and method naming conventions
- Required test scenarios
- Mock usage rules
- Response validation requirements

### references/examples/
Example test files demonstrating:
- `conftest.py` - Test fixtures and setup
- `test_todo_create_todo.py` - Comprehensive test patterns
- `test_user_create_user.py` - Additional examples

Review these files when generating tests to maintain consistency with existing codebase patterns.
