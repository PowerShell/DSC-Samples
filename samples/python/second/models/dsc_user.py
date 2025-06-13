import json
from typing import  Dict, Any
from utils.utils import check_user_exist, create_user, update_user, get_passwd_entry, get_user_groups
import sys

def dsc_resource(cls):
    """
    Decorator that marks a class as a DSC (Desired State Configuration) resource.
    This allows the class to be used in configuration management.
    """
    cls._is_dsc_resource = True
    
    # Add methods needed for DSC if they don't exist
    if not hasattr(cls, 'test'):
        cls.test = lambda self: self._exist
        
    if not hasattr(cls, 'get'):
        cls.get = lambda self: self.__dict__
    
    return cls

@dsc_resource
class User:
    """Linux User resource that can be managed via DSC."""
    def __init__(self):
        """Initialize User with default values."""
        self.username = ""
        self.password = ""
        self.uid = None 
        self.gid = None
        self.home = ""
        self.shell = ""
        self.groups = None
        self._exist = False

    
    def get_current_state(self, requested_properties=None):
        """
        Check if the user exists and return only the requested properties.
        
        Args:
            requested_properties: List of property names that were explicitly requested
                                If None, returns all available properties
        
        Returns:
            Dict containing the requested user properties
        """
        result = {}
        
        try:
            user = check_user_exist(self.username)

            if user is not None:
                self._exist = True
                result["exist"] = True

                if user:
                    passwd_entry = get_passwd_entry(self.username)
                    user_groups = get_user_groups(self.username)
                    
                    self.uid = user.get('uid', 0)
                    self.gid = user.get('gid', 0)
                    self.groups = user_groups
                    self.home = passwd_entry.get('home', '') if passwd_entry else ''
                    self.shell = passwd_entry.get('shell', '/bin/bash') if passwd_entry else '/bin/bash'
                    
                    if requested_properties:
                        for prop_name, expected_value in requested_properties:
                            if prop_name in ['username', '_exist']:
                                continue
                            current_value = getattr(self, prop_name)
                            if expected_value != current_value:
                                self._exist = False
                                break
                    
                    if requested_properties:
                        for prop_name, _ in requested_properties:
                            if hasattr(self, prop_name):
                                result[prop_name] = getattr(self, prop_name)
                    else:
                        result.update({
                            "uid": self.uid,
                            "gid": self.gid,
                            "groups": self.groups,
                            "home": self.home,
                            "shell": self.shell
                        })
            
            if not self._exist:
                print(json.dumps({
                    "username": self.username,
                    "exist": False,
                }))
            else:
                print(self.to_json(self))
            
        except Exception as e:
            print(f"Error occurred while getting current state for user '{self.username}': {e}")
            sys.exit(1)

    def modify(self, what_if: bool = False) -> None:
        exists = check_user_exist(self.username)
        if what_if:
            if exists:
                print(f"Would update user '{self.username}'")
            else:
                print(f"Would create user '{self.username}'")
            return
        
        if exists:
            update_user(
                username=self.username,
                uid=self.uid,
                gid=self.gid,
                home=self.home,
                shell=self.shell
            )
        else:
            create_user(
                username=self.username,
                uid=self.uid,
                gid=self.gid,
                home=self.home,
                shell=self.shell
            )
    
    @classmethod
    def to_dict(cls, item: 'User') -> Dict[str, Any]:
        """Convert User to dictionary for serialization."""
        result = {
            "username": item.username,
            "uid": item.uid,
            "gid": item.gid,
            "home": item.home,
            "shell": item.shell,
            "groups": item.groups,
            "exist": item._exist
        }

        return result

    @classmethod
    def to_json(cls, user: 'User') -> str:
        return json.dumps(cls.to_dict(user), separators=(',', ':'))

    @classmethod
    def from_json(cls, json_str: str) -> 'User':
        """Create a User object from JSON string."""
        data = json.loads(json_str)
        user = cls()
        user.username = data.get('username', '')
        user.password = data.get('password', '')
        user.uid = data.get('uid')
        user.gid = data.get('gid')
        user.home = data.get('home')
        user.shell = data.get('shell', '/bin/bash')
        user.groups = data.get('groups', [])
        user._exist = data.get('exists', False)
        return user