---
title:  Step 1 - Create the DSC Resource
weight: 1
dscs:
  menu_title: 1. Create the resource
---

Create a new folder called `gotstoy` and open it in VS Code. This folder is the root
folder for the project.

```sh
mkdir ./gotstoy
code ./gotstoy
```

Open the integrated terminal in VS Code. In that terminal, initialize the folder as a Go module.

```sh
go mod init "github.com/<your_github_id>/gotstoy"
```

In this tutorial, you'll be creating the DSC Resource with [dsc-go-rdk][01]. dsc-go-rdk implements
the Microsoft DSC command-based resource protocol: argument parsing, JSON input from `--input`
or stdin, output framing, exit codes, schema generation, and manifest generation. The
only code you write is the logic that manages TSToy.

Add the library to your module:

```sh
go get github.com/LibreDsc/dsc-go-rdk@v0.1.0
```

> If you're working with a local clone of dsc-go-rdk instead of the published module, point your
> `go.mod` at it with a replace directive:
>
> ```text
> replace github.com/LibreDsc/dsc-go-rdk => ../path/to/dsc-go-rdk
> ```

Create `main.go` with a minimal resource: a state struct, a handler with a stub `Get`
method, and a `main` function that hands control to the library.

```go
package main

import (
    "context"

    dsc "github.com/LibreDsc/dsc-go-rdk"
)

// Settings models one TSToy configuration file as DSC state.
// You'll define the real properties in the next step.
type Settings struct {
    Scope string `json:"scope"`
}

// Handler implements the resource's operations.
type Handler struct{}

// Get is a stub for now: it echoes the input back.
func (Handler) Get(_ context.Context, in Settings) (Settings, error) {
    return in, nil
}

func main() {
    r := dsc.MustResource[Settings](Handler{}, dsc.ResourceConfig{
        Type:        "TSToy.Example/gotstoy",
        Version:     "0.1.0",
        Description: "A DSC Resource written in Go to manage TSToy.",
        Tags:        []string{"tstoy", "example", "go"},
    })
    r.Main("gotstoy")
}
```

A few things to notice:

- `dsc.MustResource[Settings]` binds your handler to its configuration and validates the
  configuration at startup. The resource type name must match DSC's
  `<owner>[.<group>][.<area>]/<name>` format and the version must be a semantic version.
- The handler declares what the resource can do by which interfaces it implements. Right
  now it only implements `Gettable[Settings]`, the one mandatory capability. As you add
  `Set` in a later step, the resource (and its generated manifest) gain that
  capability automatically.
- `r.Main("gotstoy")` runs the full protocol CLI. The string is the executable name that
  will be written into the generated manifest.

Verify that the new application runs and has the expected commands.

```sh
go run . --help
```

```text
gotstoy - Microsoft DSC command-based resource: A DSC Resource written in Go to manage TSToy.

Usage:
  gotstoy get|set|test|delete|export [--input <json>]
  gotstoy set --what-if [--input <json>]
  gotstoy schema
  gotstoy manifest [--resource <type>] [--out-dir <dir>]

Input is read from --input or piped stdin. Output follows the Microsoft DSC JSON protocol.
```

You already have a working protocol CLI. Try the stubbed get:

```sh
go run . get --input '{ "scope": "machine" }'
```

```json
{"scope":"machine"}
```

With the application scaffolded, you need to understand the application the DSC Resource
manages before you can implement the operations. By now, you should have read [About the
TSToy application][02].

[01]: https://github.com/LibreDsc/dsc-go-rdk
[02]: /tstoy/about
