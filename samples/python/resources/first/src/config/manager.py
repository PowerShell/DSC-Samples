import os
import json
import pathlib
from typing import Dict, Any
from resources.strings import Strings
from utils.logger import Logger


class ConfigSource:
    """Represents a configuration source."""
    DEFAULT = "default"
    MACHINE = "machine"
    USER = "user"
    ENV = "environment"
    CLI = "cli"

class ConfigManager:
    def __init__(self):
        self.default_config = {
            "updates": {
                "updateAutomatically": False,
                "updateFrequency": 180
            }
        }
        self.machine_config = {}
        self.user_config = {}
        self.env_config = {}
        self.cli_config = {}
        self.config = {}
        
        # Track loaded sources for reporting
        self.loaded_sources = []

        self.logger = Logger()
        
    def get_machine_config_path(self) -> pathlib.Path:
        if os.name == 'nt':  # Windows
            return pathlib.Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData')) / 'tstoy' / 'config.json'
        else:  # Unix-like
            return pathlib.Path('/etc/tstoy/config.json')
            
    def get_user_config_path(self) -> pathlib.Path:
        if os.name == 'nt':  # Windows
            config_dir = pathlib.Path(os.environ.get('APPDATA')) 
        else:  # Unix-like
            config_dir = pathlib.Path.home() / '.config'
        
        return config_dir / 'tstoy' / 'config.json'
    
    def load_config_file(self, path: pathlib.Path) -> Dict[str, Any]:
        if not path.exists():
            self.logger.info(Strings.CONFIG_NOT_FOUND.format(path))
            return {}
            
        try:
            with open(path, 'r') as f:
                config = json.load(f)
                self.logger.info(Strings.CONFIG_LOADED.format(path))
                return config
        except json.JSONDecodeError as e:
            self.logger.error(Strings.CONFIG_INVALID.format(path, str(e)))
            return {}
        except IOError as e:
            self.logger.error(Strings.CONFIG_INVALID.format(path, str(e)))
            return {}
    
    def save_config_file(self, path: pathlib.Path, config: Dict[str, Any]) -> bool:
        try:
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w') as f:
                json.dump(config, f, indent=2)
                self.logger.info(Strings.CONFIG_UPDATED.format(path))
                return True
        except Exception as e:
            self.logger.error(Strings.ERROR_WRITE_CONFIG.format(path, str(e)))
            return False
    
    def load_default_config(self):
        self.config = self.default_config.copy()
        self.loaded_sources.append(ConfigSource.DEFAULT)
    
    def load_machine_config(self):
        path = self.get_machine_config_path()
        self.machine_config = self.load_config_file(path)
        if self.machine_config:
            self._merge_config(self.machine_config)
            self.loaded_sources.append(ConfigSource.MACHINE)
    
    def load_user_config(self):
        path = self.get_user_config_path()
        self.user_config = self.load_config_file(path)
        if self.user_config:
            self._merge_config(self.user_config)
            self.loaded_sources.append(ConfigSource.USER)
    
    def load_environment_config(self, prefix: str):
        env_config = {}
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Convert DSCPY_UPDATES_AUTOMATIC to updates.automatic
                config_key = key[len(prefix):].lower().replace('_', '.')
                
                # Convert string value to appropriate type
                if value.lower() in ('true', 'yes', '1'):
                    env_config[config_key] = True
                elif value.lower() in ('false', 'no', '0'):
                    env_config[config_key] = False
                elif value.isdigit():
                    env_config[config_key] = int(value)
                else:
                    env_config[config_key] = value
        
        if env_config:
            self.env_config = env_config
            self._merge_config(env_config)
            self.loaded_sources.append(ConfigSource.ENV)
  
    
    def _merge_config(self, source: Dict[str, Any]):
        def deep_merge(target, source):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    deep_merge(target[key], value)
                else:
                    target[key] = value
        
        deep_merge(self.config, source)
    
    def get_merged_config(self) -> Dict[str, Any]:
        return self.config
    
    def get_config_sources(self) -> list:
        return self.loaded_sources
        
    def get_all_config_files(self) -> list:
        try:
            user_config_dir = self.get_user_config_path().parent
            if user_config_dir.exists():
                # Return a list of all JSON files in the config directory
                return list(user_config_dir.glob('*.json'))
            else:
                self.logger.warning(f"Config directory does not exist: {user_config_dir}")
                return []
        except Exception as e:
            self.logger.error(f"Error enumerating config files: {str(e)}")
            return []
            
    def get_config_by_name(self, name: str) -> Dict[str, Any]:
        if name == 'default':
            return self.default_config.copy()
            
        # Try to find a specific config file with this name
        user_config_dir = self.get_user_config_path().parent
        config_path = user_config_dir / f"{name}.json"
        
        if config_path.exists():
            config = self.load_config_file(config_path)
            return config
        else:
            # If no specific file exists, return the merged config
            # This behavior can be changed based on requirements
            self.logger.warning(f"No configuration found for name: {name}")
            return self.get_merged_config()
    
    def load_all_configs(self, env_prefix: str = "TSTOY_"):
        self.load_default_config()
        self.load_machine_config()
        self.load_user_config()
        self.load_environment_config(env_prefix)
