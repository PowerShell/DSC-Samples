---
title:  Step 3 - See how input is handled
weight: 3
dscs:
  menu_title: 3. Handle input
---

A command-based DSC Resource receives the instance it should operate on as a JSON blob.
The DSC engine sends it over stdin or as the value of a command-line argument, depending
on what the resource's manifest declares. The resource must parse that JSON, validate it,
report failures on stderr, and exit with a meaningful code.

With dsc-go-rdk, all of that plumbing already exists. This step shows what the library does for
you and adds the one piece of validation that's yours to write.

## What the library already does

The generated CLI accepts input two ways, and the generated manifest advertises both:

```sh
go run . get --input '{ "scope": "machine" }'
echo '{ "scope": "machine" }' | go run . get
```

Try the failure paths. Without any input:

```sh
go run . get
```

```json
{"error":"no input provided: use --input or pipe JSON to stdin"}
```

The message is a JSON object on stderr (the structured trace format the DSC engine
ingests and re-surfaces), and the process exits with code `4`, DSC's convention for
invalid input. Malformed JSON behaves the same way:

```sh
go run . get --input '{ not json'
```

```json
{"error":"input is not valid JSON"}
```

Valid JSON that doesn't match the `Settings` struct (for example, `"updateFrequency":
"weekly"`) exits with code `3`, the JSON deserialization error code. You'll see the full
exit code table in the generated manifest in step 6.

## Add semantic validation

Schema validation catches structural problems, but only when the resource is invoked
through DSC. Someone running `gotstoy` directly bypasses the schema. The resource is
responsible for its own semantic validation.

The one rule get needs: `scope` must be present and valid. Add this to `settings.go`:

```go
import dsc "github.com/LibreDsc/dsc-go-rdk"

// validateScope checks the required scope property. Validation failures map
// to DSC's invalid-input exit code (4).
func validateScope(scope string) error {
    switch scope {
    case "machine", "user":
        return nil
    case "":
        return dsc.NewExitCodeErrorf(dsc.ExitInvalidInput,
            "the scope property is required; must be one of: machine, user")
    default:
        return dsc.NewExitCodeErrorf(dsc.ExitInvalidInput,
            "invalid scope '%s'; must be one of: machine, user", scope)
    }
}
```

`dsc.NewExitCodeErrorf` attaches an exit code to the error. When a handler returns it, the
library logs the message to stderr in the trace format and exits with that code. You
never call `os.Exit` or print errors yourself.

Wire it into the stub `Get` in `main.go`:

```go
func (Handler) Get(_ context.Context, in Settings) (Settings, error) {
    if err := validateScope(in.Scope); err != nil {
        return in, err
    }
    return in, nil
}
```

Verify the validation:

```sh
go run . get --input '{ "scope": "cluster" }'
```

```json
{"error":"invalid scope 'cluster'; must be one of: machine, user"}
```

```sh
echo $? # $LASTEXITCODE in PowerShell
```

```text
4
```

If you want diagnostic logging as you develop, `dsc.Logger` writes leveled JSON trace
lines to stderr (for example `dsc.Logger.Debugf("checking %s", path)`), honoring the
`DSC_TRACE_LEVEL` environment variable the engine sets. Stdout stays reserved for
protocol output.

With input handling covered, you can implement the real get operation.
