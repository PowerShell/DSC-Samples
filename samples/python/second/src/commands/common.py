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
        "--username",
        help="Username for authentication",
        type=str,
        required=False,
    )(function)
    
    function = click.option(
        "--password",
        help="Password for authentication",
        type=str,
        required=False,
        hide_input=True,
    )(function)
    
    # Add additional user properties
    function = click.option(
        "--uid",
        help="User ID number",
        type=int,
        required=False,
    )(function)
    
    function = click.option(
        "--gid",
        help="Primary group ID",
        type=int,
        required=False,
    )(function)
    
    function = click.option(
        "--home",
        help="Home directory path",
        type=str,
        required=False,
    )(function)
    
    function = click.option(
        "--shell",
        help="Login shell path",
        type=str,
        required=False,
    )(function)
    
    return function