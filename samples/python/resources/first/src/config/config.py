import json
import click 
import sys

from dataclasses import dataclass, field
from typing import Literal, Optional, Dict, Any, Tuple, Set
from pathlib import Path
from config.manager import ConfigManager
from utils.logger import Logger
from schema.schema import validate_resource, RESOURCE_SCHEMA


@dataclass
class Settings:
    scope: Literal["user", "machine"]
    _exist: bool = True
    updateAutomatically: Optional[bool] = None
    updateFrequency: Optional[int] = None
    config_path: str = field(default="", init=False, repr=False)
    _provided_properties: Set[str] = field(default_factory=set, init=False, repr=False)
    
    def __post_init__(self):
        self.config_manager = ConfigManager()
        self.logger = Logger()

    @staticmethod
    def validate(input_json, scope, exist, updateAutomatically, updateFrequency, command_name="command", logger=None):
        if logger is None:
            logger = Logger()
        
        data = {}
        data = Settings._read_stdin(command_name)

        if data:
            try:
                data = json.loads(data)
                logger.info(f"Parsed JSON from stdin: {json.dumps(data)}", command_name)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON format from stdin: {e}", command_name)
                click.echo(f"Error: Invalid JSON format from stdin: {e}", err=True)
                sys.exit(1)
        if input_json and not data:  # Only if we don't already have data from stdin
            try:
                data = json.loads(input_json)
                logger.info(f"Parsed JSON from --input: {json.dumps(data)}", command_name)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON format from --input: {e}", command_name)
                click.echo(f"Error: Invalid JSON format from --input: {e}", err=True)
                sys.exit(1)

        if not data:
            data = {}

        final_scope = scope if scope is not None else data.get('scope')
        
        if not final_scope:
            logger.error("Input validation failed: Validation error: 'scope' is a required property", "Settings.validate")
            sys.exit(1)
            
        if final_scope not in ['user', 'machine']:
            logger.error(f"Input validation failed: Validation error: 'scope' must be either 'user' or 'machine', got '{final_scope}'", "Settings.validate")
            sys.exit(1)

        if scope is not None:
            data['scope'] = scope
            logger.info(f"Added scope from parameter: {scope}", command_name)
        
        if exist is not None:
            data['_exist'] = exist
            logger.info(f"Added _exist from parameter: {exist}", command_name)

        if updateAutomatically is not None:
            data['updateAutomatically'] = updateAutomatically
            logger.info(f"Added updateAutomatically from parameter: {updateAutomatically}", command_name)

        if updateFrequency is not None:
            data['updateFrequency'] = updateFrequency
            logger.info(f"Added updateFrequency from parameter: {updateFrequency}", command_name)
        if not data:
            click.echo("Error: No input provided. You must specify either --input or at least --scope.", err=True)
            click.echo("\nExamples:", err=True)
            click.echo(f"  python main.py {command_name} --scope user", err=True)
            click.echo(f"  python main.py {command_name} --scope user --updateAutomatically true", err=True)
            click.echo(f"  python main.py {command_name} --input '{{\"scope\": \"user\"}}'", err=True)
            click.echo(f"  echo '{{\"scope\": \"user\"}}' | python main.py {command_name}", err=True)
            click.echo(f"\nRun 'python main.py {command_name} --help' for full usage information.", err=True)
            sys.exit(1)
        
        logger.info(f"Validating input data against schema: {json.dumps(data)}", command_name)
        is_valid, validation_error = validate_resource(data)
        if not is_valid:
            logger.error(f"Schema validation failed: {validation_error}", command_name)
            click.echo(f"Error: {validation_error}", err=True)
            sys.exit(1)
        
        logger.info(f"Final validated input data: {json.dumps(data)}", command_name)
        return data 
    
    @staticmethod
    def get_current_state(settings_request: 'Settings', logger=None) -> Tuple[Optional['Settings'], Optional[Exception]]:
        if logger is None:
            logger = Logger()
            
        try:
            config_manager = ConfigManager()
            
            if settings_request.scope == "machine":
                config_path = config_manager.get_machine_config_path()
            elif settings_request.scope == "user":
                config_path = config_manager.get_user_config_path()
            else:
                return None, ValueError(f"invalid scope: {settings_request.scope}")
            
            config_path_str = str(config_path)
            
            if not Path(config_path_str).exists():
                logger.info(f"Config file doesn't exist: {config_path_str}", "Settings")
                result = Settings(scope=settings_request.scope, _exist=False)
                result.updateAutomatically = None
                result.updateFrequency = None
                return result, None
            
            config_data = config_manager.load_config_file(Path(config_path_str))
            if config_data is None or not config_data:
                logger.info(f"Config file loaded but empty: {config_path_str}", "Settings")
                return Settings(scope=settings_request.scope, _exist=True), None
            
            logger.info(f"Config loaded successfully: {json.dumps(config_data)}", "Settings")
            
            current_settings = Settings(scope=settings_request.scope, _exist=True)
            
            if 'updates' in config_data:
                updates = config_data['updates']
                if 'updateAutomatically' in updates:
                    current_settings.updateAutomatically = bool(updates['updateAutomatically'])

                if 'updateFrequency' in updates:
                    current_settings.updateFrequency = int(updates['updateFrequency'])

                logger.info(f"Loaded settings: updateAutomatically={current_settings.updateAutomatically}, "
                            f"updateFrequency={current_settings.updateFrequency}", "Settings")
            else:
                logger.info("No 'updates' section found in config file", "Settings")
            
            if Settings._has_properties_to_validate(settings_request):
                validated_settings = Settings._validate_settings(
                    settings_request, current_settings, logger
                )
                return validated_settings, None
            else:
                logger.info("No properties to validate, returning all", "Settings")
                return current_settings, None
        except Exception as e:
            logger.error(f"Error in enforce: {str(e)}", "Settings")
            return None, e
        
    @staticmethod
    def enforce(settings: 'Settings', logger=None) -> Tuple[Optional['Settings'], Optional[Exception]]:
        if logger is None:
            logger = Logger()
            
        try:
            config_path, err = settings.get_config_path()
            if err:
                return None, err

            settings.config_path = config_path
            
            config_path_obj = Path(config_path)
            
            if settings._exist is False:
                logger.info(f"Deleting configuration file: {config_path}", "enforce")
                
                if config_path_obj.exists():
                    try:
                        config_path_obj.unlink()
                        logger.info(f"Successfully deleted configuration file: {config_path}", "enforce")
                        return settings, None
                    except Exception as e:
                        return None, Exception(f"Failed to delete configuration file: {str(e)}")
                else:
                    logger.info(f"Configuration file already doesn't exist: {config_path}", "enforce")
                    return settings, None
                    
            settings = Settings._set_default_values(settings)
            
            config_map = Settings._create_config_map(settings)
            
            config_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                with open(config_path_obj, 'w') as f:
                    json.dump(config_map, f, indent=2)
                logger.info(f"Successfully wrote configuration to: {config_path}", "enforce")
                return settings, None
            except Exception as e:
                return None, Exception(f"Failed to write configuration file: {str(e)}")
                
        except Exception as e:
            return None, e
    
    @staticmethod
    def _read_stdin(command_name="command", logger=None):
        if logger is None:
            logger = Logger()

        if not sys.stdin.isatty():
            logger.info("Reading input from stdin", command_name)
            try:
                # Read the entire content from stdin
                stdin_data = sys.stdin.read().strip()
                if stdin_data:
                    logger.info(f"Read from stdin: {stdin_data}", command_name)
                    return stdin_data
                else:
                    logger.info("Stdin was empty", command_name)
                    return None
            except Exception as e:
                logger.error(f"Error reading from stdin: {str(e)}", command_name)
                return None
        return None

    @staticmethod
    def _set_default_values(settings: 'Settings', logger=None) -> 'Settings':

        if logger is None:
            logger = Logger()

        if settings.updateAutomatically is None:
            default = RESOURCE_SCHEMA["properties"]["updateAutomatically"].get("default")
            if default is not None:
                settings.updateAutomatically = default
        
        if settings.updateFrequency is None:
            default = RESOURCE_SCHEMA["properties"]["updateFrequency"].get("default")
            if default is not None:
                settings.updateFrequency = default     
        return settings
    
    @staticmethod
    def _create_config_map(settings: 'Settings') -> dict:
        config_map = {}
        
        updates = {}
        
        if settings.updateAutomatically is not None:
            updates["updateAutomatically"] = settings.updateAutomatically
            
        if settings.updateFrequency is not None:
            updates["updateFrequency"] = settings.updateFrequency
        
        if updates:
            config_map["updates"] = updates
            
        return config_map
    
    @staticmethod
    def _has_properties_to_validate(settings: 'Settings') -> bool:
        properties = set(settings._provided_properties)
        if 'scope' in properties:
            properties.remove('scope')
        if '_exist' in properties:
            properties.remove('_exist')
            
        has_properties = len(properties) > 0
        return has_properties

    @staticmethod
    def _validate_settings(request_settings: 'Settings', current_settings: 'Settings', 
                                logger: Logger) -> 'Settings':
        validated_settings = Settings(
            scope=request_settings.scope,
            _exist=True,  # Start with True, will be set to False if validation fails
            updateAutomatically=current_settings.updateAutomatically,
            updateFrequency=current_settings.updateFrequency
        )
        
        validation_failed = False
        
        if 'updateAutomatically' in request_settings._provided_properties:
            if current_settings.updateAutomatically is None:
                validation_failed = True
                logger.info(f"updateAutomatically not found in config (requested: {request_settings.updateAutomatically})", 
                        "Settings")
            elif current_settings.updateAutomatically != request_settings.updateAutomatically:
                validation_failed = True
                logger.info(f"updateAutomatically mismatch - requested: {request_settings.updateAutomatically}, " +
                        f"found: {current_settings.updateAutomatically}", "Settings")
            else:
                logger.info(f"updateAutomatically validation passed: {request_settings.updateAutomatically}", "Settings")
        
        if 'updateFrequency' in request_settings._provided_properties:
            if current_settings.updateFrequency is None:
                validation_failed = True
                logger.info(f"updateFrequency not found in config (requested: {request_settings.updateFrequency})", 
                        "Settings")
            elif current_settings.updateFrequency != request_settings.updateFrequency:
                validation_failed = True
                logger.info(f"updateFrequency mismatch - requested: {request_settings.updateFrequency}, " +
                        f"found: {current_settings.updateFrequency}", "Settings")
            else:
                logger.info(f"updateFrequency validation passed: {request_settings.updateFrequency}", "Settings")
        
        if validation_failed:
            validated_settings._exist = False
            logger.info("Validation failed, setting _exist to False", "Settings")
        else:
            logger.info("All validations passed, _exist remains True", "Settings")
        
        return validated_settings
    
    @classmethod
    def validate_input(cls, data: Dict[str, Any], logger: Logger) -> bool:
        is_valid, validation_error = validate_resource(data)
        if not is_valid:
            logger.error(f"Input validation failed: {validation_error}", "Settings")
            return False
        allowed_properties = list(RESOURCE_SCHEMA["properties"].keys())
        logger.info(f"Valid properties per schema: {allowed_properties}", "Settings")
        logger.info(f"Provided properties: {list(data.keys())}", "Settings")
        
        return True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        settings = cls(
            scope=data.get('scope'),
            _exist=data.get('_exist', True),  # Default to True if not specified
            updateAutomatically=data.get('updateAutomatically'),
            updateFrequency=data.get('updateFrequency')
        )
        
        settings._provided_properties = set(data.keys())
        return settings
    
    def get_config_path(self) -> Tuple[str, Optional[Exception]]:
        try:
            if not self.scope:
                return "", ValueError("scope is required")
            
            if self.scope == "machine":
                config_path = self.config_manager.get_machine_config_path()
            elif self.scope == "user":
                config_path = self.config_manager.get_user_config_path()
            else:
                return "", ValueError(f"invalid scope: {self.scope}")
            
            self.config_path = str(config_path)
            return self.config_path, None
            
        except Exception as e:
            return "", e
    
    def get_config_map(self) -> Tuple[Optional[Dict[str, Any]], Optional[Exception]]:
        try:
            config_path, err = self.get_config_path()
            if err:
                return None, err
            
            if not Path(config_path).exists():
                self.logger.info(f"Config file not found: {config_path}", "Settings")
                return {}, None  # Return empty map if file doesn't exist
            
            # Load configuration
            config_data = self.config_manager.load_config_file(Path(config_path))
            if config_data is None:
                self.logger.info(f"Config file loaded but empty: {config_path}", "Settings")
                return {}, None
            
            self.logger.info(f"Config loaded successfully: {json.dumps(config_data)}", "Settings")
            return config_data, None
            
        except Exception as e:
            return None, e
    
    def get_config_settings(self) -> Tuple[Optional['Settings'], Optional[Exception]]:
        try:
            config_map, err = self.get_config_map()
            if err:
                return None, err
            
            if not config_map:
                self.logger.info("No configuration found, returning with _exist=False", "Settings")
                return Settings(scope=self.scope, _exist=False), None
            
            settings = Settings(scope=self.scope, _exist=True)
            
            if 'updates' in config_map:
                updates = config_map['updates']
                
                if 'updateAutomatically' in updates:
                    settings.updateAutomatically = bool(updates['updateAutomatically'])

                if 'updateFrequency' in updates:
                    settings.updateFrequency = int(updates['updateFrequency'])

                self.logger.info(f"Loaded settings - updateAutomatically: {settings.updateAutomatically}, " +
                               f"updateFrequency: {settings.updateFrequency}", "Settings")
            else:
                self.logger.info("No 'updates' section found in config file", "Settings")
            
            return settings, None
            
        except Exception as e:
            self.logger.error(f"Error in get_config_settings: {str(e)}", "Settings")
            return None, e
    
    def to_json(self, exclude_private: bool = False, exclude_none: bool = True) -> str:
        data = {}
        data["_exist"] = self._exist
        
        if self.scope is not None:
            data["scope"] = self.scope
        
        if not exclude_none or self.updateAutomatically is not None:
            data["updateAutomatically"] = self.updateAutomatically
        
        if not exclude_none or self.updateFrequency is not None:
            data["updateFrequency"] = self.updateFrequency
        
        if exclude_none:
            data = {k: v for k, v in data.items() if v is not None or k == "_exist"}
        
        return json.dumps(data)
    
    def print_config(self) -> None:
        json_output = self.to_json(exclude_private=False, exclude_none=True)
        self.logger.info(f"Printing configuration: {json_output}", "Settings")
        print(json_output)
    