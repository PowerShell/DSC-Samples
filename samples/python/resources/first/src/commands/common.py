import click

def common(function):
    """Add common options to click commands"""
    function = click.option(
        "--input",
        "input_json",
        help="JSON input data with settings",
        required=False,
        type=str,
    )(function)
    
    function = click.option(
        "--scope",
        help="Target configuration scope (user or machine)",
        type=click.Choice(["user", "machine"]),
        required=False,
    )(function)
    
    function = click.option(
        "--exist",
        "exist",
        help="Check if configuration exists",
        is_flag=True,
        default=None,
    )(function)
    
    function = click.option(
        "--updateAutomatically",
        "updateAutomatically", 
        help="Whether updates should be automatic",
        type=bool,
        required=False,
    )(function)
    
    function = click.option(
        "--updateFrequency",
        "updateFrequency", 
        help="Update frequency in days (1-180)",
        type=int,
        required=False,
    )(function)
    
    return function