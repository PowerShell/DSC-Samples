---
title:  Step 2 - Define the configuration settings
weight: 2
dscs:
  menu_title: 2. Define the settings
---

TSToy stores its configuration in JSON files, one per scope. The resource manages whether
each file exists and TSToy's update behavior in it:

```json
{
  "updates": {
    "automatic": true,
    "checkFrequency": 30
  }
}
```

A DSC Resource describes that as a set of properties. With dsc-go-rdk, the properties are the
fields of your state struct — the struct is the single source of truth for the
resource's data shape, and the library generates the instance JSON Schema from it.

Create `settings.go` and define the full settings model. Then remove the temporary
`Settings` struct you added to `main.go` in step 1.

```go
package main

// Settings models one TSToy configuration file as DSC state. The struct is
// the resource's contract: dsc-go-rdk generates the instance JSON Schema from its
// fields and tags, and every operation receives and returns it.
type Settings struct {
    Scope               string `json:"scope" enum:"machine,user"`
    Ensure              string `json:"ensure,omitempty" enum:"present,absent"`
    UpdateAutomatically *bool  `json:"updateAutomatically,omitempty"`
    UpdateFrequency     int    `json:"updateFrequency,omitempty"`
}
```

The struct tags carry the schema information:

- `json:"scope"` without `omitempty` makes `scope` a **required** property — the
  resource can't do anything without knowing which file to manage. The other fields use
  `omitempty`, making them optional.
- `enum:"machine,user"` constrains the property to those values in the schema, so DSC
  rejects invalid values before your code ever runs.
- `UpdateAutomatically` is a `*bool` rather than `bool`. The pointer distinguishes _not
  specified_ (`nil`) from _explicitly false_ — a distinction you'll rely on when
  implementing set.

Three things can't be expressed as struct tags: the property descriptions (they'd make the
field lines unreadably long), the `updateFrequency` range (1–90 days), and the default
value for `ensure`. Add them through the schema options in `main.go`:

```go
    r := dsc.MustResource[Settings](Handler{}, dsc.ResourceConfig{
        Type:        "TSToy.Example/gotstoy",
        Version:     "0.1.0",
        Description: "A DSC Resource written in Go to manage TSToy.",
        Tags:        []string{"tstoy", "example", "go"},

        SchemaOptions: dsc.SchemaOptions{
            SchemaDescription: "Golang TSToy Resource",
            Descriptions: map[string]string{
                "scope":  "Defines which of TSToy's config files to manage.",
                "ensure": "Defines whether the config file should exist.",
                "updateAutomatically": "Indicates whether TSToy should check for" +
                    " updates when it starts.",
                "updateFrequency": "Indicates how many days TSToy should wait" +
                    " before checking for updates.",
            },
            // Constraints the struct tags can't express.
            Overrides: func(schema map[string]any) {
                props := schema["properties"].(map[string]any)
                props["ensure"].(map[string]any)["default"] = "present"
                frequency := props["updateFrequency"].(map[string]any)
                frequency["minimum"] = 1
                frequency["maximum"] = 90
            },
        },
    })
```

> For short descriptions you can also use a `description:"..."` struct tag directly on a field.
> The tag takes precedence over the `Descriptions` map when both are present.

Every dsc-go-rdk resource has a `schema` subcommand. Inspect what you've defined:

```sh
go run . schema
```

The command emits the schema as one compact line; pretty-printed, it looks like this:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "description": "Golang TSToy Resource",
  "type": "object",
  "additionalProperties": false,
  "required": ["scope"],
  "properties": {
    "scope": {
      "description": "Defines which of TSToy's config files to manage.",
      "enum": ["machine", "user"],
      "type": "string"
    },
    "ensure": {
      "default": "present",
      "description": "Defines whether the config file should exist.",
      "enum": ["present", "absent"],
      "type": "string"
    },
    "updateAutomatically": {
      "description": "Indicates whether TSToy should check for updates when it starts.",
      "type": "boolean"
    },
    "updateFrequency": {
      "description": "Indicates how many days TSToy should wait before checking for updates.",
      "minimum": 1,
      "maximum": 90,
      "type": "integer"
    }
  }
}
```

This is the same schema DSC uses to validate instances in configuration documents, and the
manifest you generate in step 6 embeds it automatically. Note that `additionalProperties`
is `false` by default: if a user typos a property name in their configuration, DSC rejects
it instead of silently ignoring it.
