---
title:     Write your first DSC Resource Specification
linktitle: Write a DSC Resource
weight: 10
# platen:
#   menu:
#     collapse_section: true
---

## Synopsis

Specification for the sample code used in the [Write your first DSC Resource][01] tutorials.

## Description

This tutorial series uses the following learning goals:

- Create a small `<implementation language>` application to use as a DSC Resource.
- Define the properties of the DSC Resource.
- Implement get and set commands for the DSC Resource.
- Write a manifest for the DSC Resource.
- Manually test the DSC Resource.

The tutorial walks a reader through creating a basic DSC Resource to manage the fictional
[TSToy][02] application to meet those learning goals.

## Sample code requirements

The sample code representing the end of the tutorial must:

1. Define properties to manage the machine and user scope configurations for the TSToy application.
1. When called outside of DSC, handle input from stdin and argument flags.
1. Implement the `get` method.
1. Implement the `set` method.
1. Not implement the `test` method.
1. Include a DSC Resource manifest.

### Property definitions

The completed sample code must define the following properties:

- `scope` as a required property for the target configuration scope. This property must be an enum
  that accepts the values `machine` and `user`.
- `ensure` as an optional property that defaults to `present`. This property should define whether
  the DSC Resource creates or deletes the configuration file for the target scope. This property
  must be an enum that accepts the values `present` and `absent`.
- `updateAutomatically` as an optional property that manages the configuration file's
  `updates.automatic` setting. This property must be a boolean type.
- `updateFrequency` as an optional property that manages the configuration file's
  `updates.frequency` setting. This property must be an integer that accepts a minimum value of 1
  and a maximum value of `90`.

The JSON serialization of an instance should always include the `scope` and `ensure` properties. It
should only include the `updateAutomatically` or `updateFrequency` property if those values are set
in the configuration. For example:

```json
// when the config is absent
{"ensure":"absent","scope":"machine"}
// When update.automatic is defined but update.frequency isn't
{"ensure":"present","scope":"machine","updateAutomatically":false}
// When all options are defined
{"ensure":"present","scope":"user","updateAutomatically":true,"updateFrequency":45}
```

### Input handling

The application must accept an instance of the DSC Resource as a JSON blob over stdin and as the
value of the `--inputJSON` parameter for the `get` and `set` commands.

The application must accept the following parameters for the `get` and `set` commands to define the
resource instance's properties:

- `--scope`
- `--ensure`
- `--updateAutomatically`
- `--updateFrequency`
- `--inputJSON`

The `get` method must also support the `--all` boolean flag for returning every instance of the
resource.

### Get method implementation

The application's `get` method must:

1. Raise an error when the input JSON doesn't include the `scope` property and neither the
   `--scope` nor `--all` parameters are specified.
1. Return an instance for the machine and user scope configurations when the `--all` parameter flag
   is specified.
1. If the input JSON includes the `scope` parameter and the `--scope` argument is specified, use
   the value of the `--scope` parameter.
1. Ignore any other arguments and properties in the input JSON.
1. Return an instance for the specified scope as a JSON blob on a single line without any
   whitespace.
1. Use the [tstoy show path][03] command to retrieve the path to the configuration file for the
   specified scope and error if the `tstoy` application isn't executable.

### Set method implementation

The application's `set` method must:

1. Raise an error when the input JSON doesn't include the `scope` property and the `--scope`
   parameter isn't specified.
1. Raise an error if any of the specified properties for the desired state are invalid.
1. Support three set operations:
   - Create the configuration file if it doesn't exist and should. When the file is created, it
     must include only the defined settings for the desired state.
   - Remove the configuration file if it does exist and shouldn't.
   - Update the configuration file if it does and should exist but the `update.automatic` or
     `update.frequency` settings are out of the desired state. When the resource updates the
     configuration file, it must not change the order or value of any unmanaged settings.
1. If the instance is in the desired state, the resource must not alter the configuration file in
   any way.
1. Return the actual state of the configuration file as an instance after the set operation as a
   JSON blob on a single line without any whitespace.
1. Use the [tstoy show path][03] command to retrieve the path to the configuration file for the
   specified scope and error if the `tstoy` application isn't executable.

### Manifest definition

The DSC Resource manifest use the following template, replacing the placeholder values as needed:

- `<language-prefix>` - the two-character language prefix for the tutorial implementation, like
  `py` for Python or `rs` for Rust.
- `<language>` - the language for the tutorial implementation, like `Python` or `Rust`.

```json
{
    "manifestVersion": "1.0",
    "type": "TSToy.Example/<language-prefix>tstoy",
    "version": "0.1.0",
    "description": "A DSC Resource written in <language> to manage TSToy.",
    "get": {
        "executable": "<language-prefix>tstoy",
        "args": ["get"],
        "input": "stdin"
    },
    "set": {
        "executable": "<language-prefix>tstoy",
        "args": ["set"],
        "input": "stdin",
        "preTest": false,
        "return": "state"
    },
    "schema": {
        "embedded": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "<language> TSToy Resource",
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

[01]: /DSC-Samples/tutorials/first-resource/
[02]: /DSC-Samples/tstoy/about/
[03]: /DSC-Samples/tstoy/cli/show-path/
