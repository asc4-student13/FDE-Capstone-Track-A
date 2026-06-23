"""Unit tests for the mock data loader functions."""

from __future__ import annotations

from data.loader import load_budgets, load_policies, load_requests, load_vendors


def test_loader_exposes_all_mock_data_files() -> None:
    budgets = load_budgets()
    vendors = load_vendors()
    policies = load_policies()
    requests = load_requests()

    assert isinstance(budgets, list) and budgets
    assert isinstance(vendors, list) and vendors
    assert isinstance(policies, list) and policies
    assert isinstance(requests, list) and requests


def test_loader_key_fields_present_for_joins() -> None:
    assert "cost_center_id" in load_budgets()[0]
    assert "vendor_id" in load_vendors()[0]
    assert "category" in load_vendors()[0]
    assert "affected_categories" in load_policies()[0]
    assert "cost_center_id" in load_requests()[0]
    assert "vendor_id" in load_requests()[0]
