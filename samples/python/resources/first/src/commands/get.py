import click
import sys
from utils.logger import Logger
from config.config import Settings
from commands.common import common

logger = Logger()

@click.command("get")
@common
def get_command(input_json, scope, exist, updateAutomatically, updateFrequency):
    """Gets the current state of a tstoy configuration file."""
    try:
        data = Settings.validate(
            input_json, scope, exist, updateAutomatically, updateFrequency, 'get', logger
        )

        settings = Settings.from_dict(data)

        result_settings, err = Settings.get_current_state(settings, logger)
        if err:
            logger.error(f"Failed to get settings: {err}", "get_command")
            sys.exit(1)

        result_settings.print_config()
        
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}", "get_command")
        sys.exit(1)