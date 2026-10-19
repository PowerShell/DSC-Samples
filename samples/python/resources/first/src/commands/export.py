import click
import json
import sys
from utils.logger import Logger
from config.config import Settings

logger = Logger()

@click.command("export")
def export_command():
    """Export all configuration settings (user and machine) as JSON.
    
    This command retrieves both user and machine configurations and
    outputs them as a JSON object. If a configuration doesn't
    exist, it will show the default values.
    """
    try:
        user_settings = Settings(scope="user")
        machine_settings = Settings(scope="machine")
        
        user_result, user_err = Settings.get_current_state(user_settings, logger)
        machine_result, machine_err = Settings.get_current_state(machine_settings, logger)

        if user_err:
            logger.warning(f"Error retrieving user configuration: {user_err}", "export_command")
        if machine_err:
            logger.warning(f"Error retrieving machine configuration: {machine_err}", "export_command")

        print(user_result.to_json())
        print(machine_result.to_json())

    except Exception as e:
        logger.critical(f"Unexpected error in export command: {str(e)}", "export_command")
        sys.exit(1)