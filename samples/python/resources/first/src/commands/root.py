import click
from utils.logger import Logger
from schema.schema import get_schema
from commands.get import get_command
from commands.set import set_command
from commands.export import export_command

logger = Logger()

# Custom group class for better help formatting
class CustomGroup(click.Group):
    def format_help(self, ctx, formatter):
        super().format_help(ctx, formatter)
        
        formatter.write("""
Flags:
  --input TEXT                     JSON input data with settings
  --scope [user|machine]           Target configuration scope (user or machine)
  --exist                          Whether the configuration should exist
  --updateAutomatically            Enable automatic updates
  --updateFrequency INTEGER        Update frequency in days (1-180)
""")
        formatter.write("\nExamples:\n")
        formatter.write("  pythontstoy get --scope user\n")
        formatter.write("  pythontstoy set --scope user --updateAutomatically\n")
        formatter.write("  pythontstoy get --input '{\"scope\": \"user\"}'\n")
        formatter.write("  '{\"scope\": \"user\"}' | pythontstoy set\n")
        formatter.write("  pythontstoy schema\n")

@click.command("schema")
def schema_command():
    """Get the schema of the tstoy configuration."""
    print(get_schema())

@click.command('help')
@click.pass_context
def help_command(ctx):
    """Show help information for commands."""
    parent = ctx.parent
    click.echo(parent.get_help())

@click.group(cls=CustomGroup)
def cli():
    """Command-line tool for managing configurations.
    
    Use 'get' to retrieve configuration or 'set' to modify configuration.
    Use 'schema' to view the configuration schema.
    """
    pass

cli.add_command(get_command)
cli.add_command(set_command)
cli.add_command(schema_command)
cli.add_command(help_command)
cli.add_command(export_command)