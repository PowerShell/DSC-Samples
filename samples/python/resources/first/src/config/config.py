from dataclasses import dataclass, field
from typing import Literal, Optional, Dict, Any, Tuple, Set
from pathlib import Path
from config.manager import ConfigManager
from utils.logger import Logger
from schema.schema import validate_resource, RESOURCE_SCHEMA
import json

@dataclass
class Settings:
    scope: Literal["user", "machine"]
    _exist: bool = True
    updateAutomatically: Optional[bool] = None
    updateFrequency: Optional[int] = None
    config_path: str = field(default="", init=False, repr=False)
    _provided_properties: Set[str] = field(default_factory=set, init=False, repr=False)
    
    def __post_init__(self):
        """Initialize dependencies after dataclass creation"""
        self.config_manager = ConfigManager()
        self.logger = Logger()
    
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
    
    def enforce(self) -> Tuple[Optional['Settings'], Optional[Exception]]:
        try:
            current_settings, err = self.get_config_settings()
            if err:
                return None, err
            
            if not current_settings:
                self.logger.info("Failed to get settings, returning with scope only", "Settings")
                return Settings(scope=self.scope, _exist=True), None
            
            if not Path(self.config_path).exists():
                self.logger.info("Config file doesn't exist, returning scope only with _exist=false", "Settings")
                result = Settings(scope=self.scope, _exist=False)
                result.updateAutomatically = None
                result.updateFrequency = None
                return result, None
            
            self.logger.info("Current settings from config file: " +
                           f"updateAutomatically={current_settings.updateAutomatically}, " +
                           f"updateFrequency={current_settings.updateFrequency}", "Settings")
            
            if self._has_properties_to_validate():
                validated_settings = self._validate_settings(current_settings)
                return validated_settings, None
            else:
                self.logger.info("No properties to validate, returning all: " + 
                               f"updateAutomatically={current_settings.updateAutomatically}, " +
                               f"updateFrequency={current_settings.updateFrequency}", "Settings")
                
                return current_settings, None
            
        except Exception as e:
            self.logger.error(f"Error in enforce: {str(e)}", "Settings")
            return None, e
    
    def _has_properties_to_validate(self) -> bool:
        properties = set(self._provided_properties)
        if 'scope' in properties:
            properties.remove('scope')
        if '_exist' in properties:
            properties.remove('_exist')
            
        has_properties = len(properties) > 0
        self.logger.info(f"Properties to validate: {properties}, has_properties: {has_properties}", "Settings")
        return has_properties
    
    def _validate_settings(self, current_settings: 'Settings') -> 'Settings':
        validated_settings = Settings(
            scope=self.scope,
            _exist=True,  # Start with True, will be set to False if validation fails
            updateAutomatically=current_settings.updateAutomatically,
            updateFrequency=current_settings.updateFrequency
        )
        
        validation_failed = False
        
        if 'updateAutomatically' in self._provided_properties:
            if current_settings.updateAutomatically is None:
                validation_failed = True
                self.logger.info(f"updateAutomatically not found in config (requested: {self.updateAutomatically})", "Settings")
            elif current_settings.updateAutomatically != self.updateAutomatically:
                validation_failed = True
                self.logger.info(f"updateAutomatically mismatch - requested: {self.updateAutomatically}, found: {current_settings.updateAutomatically}", "Settings")
            else:
                self.logger.info(f"updateAutomatically validation passed: {self.updateAutomatically}", "Settings")
        
        if 'updateFrequency' in self._provided_properties:
            if current_settings.updateFrequency is None:
                validation_failed = True
                self.logger.info(f"updateFrequency not found in config (requested: {self.updateFrequency})", "Settings")
            elif current_settings.updateFrequency != self.updateFrequency:
                validation_failed = True
                self.logger.info(f"updateFrequency mismatch - requested: {self.updateFrequency}, found: {current_settings.updateFrequency}", "Settings")
            else:
                self.logger.info(f"updateFrequency validation passed: {self.updateFrequency}", "Settings")
        
        if validation_failed:
            validated_settings._exist = False
            self.logger.info("Validation failed, setting _exist to False", "Settings")
        else:
            self.logger.info("All validations passed, _exist remains True", "Settings")
        
        return validated_settings
    
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
        
        self.logger.info(f"Serializing to JSON: {data}", "Settings")
        
        return json.dumps(data)
    
    def print_config(self) -> None:
        json_output = self.to_json(exclude_private=False, exclude_none=True)
        self.logger.info(f"Printing configuration: {json_output}", "Settings")
        print(json_output)
    
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
    
    def validate(self) -> bool:
        if not self.scope or self.scope not in ['user', 'machine']:
            return False
        return True