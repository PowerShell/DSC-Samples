import jsonschema
import json

RESOURCE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Python TSToy Resource",
    "type": "object",
    "required": ["scope"],
    "additionalProperties": False,
    "properties": {
        "scope": {
            "title": "Target configuration scope",
            "description": "Defines which of TSToy's config files to manage.",
            "type": "string",
            "enum": ["machine", "user"],
        },
        "_exist": {
            "title": "Should configuration exist",
            "description": "Defines whether the config file should exist.",
            "type": "boolean",
            "default": True,
        },
        "updateAutomatically": {
            "title": "Should update automatically",
            "description": "Indicates whether TSToy should check for updates when it starts.",
            "type": "boolean",
        },
        "updateFrequency": {
            "title": "Update check frequency",
            "description": "Indicates how many days TSToy should wait before checking for updates.",
            "type": "integer",
            "minimum": 1,
            "maximum": 180,
        },
    }
}

def validate_resource(instance):
    """Validate resource instance against schema."""
    try:
        jsonschema.validate(instance=instance, schema=RESOURCE_SCHEMA)
        return True, None
    except jsonschema.exceptions.ValidationError as err:
        return False, f"Validation error: {err.message}"
 
def get_schema():
    """Dump the schema as formatted JSON string."""
    return json.dumps(RESOURCE_SCHEMA, separators=(',', ':'))