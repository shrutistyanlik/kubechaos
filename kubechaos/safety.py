from kubernetes import client

PROTECTED_NAMESPACES = frozenset({"kube-system", "kube-public", "default"})


class SafetyError(Exception):
    pass


def validate_namespace(namespace: str) -> None:
    if namespace in PROTECTED_NAMESPACES:
        raise SafetyError(
            f"Namespace '{namespace}' is protected. " f"Use --force to override."
        )


def get_health_snapshot(api: client.CoreV1Api, namespace: str) -> dict:
    pods = api.list_namespaced_pod(namespace)
    return {
        "namespace": namespace,
        "total_pods": len(pods.items),
        "running": sum(1 for p in pods.items if p.status.phase == "Running"),
        "not_running": [
            p.metadata.name for p in pods.items if p.status.phase != "Running"
        ],
    }


def pre_chaos_check(api: client.CoreV1Api, namespace: str, force: bool = False) -> dict:
    if not force:
        validate_namespace(namespace)
    return get_health_snapshot(api, namespace)
