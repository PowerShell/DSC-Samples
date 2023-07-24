---
title:  Step 7 - Validate the DSC Resource with DSC
weight: 7
dscs:
  menu_title: 7. Validate the resource
---

The DSC Resource is now fully implemented.

## Build the resource

To use it with DSC, you need to compile it and ensure DSC can find it in the `PATH`.

``````tabs
````tab { name="Build on Windows" }
```powershell
go build -o gotstoy.exe .
$env:Path = $PWD.Path + ';' + $env:Path
```
````

````tab { name="Build on Linux or macOS" }
```sh
go build -o gotstoy .
export PATH=$(pwd):$PATH
```
````
``````

## List the resource with DSC { toc_text="List the resource" }

With the resource built and added to the PATH with its manifest, you can use it with DSC instead of
calling it directly.

First, verify that DSC recognizes the DSC Resource.

```sh
dsc resource list TSToy.Example/gotstoy
```

```yaml
type: TSToy.Example/gotstoy
version: ''
path: C:\code\dsc\gotstoy\gotstoy.dsc.resource.json
directory: C:\code\dsc\gotstoy
implementedAs: Command
author: null
properties: []
requires: null
manifest:
  manifestVersion: '1.0'
  type: TSToy.Example/gotstoy
  version: 0.1.0
  description: A DSC Resource written in go to manage TSToy.
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

## Manage state with `dsc resource`

Get the current state of the machine-scope configuration file.

```sh
'{ "scope": "machine" }' | dsc resource get --resource TSToy.Example/gotstoy
```

```yaml
actualState:
  ensure: present
  scope: machine
  updateAutomatically: false
```

Test whether the user-scope configuration file is absent.

```sh
'{
    "scope":  "machine",
    "ensure": "absent"
}' | dsc resource test --resource TSToy.Example/gotstoy
```

```yaml
expected_state:
  scope: machine
  ensure: absent
actualState:
  ensure: present
  scope: machine
  updateAutomatically: false
differingProperties:
- ensure
```

Remove the machine-scope configuration file.

```sh
'{
    "scope": "machine",
    "ensure": "absent"
}' | dsc resource set --resource TSToy.Example/gotstoy
```

```yaml
beforeState:
  ensure: present
  scope: machine
  updateAutomatically: false
afterState:
  ensure: absent
  scope: machine
changedProperties:
- ensure
```

## Manage state with `dsc config`

Save the following configuration file as `gotstoy.dsc.config.yaml`. It defines an instance for both
configuration scopes, disabling automatic updates in the machine scope and enabling it with a
30-day frequency in the user scope.

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
    updateFrequency: 30
```

Get the current state of the instances defined in the configuration:

```sh
cat gotstoy.dsc.config.yaml | dsc config get
```

```yaml
results:
- name: All Users Configuration
  type: TSToy.Example/gotstoy
  result:
    actualState:
      ensure: absent
      scope: machine
- name: Current User Configuration
  type: TSToy.Example/gotstoy
  result:
    actualState:
      ensure: present
      scope: user
      updateAutomatically: true
      updateFrequency: 45
messages: []
hadErrors: false
```

The command returns a result for each instance in the configuration, showing the instance's name,
resource type, and actual state. The resource didn't raise any errors or emit any messages.

Next, test whether the instances are in the desired state:

```sh
cat gotstoy.dsc.config.yaml | dsc config test
```

```yaml
results:
- name: All Users Configuration
  type: TSToy.Example/gotstoy
  result:
    desiredState:
      updateAutomatically: false
      scope: machine
      ensure: present
    actualState:
      ensure: absent
      scope: machine
    differingProperties:
    - updateAutomatically
    - ensure
- name: Current User Configuration
  type: TSToy.Example/gotstoy
  result:
    desiredState:
      ensure: present
      scope: user
      updateFrequency: 30
      updateAutomatically: true
    actualState:
      ensure: present
      scope: user
      updateAutomatically: true
      updateFrequency: 45
    differingProperties:
    - updateFrequency
messages: []
hadErrors: false
```

The results show that both resources are out of the desired state. The machine scope configuration
file doesn't exist, while the user scope configuration file has an incorrect value for the update
frequency.

Enforce the configuration with the `set` command.

```sh
cat gotstoy.dsc.config.yaml | dsc config set
```

```yaml
results:
- name: All Users Configuration
  type: TSToy.Example/gotstoy
  result:
    beforeState:
      ensure: absent
      scope: machine
    afterState:
      ensure: present
      scope: machine
      updateAutomatically: false
    changedProperties:
    - ensure
    - updateAutomatically
- name: Current User Configuration
  type: TSToy.Example/gotstoy
  result:
    beforeState:
      ensure: present
      scope: user
      updateAutomatically: true
      updateFrequency: 45
    afterState:
      ensure: present
      scope: user
      updateAutomatically: true
      updateFrequency: 30
    changedProperties:
    - updateFrequency
messages: []
hadErrors: false
```

The results show that the resource created the machine scope configuration file and set the
`updateAutomatically` property for it. The results also show that the resource changed the update
frequency for the user scope configuration file.

Together, these steps minimally confirm that the resource can be used with DSC. DSC is able to get,
test, and set resource instances individually and in configuration documents.
