import click
from commands.get import get_command


@click.group()
def main():
    """Python TSToy CLI tool."""
    pass

# TODO: Add more commands and move away in main.py
main.add_command(get_command)


if __name__ == '__main__':
    main()
