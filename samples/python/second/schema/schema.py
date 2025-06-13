import os
import json
import jsonschema
from typing import Dict, Any
from utils.logger import setup_logger

logger = setup_logger('utils.schema_validator')

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

# TODO: Add proper error message handling and create dsc.resource.json file
def get_schema() -> Dict[str, Any]:
    schema_path = os.path.join(os.path.dirname(__file__), '..', '.dsc.resource.json')
    
    if os.path.exists(schema_path):
        try:
            logger.info(f"Loading schema from {schema_path}")
            with open(schema_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load schema from file: {e}, falling back to default")
    else:
        logger.info("Schema file not found, using default schema")
    
    # Fall back to embedded schema
    return DEFAULT_USER_SCHEMA

def validate_user_data(data: Dict[str, Any]) -> None:
    schema = get_schema()
    
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"Schema validation failed: {e}")
        raise