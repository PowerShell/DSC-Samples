---
title:  Step 6 - Author the DSC Resource manifest
weight: 6
dscs:
  menu_title: 6. Author manifest
---

The DSC Resource is now fully implemented. The last required step to use it with DSC is to author a
resource manifest. Command-based DSC Resources must have a JSON file that follows the naming
convention `<resource_name>.dsc.resource.json`. That's the manifest file for the resource. It
informs DSC and other higher-order tools about how the DSC Resource is implemented.

Create a new file called `csharptstoy.dsc.resource.json` in the project folder and open it.

```sh
touch ./csharptstoy.dsc.resource.json
code ./csharptstoy.dsc.resource.json
```

Add basic metadata for the DSC Resource.

```json
{
    "manifestVersion": "1.0",
    "type": "TSToy.Example/csharptstoy",
    "version": "0.1.0",
    "description": "A DSC Resource written in go to manage TSToy."
}
```

To inform DSC about how to get the current state of an instance, add the `get` key to the manifest.

```json
{
    "manifestVersion": "1.0",
    "type": "TSToy.Example/csharptstoy",
    "version": "0.1.0",
    "description": "A DSC Resource written in go to manage TSToy.",
    "get": {
        "executable": "csharptstoy",
        "args": ["get"],
        "input": "stdin"
    }
}
```

The `executable` key indicates the name of the binary `dsc` should use. The `args` key indicates
that `dsc` should call `csharptstoy get` to get the current state. The `input` key indicates that `dsc`
should pass the settings to the DSC Resource as a JSON blob over `stdin`. Even though the DSC
Resource can use argument flags, setting this value to JSON makes the integration more robust and
maintainable.

Next, define the `set` key in the manifest to inform DSC how to enforce the desired state of an
instance.

```json
{
    "manifestVersion": "1.0",
    "type": "TSToy.Example/csharptstoy",
    "version": "0.1.0",
    "description": "A DSC Resource written in go to manage TSToy.",
    "get": {
        "executable": "csharptstoy",
        "args": ["get"],
        "input": "stdin"
    },
    "set": {
        "executable": "csharptstoy",
        "args": ["set"],
        "input": "stdin",
        "preTest": true,
        "return": "state"
    }
}
```

In this section of the manifest, the `preTest` option indicates that the DSC Resource validates the
instance state itself inside the set command. DSC won't test instances of the resource before
invoking the set operation.

This section also defines the `return` key as `state`, which indicates that the resource returns
the current state of the instance when the command finishes.

The last section of the manifest that needs to be defined is the `schema`.

## Define the resource schema

For this resource, add the JSON Schema representing valid settings in the `embedded` key. An
instance of the resource must meet these criteria:

1. The instance must be an object.
1. The instance must define the `scope` property.
1. The `scope` property must be a string and set to either `machine` or `user`.
1. If the `ensure` property is specified, must be a string and set to either `present` or `absent`.
   If `ensure` isn't specified, it should default to `present`.
1. If the `updateAutomatically` property is specified, it must be a boolean value.
1. If the `updateFrequency` property is specified, it must be an integer between `1` and `90`,
   inclusive.

```json
{
    "manifestVersion": "1.0",
    "type": "TSToy.Example/csharptstoy",
    "version": "0.1.0",
    "description": "A DSC Resource written in go to manage TSToy.",
    "get": {
        "executable": "csharptstoy",
        "args": ["get"],
        "input": "stdin"
    },
    "set": {
        "executable": "csharptstoy",
        "args": ["set"],
        "input": "stdin",
        "preTest": true,
        "return": "state"
    },
    "schema": {
        "embedded": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "Golang TSToy Resource",
            "type": "object",
            "required": [
                "scope"
            ],
            "properties": {
                "scope": {
                    "title": "Target configuration scope",
                    "description": "Defines which of TSToy's config files to manage.",
                    "type": "string",
                    "enum": [
                        "machine",
                        "user"
                    ]
                },
                "ensure": {
                    "title": "Ensure configuration file existence",
                    "description": "Defines whether the config file should exist.",
                    "type": "string",
                    "enum": [
                        "present",
                        "absent"
                    ],
                    "default": "present"
                },
                "updateAutomatically": {
                    "title": "Should update automatically",
                    "description": "Indicates whether TSToy should check for updates when it starts.",
                    "type": "boolean"
                },
                "updateFrequency": {
                    "title": "Update check frequency",
                    "description": "Indicates how many days TSToy should wait before checking for updates.",
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 90
                }
            }
        }
    }
}
```

When authoring a JSON Schema, always include the `title` and `description` keys for every property.
Authoring tools, like VS Code, use those keys to give users context.
