import click
import sys
from utils.logger import Logger
from config.config import Settings
from commands.common import common
logger = Logger()

@click.command("set")
@common
def set_command(input_json, scope, exist, updateAutomatically, updateFrequency):
    """Sets a tstoy configuration file to the desired state."""

    data = Settings.validate(
        input_json, scope, exist, updateAutomatically, updateFrequency, 'set', logger
    )

    try:
        settings = Settings.from_dict(data)

        result, err = Settings.enforce(settings, logger)
        if err:
            logger.error(f"Failed to set configuration: {err}", "set_command")
            sys.exit(1)

    except Exception as e:
        logger.critical(
            "Unexpected error in set_command",
            "set_command",
            error_type=type(e).__name__,
            error_message=str(e),
        )
        sys.exit(1)
