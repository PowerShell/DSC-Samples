import click
from typing import Optional
from commands.common import common
from utils.utils import get_input

@click.command()
@common
@click.option('-w', '--what-if', is_flag=True, help='Show what would happen without making changes')
def set(
    username: Optional[str],
    password: Optional[str],
    input_json: Optional[str],
    uid: Optional[int],
    gid: Optional[int],
    home: Optional[str],
    shell: Optional[str],
    what_if: bool
):
    """
    Create or update a Linux user.
    
    This command takes either command line parameters or a JSON input to create or
    modify a Linux user. If the user already exists, it will be updated.
    
    Note: Group membership is read-only and cannot be modified with this command.
    """
    user = get_input(
            username=username,
            password=password,
            input_json=input_json,
            uid=uid,
            gid=gid,
            home=home,
            shell=shell
        )
        
    user.modify(what_if=what_if)