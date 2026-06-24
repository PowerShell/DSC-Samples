# Write your first DSC Resource in C#

This folder contains a working DSC Resource written in C# for the tstoy application. Throughout this repo you may see C# referred to as csharp.  

## Building the sample

Before building the sample you will need to ensure you have the .net 8 SDK installed on your system. You may find out more about this on the Overview of [Install .NET on Windows, Linux, and macOS](https://learn.microsoft.com/en-us/dotnet/core/install/).  

Once you have .net 8 installed you may build the sample code in the following way:

- On Linux or macOS:

  ```sh
  dotnet restore
  dotnet publish --self-contained -o .
  export PATH=$(pwd):PATH
  ```

- On Windows:

  ```powershell
  dotnet restore
  dotnet publish --self-contained -o .
  $env:Path = $PWD.Path + ';' + $env:Path
  ```

## Getting current state

You can retrieve the current state of the resource with the `get` command.

```sh
# Get current state with flags
csharptstoy get --scope machine --ensure present --updateAutomatically=false
```

```json
{"ensure":"present","scope":"machine"}
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
' | csharptstoy get
```

```json
{"ensure":"absent","scope":"user"}
```

```sh
# Get current state of all scopes:
csharptstoy get --all
```

```json
{"ensure":"absent","scope":"machine"}
{"ensure":"absent","scope":"user"}
```

## Setting desired state

You can enforce the state of the resource with the `set` command.

```sh
# Set the state with flags
csharptstoy set --scope machine --ensure present --updateAutomatically=false
# Set with JSON over stdin
'
{
    "scope": "user",
    "ensure": "present",
    "updateAutomatically": true,
    "updateFrequency": 45
}
' | csharptstoy set
# Get new state of all scopes:
csharptstoy get --all
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

You can list `csharptstoy` as a DSC Resource to inspect it:

```pwsh
dsc resource list TSToy.Example/csharptstoy -f yaml
```

```yaml
type: TSToy.Example/csharptstoy
kind: Resource
version: 0.1.0
capabilities:
- Get
- Set
- Export
path: C:\Users\User\.local\bin\csharptstoy.dsc.resource.json
description: A DSC Resource written in C# to manage TSToy.
directory: C:\Users\User\.local\bin
implementedAs: null
author: null
properties: []
requireAdapter: null
manifest:
  $schema: https://raw.githubusercontent.com/PowerShell/DSC/main/schemas/2023/10/resource/manifest.json
  type: TSToy.Example/csharptstoy
  version: 0.1.0
  description: A DSC Resource written in C# to manage TSToy.
  tags: null
  get:
    executable: csharptstoy
    args:
    - get
    input: stdin
  set:
    executable: csharptstoy
    args:
    - set
    input: stdin
    return: state
  export:
    executable: csharptstoy
    args:
    - get
    - --all
  schema:
    embedded:
      $schema: https://json-schema.org/draft/2020-12/schema
      title: C# TSToy Resource
      type: object
      required:
      - scope
      properties:
        scope:
          title: Target configuration scope
          description: Defines which of TSToy's config files to manage.
          type: string
          enum:
          - machine
          - user
        ensure:
          title: Ensure configuration file existence
          description: Defines whether the config file should exist.
          type: string
          enum:
          - present
          - absent
          default: present
        updateAutomatically:
          title: Should update automatically
          description: Indicates whether TSToy should check for updates when it starts.
          type: boolean
        updateFrequency:
          title: Update check frequency
          description: Indicates how many days TSToy should wait before checking for updates.
          type: integer
          minimum: 1
          maximum: 90
```

You can retrieve the current state of the resource:

```powershell
$ResourceName = 'TSToy.Example/csharptstoy'
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
$schema: https://raw.githubusercontent.com/PowerShell/DSC/main/schemas/2023/10/config/document.json
resources:
- name: All Users Configuration
  type: TSToy.Example/csharptstoy
  properties:
    scope:  machine
    ensure: present
    updateAutomatically: false
- name: Current User Configuration
  type: TSToy.Example/csharptstoy
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
  type: TSToy.Example/csharptstoy
  result:
    actual_state:
      ensure: present
      scope: machine
      updateAutomatically: false
- name: Current User Configuration
  type: TSToy.Example/csharptstoy
  result:
    actual_state:
      ensure: present
      scope: user
      updateAutomatically: true
      updateFrequency: 45
messages: []
hadErrors: false
```
