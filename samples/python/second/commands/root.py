import click
import sys
import os
from utils.logger import setup_logger
from commands.get import get
from commands.set import set

# Setup logger for root commands
logger = setup_logger('commands.root')

@click.group(invoke_without_command=True)
@click.pass_context
def root_command(ctx):
    """Linux User Management CLI - Root Command."""

    ctx.ensure_object(dict)
    ctx.obj['logger'] = logger

    if os.name != 'nt' and hasattr(os, 'geteuid') and os.geteuid() != 0:
        click.echo("This program requires root privileges to manage users. Please run with sudo.")
        sys.exit(1)

    ctx.obj['logger'].info("Starting Linux User Management CLI")

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

# Register all available commands
root_command.add_command(get, name="get")
root_command.add_command(set, name="set")