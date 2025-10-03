import os
import json
import sys
import jsonschema
from typing import Dict, Any
from utils.logger import dfl_logger as logger

# Default schema with username as required field
DEFAULT_USER_SCHEMA = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "password": {"type": ["string", "null"]},
        "uid": {"type": ["integer", "null"]},
        "gid": {"type": ["integer", "null"]},
        "home": {"type": ["string", "null"]},
        "shell": {"type": "string"},
        "groups": {
            "type": "array",
            "items": {"type": "string"},
            "readOnly": True
        }
    },
    "required": ["username"],
    "additionalProperties": False
}

def get_schema() -> Dict[str, Any]:
    schema_path = os.path.join(os.path.dirname(__file__), '..', '.dsc.resource.json')
    
    if os.path.exists(schema_path):
        try:
            with open(schema_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load schema from {schema_path}: {e}")
            sys.exit(1)
    
    return DEFAULT_USER_SCHEMA

def validate_user_data(data: Dict[str, Any]) -> None:
    schema = get_schema()
    
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"Schema validation failed: {e.message}")
        sys.exit(1)