"""Compatibility loader that delegates to the project root data loader."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def _get_root_loader_module() -> ModuleType:
    """Load and return the root data/loader.py module."""
    root_loader_path = Path(__file__).resolve().parents[2] / "data" / "loader.py"
    spec = importlib.util.spec_from_file_location("root_data_loader", root_loader_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load root data loader at {root_loader_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_budgets() -> list[object]:
    """Return all cost center budget records."""
    return _get_root_loader_module().load_budgets()


def load_vendors() -> list[object]:
    """Return all vendor records."""
    return _get_root_loader_module().load_vendors()


def load_policies() -> list[object]:
    """Return all procurement policy records."""
    return _get_root_loader_module().load_policies()


def load_requests() -> list[object]:
    """Return all sample purchase request records."""
    return _get_root_loader_module().load_requests()
