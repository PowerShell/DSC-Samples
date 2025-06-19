import click
import sys
import os
from commands.get import get
from commands.set import set
from commands.delete import delete
from commands.export import export

@click.group(invoke_without_command=True)
@click.pass_context
def root_command(ctx):
    """Linux User Management CLI."""

    ctx.ensure_object(dict)

    if os.name != 'nt' and hasattr(os, 'geteuid') and os.geteuid() != 0:
        click.echo("This program requires root privileges to manage users. Please run with sudo.")
        sys.exit(1)

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

# Register all available commands
root_command.add_command(get, name="get")
root_command.add_command(set, name="set")
root_command.add_command(delete, name="delete")
root_command.add_command(export, name="export")