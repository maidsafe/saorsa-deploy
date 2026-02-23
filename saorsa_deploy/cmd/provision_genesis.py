import sys

from rich.console import Console

from saorsa_deploy.provisioning.genesis import SaorsaGenesisNode
from saorsa_deploy.state import load_deployment_state


def cmd_provision_genesis(args):
    """Execute the provision-genesis command: provision the genesis node."""
    console = Console()

    console.print(f"[bold]Loading deployment state for '{args.name}'...[/bold]")
    try:
        state = load_deployment_state(args.name)
    except RuntimeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)

    bootstrap_ip = state.get("bootstrap_ip")
    if not bootstrap_ip:
        console.print(
            "[bold red]Error:[/bold red] No bootstrap IP found in deployment state. "
            "Was this deployment created with a recent version of the infra command?"
        )
        sys.exit(1)

    console.print(f"[bold]Provisioning genesis node at {bootstrap_ip}...[/bold]")
    console.print(f"  SSH key: {args.ssh_key_path}")
    if args.port:
        console.print(f"  Port: {args.port}")
    if args.ip_version:
        console.print(f"  IP version: {args.ip_version}")
    if args.log_level:
        console.print(f"  Log level: {args.log_level}")
    if args.testnet:
        console.print("  Testnet mode: enabled")
    console.print()

    node = SaorsaGenesisNode(
        ip=bootstrap_ip,
        ssh_key_path=args.ssh_key_path,
        port=args.port,
        ip_version=args.ip_version,
        log_level=args.log_level,
        testnet=args.testnet,
        console=console,
    )

    try:
        node.provision()
        console.print()
        console.print("[bold green]Genesis node provisioned successfully.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Failed to provision genesis node:[/bold red] {e}")
        sys.exit(1)
