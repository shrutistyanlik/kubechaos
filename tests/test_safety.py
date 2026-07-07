import pytest
from unittest.mock import MagicMock

from kubechaos.safety import (
    validate_namespace,
    get_health_snapshot,
    pre_chaos_check,
    SafetyError,
    PROTECTED_NAMESPACES,
)


def test_validate_namespace_blocks_protected():
    for ns in PROTECTED_NAMESPACES:
        with pytest.raises(SafetyError):
            validate_namespace(ns)


def test_validate_namespace_allows_custom():
    validate_namespace("my-app")


def test_get_health_snapshot():
    mock_api = MagicMock()

    mock_pod_running = MagicMock()
    mock_pod_running.status.phase = "Running"
    mock_pod_running.metadata.name = "pod-1"

    mock_pod_pending = MagicMock()
    mock_pod_pending.status.phase = "Pending"
    mock_pod_pending.metadata.name = "pod-2"

    mock_api.list_namespaced_pod.return_value.items = [
        mock_pod_running,
        mock_pod_pending,
    ]

    snapshot = get_health_snapshot(mock_api, "my-app")

    assert snapshot["namespace"] == "my-app"
    assert snapshot["total_pods"] == 2
    assert snapshot["running"] == 1
    assert snapshot["not_running"] == ["pod-2"]


def test_pre_chaos_check_blocks_without_force():
    mock_api = MagicMock()
    with pytest.raises(SafetyError):
        pre_chaos_check(mock_api, "kube-system")


def test_pre_chaos_check_allows_with_force():
    mock_api = MagicMock()
    mock_api.list_namespaced_pod.return_value.items = []
    snapshot = pre_chaos_check(mock_api, "kube-system", force=True)
    assert snapshot["total_pods"] == 0
