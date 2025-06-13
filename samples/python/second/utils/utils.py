import sys
import json
import subprocess
import grp
import pwd
import os
from schema.schema import validate_user_data
from typing import Dict, Any, Optional


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

    if password:
        cmd.extend(["--password", password])

    cmd.append(username)

    try:
        with open(os.devnull, "w") as DEVNULL:
            process = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=DEVNULL,  # Redirect stdin from /dev/null to prevent hangs
                universal_newlines=True,
            )

            if process.returncode != 0:
                raise RuntimeError(f"Failed to create user: {process.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create user: {e.stderr}")


def update_user(
    username: str,
    password: Optional[str] = None,
    uid: Optional[int] = None,
    gid: Optional[int] = None,
    home: Optional[str] = None,
    shell: Optional[str] = None,
) -> None:
    # TODO: Fix
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
        cmd.extend(["-p", password])

    cmd.append(username)

    try:
        print(f"Updating user with command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to update user: {e.stderr.decode('utf-8')}")


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
