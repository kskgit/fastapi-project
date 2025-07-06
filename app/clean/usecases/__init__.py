"""UseCases layer - Application use cases and business workflows.

This layer contains:
- Individual use case implementations
- Application-specific business logic
- Orchestration of domain entities and services
- Dependency only on Domain layer interfaces

Clean Architecture Rules:
- Can only depend on Domain layer
- Cannot depend on API, Services, or Infrastructure layers
- Each UseCase should have a single responsibility (execute method)
"""
