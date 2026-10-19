import click
import sys
from typing import Optional
from utils.utils import delete_user, collect_input_data
from utils.logger import dfl_logger as Logger


@click.command()
@click.option("--username", "-u", help="Username of the user to delete", type=str)
@click.option("--input", "input_json", help="JSON input with username", type=str)
@click.option(
    "-w",
    "--what-if",
    is_flag=True,
    help="Show what would happen without making changes",
)
def delete(username: Optional[str], input_json: Optional[str], what_if: bool):
    """
    Delete a Linux user.

    This command deletes a specified Linux user from the system.
    """
    try:
        data = collect_input_data(username=username, input_json=input_json)

        username_to_delete = data.get("username")

        if not username_to_delete:
            Logger.error("Username is required to delete a user.", target="delete")
            sys.exit(1)

        Logger.info(
            f"Processing delete request for user: {username_to_delete}", target="delete"
        )

        delete_user(username=username_to_delete, what_if=what_if)

    except Exception as e:
        Logger.error(f"Failed to process delete command: {str(e)}", target="delete")
        sys.exit(1)
