import click
import json
import sys
from utils.logger import Logger
from config.config import Settings

# Create a logger instance for this module
logger = Logger()

@click.command('get')
@click.option('--input', 'input_json', 
              help='JSON input data with required scope field', 
              required=True,
              type=str)
def get_command(input_json):
    """Get command that retrieves configuration based on scope from validated JSON input"""
    
    try:
        try:
            data = json.loads(input_json)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format - {e}", "get_command", input_data=input_json)
            sys.exit(1)
        
        if not Settings.validate_input(data, logger):
            sys.exit(1)
        
        settings = Settings.from_dict(data)
        
        if not settings.validate():
            logger.error(f"Settings validation failed for scope: {settings.scope}", "get_command", scope=settings.scope)
            sys.exit(1)
        
        logger.info(f"Processing settings for scope: {settings.scope}", "get_command", scope=settings.scope)
        
        result_settings, err = settings.enforce()
        if err:
            logger.error(f"Failed to enforce settings for scope {settings.scope}", "get_command", 
                        scope=settings.scope, error_details=str(err))
            sys.exit(1)
        
        result_settings.print_config()
        logger.info(f"Settings retrieved successfully for scope: {settings.scope}", "get_command", 
                   scope=settings.scope)
        
        return result_settings
        
    except Exception as e:
        logger.critical(f"Unexpected error in get_command", "get_command", 
                       error_type=type(e).__name__, error_message=str(e))
        sys.exit(1)