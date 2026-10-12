---
title:  Step 6 - Generate the DSC Resource manifest
weight: 6
dscs:
  menu_title: 6. Generate the manifest
---

Command-based DSC Resources must have a manifest — a JSON file following the naming
convention `<resource_name>.dsc.resource.json` — that tells DSC and higher-order tools
how the resource is implemented: how to invoke each operation, what the instance schema
is, and what the exit codes mean.

When authoring a resource by hand, writing the manifest and keeping it synchronized with
the code is a meaningful chunk of the work. With dsc-go-rdk you don't write it at all: the
library generates the manifest from the `ResourceConfig` plus the capabilities your
handler actually implements, so the manifest can never drift from the code.

## Inspect the generated manifest

Every dsc-go-rdk resource has a `manifest` subcommand:

```sh
go run . manifest
```

The command prints the manifest as one JSON line. To write it as a pretty-printed file
with the conventional name, use `--out-dir`:

```sh
go build -o gotstoy .
./gotstoy manifest --out-dir .
```

This creates `tstoy.example.gotstoy.dsc.resource.json` — the resource type name,
lowercased, with `/` replaced by `.`:

```json
{
  "$schema": "https://aka.ms/dsc/schemas/v3/bundled/resource/manifest.json",
  "type": "TSToy.Example/gotstoy",
  "version": "0.1.0",
  "description": "A DSC Resource written in Go to manage TSToy.",
  "tags": ["tstoy", "example", "go"],
  "get": {
    "executable": "gotstoy",
    "args": ["get", { "jsonInputArg": "--input", "mandatory": true }]
  },
  "set": {
    "executable": "gotstoy",
    "args": ["set", { "jsonInputArg": "--input", "mandatory": true }],
    "implementsPretest": true,
    "return": "state"
  },
  "exitCodes": {
    "0": "Success",
    "1": "Error",
    "2": "Resource error",
    "3": "JSON serialization error",
    "4": "Invalid input",
    "5": "Schema validation error",
    "6": "Resource not found"
  },
  "schema": {
    "embedded": { "...": "the schema from step 2, embedded verbatim" }
  }
}
```

Walking through what the library derived and from where:

- The `$schema`, `type`, `version`, `description`, and `tags` come from your
  `ResourceConfig`.
- The `get` and `set` sections exist because your handler implements `Get` and `Set` —
  nothing else. If you later add an `Export` method, an `export` section appears
  automatically.
- `{ "jsonInputArg": "--input", "mandatory": true }` tells DSC to pass the instance JSON
  as the value of the `--input` argument — exactly the invocation you've been typing by
  hand since step 1.
- `implementsPretest` and `return: state` come from the `ImplementsPretest` and
  `SetReturn` settings you added in step 5.
- There's no `test` section: the handler doesn't implement a test operation, so DSC falls
  back to its _synthetic test_ — it runs get and compares the actual state against the
  desired state property by property. For this resource, that's exactly the right
  behavior, so there's nothing to write.
- The `exitCodes` table documents the codes you saw in step 3, letting DSC render friendly
  messages when the resource fails.
- `schema.embedded` is the full schema from step 2.

## Manifest discovery

DSC discovers resources by searching every folder in the `PATH` environment variable —
and, if defined, `DSC_RESOURCE_PATH` — for files matching `*.dsc.resource.json`. With
the manifest written next to the `gotstoy` binary and that folder in `PATH`, DSC can find
and invoke the resource.

You'll validate that integration in the next step.
