import click
from kubernetes import client, config
from rich.console import Console

from kubechaos.chaos import kill_pod, scramble_labels
from kubechaos.safety import SafetyError, get_health_snapshot

console = Console()


def get_k8s_client() -> client.CoreV1Api:
    config.load_kube_config()
    return client.CoreV1Api()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """KubeChaos - A CLI chaos engineering toolkit for Kubernetes."""
    pass


@main.command()
@click.option("--namespace", "-n", required=True, help="Target namespace")
@click.option("--pod", "-p", default=None, help="Specific pod name (random if omitted)")
@click.option("--force", is_flag=True, help="Override namespace protection")
@click.option("--dry-run", is_flag=True, help="Preview without executing")
def kill(namespace, pod, force, dry_run):
    """Kill a pod to test self-healing."""
    try:
        api = get_k8s_client()
        kill_pod(api, namespace, pod_name=pod, force=force, dry_run=dry_run)
    except SafetyError as e:
        console.print(f"[red]Safety check failed: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@main.command()
@click.option("--namespace", "-n", required=True, help="Target namespace")
@click.option("--pod", "-p", default=None, help="Specific pod name (random if omitted)")
@click.option("--force", is_flag=True, help="Override namespace protection")
@click.option("--dry-run", is_flag=True, help="Preview without executing")
def scramble(namespace, pod, force, dry_run):
    """Scramble pod labels to test service discovery."""
    try:
        api = get_k8s_client()
        scramble_labels(api, namespace, pod_name=pod, force=force, dry_run=dry_run)
    except SafetyError as e:
        console.print(f"[red]Safety check failed: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@main.command()
@click.option("--namespace", "-n", required=True, help="Target namespace")
def health(namespace):
    """Show current health snapshot of a namespace."""
    try:
        api = get_k8s_client()
        snapshot = get_health_snapshot(api, namespace)
        console.print(f"[green]Namespace:[/green] {snapshot['namespace']}")
        console.print(f"[green]Total pods:[/green] {snapshot['total_pods']}")
        console.print(f"[green]Running:[/green] {snapshot['running']}")
        if snapshot["not_running"]:
            console.print(
                f"[yellow]Not running:[/yellow] {', '.join(snapshot['not_running'])}"
            )
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
