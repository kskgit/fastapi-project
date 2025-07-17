"""Composition Root layer.

This layer is responsible for assembling the entire application dependency graph.
It's the only layer allowed to depend on all other layers
(Domain, UseCase, Infrastructure, API).
"""
