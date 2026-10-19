import click
from models.dsc_user import User

@click.command()
def export():
    """
    Export Linux user information.
    
    This command exports information about Linux users in JSON format.
    """
    
    user = User()
    user.export()