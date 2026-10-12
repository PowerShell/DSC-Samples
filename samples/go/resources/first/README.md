# Write your first DSC Resource in Go sample code

This folder contains the sample code for the completed _Write your first DSC Resource_
tutorial in Go, as well as the tutorial's documentation files. The resource is built with
[dsc-go-rdk](https://github.com/LibreDsc/dsc-go-rdk), a Go library that implements the Microsoft DSC
command-based resource protocol: CLI dispatch, JSON input handling, output framing,
schema generation, and manifest generation. As a result, the sample only implements the
`get` and `set` logic for the TSToy application.

## Building the sample

Navigate to this folder, then run:

- On Linux or macOS:

  ```sh
  go build -o gotstoy .
  export PATH=$(pwd):$PATH
  ```

- On Windows:

  ```powershell
  go build -o gotstoy.exe .
  $env:Path = $PWD.Path + ';' + $env:Path
  ```

The resource shells out to the `tstoy` application, so `tstoy` must also be on your `PATH`
(build it from the repository's `tstoy` folder).

## Getting current state

Pass the instance as JSON with `--input` or over stdin.

```sh
gotstoy get --input '{"scope":"machine"}'
```

```json
{"scope":"machine","ensure":"absent"}
```

```sh
echo '{"scope":"user"}' | gotstoy get
```

```json
{"scope":"user","ensure":"absent"}
```

## Setting desired state

```sh
echo '{
  "scope": "user",
  "ensure": "present",
  "updateAutomatically": true,
  "updateFrequency": 45
}' | gotstoy set
```

```json
{"scope":"user","ensure":"present","updateAutomatically":true,"updateFrequency":45}
```

After you've enforced state, you can verify the changes with the `tstoy` application
itself:

```sh
tstoy show
```

## Inspecting the resource

```sh
gotstoy schema                # the generated instance JSON Schema
gotstoy manifest              # the generated DSC resource manifest
gotstoy manifest --out-dir .  # write resource manifest for discovery 
```

## Using `dsc resource`

With this folder on `PATH` (or `DSC_RESOURCE_PATH`) and the resource
manifest written next to the binary:

```powershell
$ResourceName = 'TSToy.Example/gotstoy'
$UserSettings = @'
{"scope":"user","ensure":"present","updateAutomatically":true,"updateFrequency":45}
'@

dsc resource list $ResourceName
dsc resource get  --resource $ResourceName --input '{"scope":"machine"}'
$UserSettings | dsc resource test --resource $ResourceName
$UserSettings | dsc resource set  --resource $ResourceName
```

The resource has no `test` method in its manifest, so DSC synthesizes the test operation
from `get` output automatically.

## Using `dsc config`

The included [gotstoy.dsc.config.yaml](gotstoy.dsc.config.yaml) defines an instance for
both configuration scopes:

```powershell
dsc config get  --file gotstoy.dsc.config.yaml
dsc config test --file gotstoy.dsc.config.yaml
dsc config set  --file gotstoy.dsc.config.yaml
```

See the tutorial in [docs](docs/_index.md) for the full step-by-step walkthrough.
