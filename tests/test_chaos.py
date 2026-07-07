from unittest.mock import MagicMock

import pytest

from kubechaos.chaos import kill_pod, scramble_labels
from kubechaos.safety import SafetyError


def make_mock_pod(name, phase="Running", labels=None):
    pod = MagicMock()
    pod.metadata.name = name
    pod.status.phase = phase
    pod.metadata.labels = labels or {"app": "web"}
    return pod


def make_mock_api(pods):
    api = MagicMock()
    api.list_namespaced_pod.return_value.items = pods
    return api


class TestKillPod:
    def test_kills_specific_pod(self):
        api = make_mock_api([make_mock_pod("pod-1"), make_mock_pod("pod-2")])
        result = kill_pod(api, "my-app", pod_name="pod-1", force=True)
        assert result == "pod-1"
        api.delete_namespaced_pod.assert_called_once_with("pod-1", "my-app")

    def test_kills_random_pod(self):
        pods = [make_mock_pod("pod-1"), make_mock_pod("pod-2")]
        api = make_mock_api(pods)
        result = kill_pod(api, "my-app", force=True)
        assert result in ["pod-1", "pod-2"]
        api.delete_namespaced_pod.assert_called_once()

    def test_dry_run_does_not_delete(self):
        api = make_mock_api([make_mock_pod("pod-1")])
        result = kill_pod(api, "my-app", dry_run=True, force=True)
        assert result == "pod-1"
        api.delete_namespaced_pod.assert_not_called()

    def test_empty_namespace_returns_empty(self):
        api = make_mock_api([])
        result = kill_pod(api, "my-app", force=True)
        assert result == ""

    def test_blocks_protected_namespace(self):
        api = make_mock_api([make_mock_pod("pod-1")])
        with pytest.raises(SafetyError):
            kill_pod(api, "kube-system")


class TestScrambleLabels:
    def test_scrambles_specific_pod(self):
        api = make_mock_api([make_mock_pod("pod-1", labels={"app": "web"})])
        result = scramble_labels(api, "my-app", pod_name="pod-1", force=True)
        assert result == "pod-1"
        api.patch_namespaced_pod.assert_called_once_with(
            "pod-1",
            "my-app",
            {"metadata": {"labels": {"app": "chaos-web"}}},
        )

    def test_dry_run_does_not_patch(self):
        api = make_mock_api([make_mock_pod("pod-1")])
        result = scramble_labels(
            api, "my-app", pod_name="pod-1", dry_run=True, force=True
        )
        assert result == "pod-1"
        api.patch_namespaced_pod.assert_not_called()

    def test_pod_not_found_returns_empty(self):
        api = make_mock_api([make_mock_pod("pod-1")])
        result = scramble_labels(api, "my-app", pod_name="nonexistent", force=True)
        assert result == ""

    def test_empty_namespace_returns_empty(self):
        api = make_mock_api([])
        result = scramble_labels(api, "my-app", force=True)
        assert result == ""

    def test_blocks_protected_namespace(self):
        api = make_mock_api([make_mock_pod("pod-1")])
        with pytest.raises(SafetyError):
            scramble_labels(api, "default")
