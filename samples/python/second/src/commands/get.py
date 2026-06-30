import click
from utils.utils import get_input, get_requested_properties
from commands.common import common



@click.command()
@common
def get(username, password, input_json, uid, gid, home, shell):
    """
    Get Linux user information.
    
    This command takes either command line parameters or a JSON input to retrieve
    information about a Linux user.
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
    
    requested_properties = get_requested_properties(user)

    user.get_current_state(requested_properties)