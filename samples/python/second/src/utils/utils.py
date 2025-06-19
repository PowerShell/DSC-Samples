import sys
import json
import subprocess
import grp
import pwd
import os
from schema.schema import validate_user_data
from typing import Dict, Any, Optional
from utils.logger import dfl_logger as Logger


def read_stdin() -> str:
    return sys.stdin.read().strip()


def parse_json_input(data: str) -> Dict[str, Any]:
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON input: {str(e)}")

def get_input(
    username: Optional[str] = None,
    password: Optional[str] = None,
    input_json: Optional[str] = None,
    uid: Optional[int] = None,
    gid: Optional[int] = None,
    home: Optional[str] = None,
    shell: Optional[str] = None,
):
    from models.dsc_user import User

    combined_data = collect_input_data(
        username=username,
        password=password,
        input_json=input_json,
        uid=uid,
        gid=gid,
        home=home,
        shell=shell,
    )

    validate_user_data(combined_data)

    user = User()

    for key, value in combined_data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    return user


def collect_input_data(
    username: Optional[str] = None,
    password: Optional[str] = None,
    input_json: Optional[str] = None,
    uid: Optional[int] = None,
    gid: Optional[int] = None,
    home: Optional[str] = None,
    shell: Optional[str] = None,
) -> Dict[str, Any]:
    combined_data = {}

    # Process JSON input if provided
    if input_json:
        try:
            if input_json.startswith("{"):
                json_data = parse_json_input(input_json)
            else:
                with open(input_json, "r") as f:
                    json_data = json.load(f)

            combined_data.update(json_data)

        except (ValueError, IOError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse JSON input: {str(e)}")
    else:
        # Try to read from stdin if no JSON input was explicitly provided
        try:
            if not sys.stdin.isatty():
                stdin_data = read_stdin()
                if stdin_data:
                    json_data = parse_json_input(stdin_data)
                    combined_data.update(json_data)
        except (ValueError, EOFError) as e:
            pass

    cli_data = {}

    if username is not None:
        cli_data["username"] = username

    if password is not None:
        cli_data["password"] = password

    if uid is not None:
        cli_data["uid"] = uid

    if gid is not None:
        cli_data["gid"] = gid

    if home is not None:
        cli_data["home"] = home

    if shell is not None:
        cli_data["shell"] = shell

    if cli_data:
        combined_data.update(cli_data)

    return combined_data


def check_user_exist(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Check if a user exists in the system and return user information.

    Args:
        user_id: The user ID to check

    Returns:
        Dictionary with username, uid, and gid if user exists, None otherwise
    """
    try:
        result = subprocess.run(
            ["id", str(user_id)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode == 0:
            output = result.stdout.strip()

            uid_part = output.split()[0]  # uid=1000(username)
            username = uid_part.split("(")[1].rstrip(")")
            uid = int(uid_part.split("=")[1].split("(")[0])

            gid_part = output.split()[1]  # gid=1000(groupname)
            gid = int(gid_part.split("=")[1].split("(")[0])

            return {"username": username, "uid": uid, "gid": gid}
    except (subprocess.SubprocessError, ValueError, IndexError):
        pass
    return None


def create_user(
    username: str,
    password: Optional[str] = None,
    uid: Optional[int] = None,
    gid: Optional[int] = None,
    home: Optional[str] = None,
    shell: Optional[str] = None,
) -> None:
    cmd = ["adduser", "--quiet"]

    # Add optional parameters if provided
    if home:
        cmd.extend(["--home", home])

    if shell:
        cmd.extend(["--shell", shell])
    if uid is not None:
        cmd.extend(["--uid", str(uid)])

    if gid is not None:
        try:
            group_name = grp.getgrgid(gid).gr_name
            cmd.extend(["--gid", group_name])
        except KeyError:
            raise ValueError(f"Group ID {gid} does not exist")

    cmd.append(username)
    Logger.info(
        "Creating user", "user_management", command="adduser", username=username
    )

    result = run_command(
        cmd, prevent_input=True, command_name="Create user", username=username
    )

    if result and result.returncode == 0 and password:
        set_password(username, password)


def set_password(username: str, password: str) -> None:
    """
    Set or update a user's password.

    Args:
        username: The username to set password for
        password: The new password

    Raises:
        RuntimeError: If setting the password fails
    """
    if not username or not password:
        Logger.error(
            "Username and password are required for setting password",
            "user_management",
            username=username,
        )
        sys.exit(4)

    Logger.info("Setting password for user", "user_management", username=username)

    input_str = f"{username}:{password}\n"

    try:
        run_command(
            ["chpasswd"],
            input_str=input_str,
            command_name="Set password",
            username=username,
        )
    except RuntimeError as e:
        error_msg = str(e)
        sanitized_error = error_msg.replace(password, "********")
        raise RuntimeError(f"Failed to set password: {sanitized_error}")

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode("utf-8") if hasattr(e, "stderr") else str(e)
        # Don't include the password in error messages
        sanitized_error = error_msg.replace(password, "********")
        Logger.error(
            "Failed to set password",
            "user_management",
            username=username,
            error=sanitized_error,
        )
        raise RuntimeError(f"Failed to set password: {sanitized_error}")
    except Exception as e:
        Logger.error(
            "Error setting password", "user_management", username=username, error=str(e)
        )
        raise RuntimeError(f"Error setting password: {str(e)}")


def update_user(
    username: str,
    password: Optional[str] = None,
    uid: Optional[int] = None,
    gid: Optional[int] = None,
    home: Optional[str] = None,
    shell: Optional[str] = None,
) -> None:
    cmd = ["usermod"]

    if uid is not None:
        cmd.extend(["-u", str(uid)])

    if gid is not None:
        cmd.extend(["-g", str(gid)])

    if home:
        cmd.extend(["-d", home, "-m"])

    if shell:
        cmd.extend(["-s", shell])

    if password:
        print("Setting password for user", username)
        set_password(username, password)

    if len(cmd) == 1:
        Logger.debug(
            "No changes specified for user", "user_management", username=username
        )
        return

    cmd.append(username)

    Logger.info(
        "Updating user", "user_management", command="usermod", username=username
    )

    run_command(cmd, command_name="Update user", username=username)


def delete_user(username: str, what_if: bool = False) -> None:
    user = check_user_exist(username)
    if not user:
        return

    cmd = ["userdel"]
    cmd.append(username)

    if what_if:
        print(
            json.dumps(
                {
                    "username": username,
                    "_metadata": {
                        "whatIf": [f"User '{username}' exists and will be deleted."]
                    },
                }
            )
        )
        return

    Logger.info(
        "Deleting user", "user_management", command="delete_user", username=username
    )

    run_command(cmd, command_name="Delete user", username=username)


def export_user() -> str:
    """
    Export all users in JSON format.

    Returns:
        JSON string containing all user information
    """
    users = []

    try:
        for user_entry in pwd.getpwall():
            user_info = {
                "username": user_entry.pw_name,
                "uid": user_entry.pw_uid,
                "gid": user_entry.pw_gid,
                "home": user_entry.pw_dir,
                "shell": user_entry.pw_shell,
                "groups": get_user_groups(user_entry.pw_name),
            }
            users.append(user_info)

        return json.dumps(users, indent=2)
    except Exception as e:
        raise RuntimeError(f"Failed to export users: {str(e)}")


def get_passwd_entry(username: str) -> Dict[str, Any]:
    """
    Get user info from /etc/passwd.

    Args:
        username: The username to look up

    Returns:
        Dictionary with user information from passwd file
    """
    try:
        result = subprocess.run(
            ["grep", f"^{username}:", "/etc/passwd"],
            check=False,
            stdout=subprocess.PIPE,
            text=True,
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(":")
            return {
                "username": parts[0],
                "uid": int(parts[2]),
                "gid": int(parts[3]),
                "gecos": parts[4],
                "home": parts[5],
                "shell": parts[6],
            }
    except Exception:
        pass
    return {}


def get_user_groups(username: str) -> list:
    """
    Get all groups the user belongs to.

    Args:
        username: The username to check group membership for

    Returns:
        List of group names
    """
    try:
        result = subprocess.run(
            ["groups", username], check=False, stdout=subprocess.PIPE, text=True
        )
        if result.returncode == 0:
            # Output format: "username : group1 group2 group3"
            return result.stdout.split(":", 1)[1].strip().split()

        # Alternative method using Python's grp module
        groups = []
        for group in grp.getgrall():
            if username in group.gr_mem:
                groups.append(group.gr_name)

        try:
            pw_entry = pwd.getpwnam(username)
            primary_group = grp.getgrgid(pw_entry.pw_gid).gr_name
            if primary_group not in groups:
                groups.append(primary_group)
        except KeyError:
            pass

        return groups
    except Exception:
        pass
    return []


def get_requested_properties(user) -> list:
    """
    Get a list of properties that have non-None and non-empty values from a user object.

    Args:
        user: User object to inspect

    Returns:
        List of property names that have values
    """
    requested_properties = []

    for attr in dir(user):
        if not attr.startswith("_") and not callable(getattr(user, attr)):
            user_value = getattr(user, attr)
            if user_value is not None and user_value != "":
                requested_properties.append((attr, user_value))
    return requested_properties


def run_command(
    cmd: list,
    input_str: bytes = None,
    check: bool = True,
    prevent_input: bool = False,
    command_name: str = None,
    username: str = None,
    universal_newlines: bool = True,
) -> subprocess.CompletedProcess:
    """
    Run a system command with consistent error handling and logging.

    Args:
        cmd: Command and arguments as a list
        input_str: Optional input to send to process stdin
        check: Whether to check return code and raise exception
        prevent_input: Whether to redirect stdin from /dev/null
        command_name: Name of command for logging
        username: Username for logging
        universal_newlines: Convert output to strings

    Returns:
        CompletedProcess instance with return code, stdout, stderr

    Raises:
        RuntimeError: If command fails and check is True
    """

    try:
        kwargs = {
            "check": check,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "universal_newlines": universal_newlines,
        }

        # If input provided, pass it to process
        if input_str:
            kwargs["input"] = input_str

        # If preventing input, redirect stdin from /dev/null
        if prevent_input:
            with open(os.devnull, "r") as DEVNULL:
                kwargs["stdin"] = DEVNULL
                return subprocess.run(cmd, **kwargs)
        else:
            return subprocess.run(cmd, **kwargs)

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if universal_newlines else e.stderr.decode("utf-8")
        if command_name:
            Logger.error(
                f"{command_name} failed",
                "user_management",
                command=cmd[0],
                error=error_msg,
                username=username,
            )
        if check:
            raise RuntimeError(f"Command failed: {error_msg}")
        return e
    except Exception as e:
        if command_name:
            Logger.error(
                f"{command_name} failed unexpectedly",
                "user_management",
                command=cmd[0],
                error=str(e),
                username=username,
            )
        if check:
            raise RuntimeError(f"Command execution error: {str(e)}")
        return None
