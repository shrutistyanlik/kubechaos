import random

from kubernetes import client
from rich.console import Console

from kubechaos.safety import pre_chaos_check

console = Console()


def kill_pod(
    api: client.CoreV1Api,
    namespace: str,
    pod_name: str = None,
    force: bool = False,
    dry_run: bool = False,
) -> str:
    pre_chaos_check(api, namespace, force=force)
    pods = api.list_namespaced_pod(namespace)

    if not pods.items:
        console.print(f"[yellow]No pods found in namespace {namespace}[/yellow]")
        return ""

    target = pod_name or random.choice(pods.items).metadata.name

    if dry_run:
        console.print(f"[cyan][DRY RUN] Would delete pod: {target}[/cyan]")
        return target

    api.delete_namespaced_pod(target, namespace)
    console.print(f"[red]Deleted pod: {target}[/red]")
    return target


def scramble_labels(
    api: client.CoreV1Api,
    namespace: str,
    pod_name: str = None,
    force: bool = False,
    dry_run: bool = False,
) -> str:
    pre_chaos_check(api, namespace, force=force)
    pods = api.list_namespaced_pod(namespace)

    if not pods.items:
        console.print(f"[yellow]No pods found in namespace {namespace}[/yellow]")
        return ""

    target_pod = None
    if pod_name:
        for p in pods.items:
            if p.metadata.name == pod_name:
                target_pod = p
                break
    else:
        target_pod = random.choice(pods.items)

    if not target_pod:
        console.print(f"[yellow]Pod '{pod_name}' not found[/yellow]")
        return ""

    target = target_pod.metadata.name
    original_labels = target_pod.metadata.labels or {}
    chaos_labels = {k: f"chaos-{v}" for k, v in original_labels.items()}

    if dry_run:
        console.print(f"[cyan][DRY RUN] Would scramble labels for pod: {target}[/cyan]")
        return target

    body = {"metadata": {"labels": chaos_labels}}
    api.patch_namespaced_pod(target, namespace, body)
    console.print(f"[red]Scrambled labels for pod: {target}[/red]")
    return target
