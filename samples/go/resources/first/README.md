# Write your first DSC Resource in Go sample code

This folder contains the sample code for the completed _Write your first DSC Resource_ tutorial
in Go, as well as the tutorial's documentation files.

## Building the sample

You can build the sample code with the included PowerShell build script, or running the commands
manually. The build script handles building the DSC Resource, adding it to the path, and
registering shell completions.

To manually build the sample for the current operating system, navigate to this folder. Then, run
the following commands:

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

## Getting current state

You can retrieve the current state of the resource with the `get` command.

```sh
# Get current state with flags
gotstoy get --scope machine --ensure present --updateAutomatically=false
```

```json
{"ensure":"absent","scope":"machine"}
```

```sh
# Get with JSON over stdin
'
{
    "scope": "user",
    "ensure": "present",
    "updateAutomatically": true,
    "updateFrequency": 45
}
' | gotstoy get
```

```json
{"ensure":"absent","scope":"user"}
```

```sh
# Get current state of all scopes:
gotstoy get --all
```

```json
{"ensure":"absent","scope":"machine"}
{"ensure":"absent","scope":"user"}
```

## Setting desired state

You can enforce the state of the resource with the `set` command.

```sh
# Set the state with flags
gotstoy set --scope machine --ensure present --updateAutomatically=false
# Set with JSON over stdin
'
{
    "scope": "user",
    "ensure": "present",
    "updateAutomatically": true,
    "updateFrequency": 45
}
' | gotstoy set
# Get new state of all scopes:
gotstoy get --all
```

```json
{"ensure":"present","scope":"machine","updateAutomatically":false}

{"ensure":"present","scope":"user","updateAutomatically":true,"updateFrequency":45}

{"ensure":"present","scope":"machine","updateAutomatically":false}
{"ensure":"present","scope":"user","updateAutomatically":true,"updateFrequency":45}
```

## Verifying state

After you've enforced state, you should verify the changes with the `tstoy` application itself:

```sh
tstoy show
```

```yaml
Default configuration: {
  "Updates": {
    "Automatic": false,
    "CheckFrequency": 90
  }
}
Machine configuration: {
  "updates": {
    "automatic": false
  }
}
User configuration: {
  "updates": {
    "automatic": true,
    "checkfrequency": 45
  }
}
Final configuration: {
  "updates": {
    "automatic": true,
    "checkfrequency": 45
  }
}
```

## Using `dsc resource`

You can list `gotstoy` as a DSC Resource to inspect it:

```pwsh
dsc resource list TSToy.Example/gotstoy
```

```yaml
type: TSToy.Example/gotstoy
version: ''
path: C:\dsc-samples\samples\go\resources\first\dist\gotstoy_windows_amd64_v1\gotstoy.dsc.resource.json
directory: C:\dsc-samples\samples\go\resources\first\dist\gotstoy_windows_amd64_v1
implementedAs: Command
author: null
properties: []
requires: null
manifest:
  manifestVersion: '1.0'
  type: TSToy.Example/gotstoy
  version: 0.1.0
  description: The go implementation of a DSC Resource for the fictional TSToy application.
  get:
    executable: gotstoy
    args:
    - get
    input: stdin
  set:
    executable: gotstoy
    args:
    - set
    input: stdin
    preTest: true
    return: state
  schema:
    embedded:
      $schema: https://json-schema.org/draft/2020-12/schema
      title: Golang TSToy Resource
      type: object
      required:
      - scope
      properties:
        ensure:
          title: Ensure configuration file existence
          description: Defines whether the application's configuration file for this scope should exist or not.
          type: string
          enum:
          - present
          - absent
          default: present
        scope:
          title: Target configuration scope
          description: Defines which of the application's configuration files the resource should manage.
          type: string
          enum:
          - machine
          - user
        updateAutomatically:
          title: Should update automatically
          description: Indicates whether the application should check for updates when it starts.
          type: boolean
        updateFrequency:
          title: Update check frequency
          description: Indicates how many days the application should wait before checking for updates.
          type: integer
          minimum: 1
          maximum: 90
```

You can retrieve the current state of the resource:

```powershell
$ResourceName = 'TSToy.Example/gotstoy'
$MachineSettings = '{ "scope": "machine", "ensure": "present", "updateAutomatically": false }'
$UserSettings = @'
{
    "scope": "user",
    "ensure": "present",
    "updateAutomatically": true,
    "updateFrequency": 45
}
'@
# Get current state with flags
dsc resource get --resource $ResourceName  --input $MachineSettings
# Get with JSON over stdin
$UserSettings | dsc resource get --resource $ResourceName
```

```yaml
actual_state:
  ensure: absent
  scope: machine
```

```yaml
actual_state:
  ensure: absent
  scope: user
```

You can test whether the resource is in the desired state:

```powershell
# Test current state with flags
dsc resource test --resource $ResourceName  --input $MachineSettings
# Test with JSON over stdin
$UserSettings | dsc resource test --resource $ResourceName
```

```yaml
expected_state:
  scope: machine
  ensure: present
  updateAutomatically: false
actual_state:
  ensure: absent
  scope: machine
diff_properties:
- ensure
- updateAutomatically
```

```yaml
expected_state:
  scope: user
  ensure: present
  updateAutomatically: true
  updateFrequency: 45
actual_state:
  ensure: absent
  scope: user
diff_properties:
- ensure
- updateAutomatically
- updateFrequency
```

You can enforce the desired state for the resource:

```powershell
# Set desired state with flags
dsc resource set --resource $ResourceName  --input $MachineSettings
# Set with JSON over stdin
$UserSettings | dsc resource set --resource $ResourceName
```

```yaml
before_state:
  ensure: absent
  scope: machine
after_state:
  ensure: present
  scope: machine
  updateAutomatically: false
changed_properties:
- ensure
- updateAutomatically
```

```yaml
before_state:
  ensure: absent
  scope: user
after_state:
  ensure: present
  scope: user
  updateAutomatically: true
  updateFrequency: 45
changed_properties:
- ensure
- updateAutomatically
- updateFrequency
```

And when you call it again, the output shows that the resource didn't change the settings:

```powershell
# Set desired state with flags
dsc resource set --resource $ResourceName  --input $MachineSettings
# Set with JSON over stdin
$UserSettings | dsc resource set --resource $ResourceName
```

```yaml
before_state:
  ensure: present
  scope: machine
  updateAutomatically: false
after_state:
  ensure: present
  scope: machine
  updateAutomatically: false
changed_properties: []
```

```yaml
before_state:
  ensure: present
  scope: user
  updateAutomatically: true
  updateFrequency: 45
after_state:
  ensure: present
  scope: user
  updateAutomatically: true
  updateFrequency: 45
changed_properties: []
```

Finally, you can call `get` and `test` again:

```powershell
# Set desired state with flags
dsc resource get --resource $ResourceName  --input $MachineSettings
# Set with JSON over stdin
$UserSettings | dsc resource test --resource $ResourceName
```

```yaml
actual_state:
  ensure: present
  scope: machine
  updateAutomatically: false
```

```yaml
expected_state:
  scope: user
  ensure: present
  updateAutomatically: true
  updateFrequency: 45
actual_state:
  ensure: present
  scope: user
  updateAutomatically: true
  updateFrequency: 45
diff_properties: []
```

## Using `dsc config`

Save this configuration to a file or variable. It sets the configuration files for the application
using the go implementation. To use a different implementation, replace the value for the `type`
key in the resource entries.

```yaml
$schema: https://schemas.microsoft.com/dsc/2023/03/configuration.schema.json
resources:
- name: All Users Configuration
  type: TSToy.Example/gotstoy
  properties:
    scope:  machine
    ensure: present
    updateAutomatically: false
- name: Current User Configuration
  type: TSToy.Example/gotstoy
  properties:
    scope:  user
    ensure: present
    updateAutomatically: true
    updateFrequency: 45
```

Get the current state of the resources with `dsc config get`:

```powershell
$config | dsc config get
```

```yaml
results:
- name: All Users Configuration
  type: TSToy.Example/gotstoy
  result:
    actual_state:
      ensure: present
      scope: machine
      updateAutomatically: false
- name: Current User Configuration
  type: TSToy.Example/gotstoy
  result:
    actual_state:
      ensure: present
      scope: user
      updateAutomatically: true
      updateFrequency: 45
messages: []
hadErrors: false
```
