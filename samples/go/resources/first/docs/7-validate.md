---
title:  Step 7 - Validate the DSC Resource with DSC
weight: 7
dscs:
  menu_title: 7. Validate the resource
---

The DSC Resource is now fully implemented.

## Build the resource

To use it with DSC, you need to compile it, generate its manifest, and ensure DSC can find
both in the `PATH`.

``````tabs
````tab { name="Build on Windows" }
```powershell
go build -o gotstoy.exe .
.\gotstoy.exe manifest --out-dir .
$env:Path = $PWD.Path + ';' + $env:Path
```
````

````tab { name="Build on Linux or macOS" }
```sh
go build -o gotstoy .
./gotstoy manifest --out-dir .
export PATH=$(pwd):$PATH
```
````
``````

## List the resource with DSC { toc_text="List the resource" }

With the resource built and its manifest next to it in the `PATH`, you can use it with DSC
instead of calling it directly.

First, verify that DSC recognizes the DSC Resource.

```sh
dsc resource list TSToy.Example/gotstoy
```

```yaml
type: TSToy.Example/gotstoy
kind: resource
version: 0.1.0
capabilities:
- get
- set
description: A DSC Resource written in Go to manage TSToy.
directory: C:\code\dsc\gotstoy
implementedAs: null
author: null
properties: []
requireAdapter: null
manifest: # the manifest you generated in step 6
```

Note the capabilities: `get` and `set`, exactly the methods your handler implements.

## Manage state with `dsc resource`

Get the current state of the machine-scope configuration file.

```sh
'{ "scope": "machine" }' | dsc resource get --resource TSToy.Example/gotstoy
```

```yaml
actualState:
  scope: machine
  ensure: absent
```

Test whether the machine-scope configuration file is present. Remember that the resource
itself has no test operation — DSC synthesizes it from get:

```sh
'{
    "scope":  "machine",
    "ensure": "present",
    "updateAutomatically": false
}' | dsc resource test --resource TSToy.Example/gotstoy
```

```yaml
desiredState:
  scope: machine
  ensure: present
  updateAutomatically: false
actualState:
  scope: machine
  ensure: absent
inDesiredState: false
differingProperties:
- ensure
- updateAutomatically
```

Enforce the desired state:

```sh
'{
    "scope":  "machine",
    "ensure": "present",
    "updateAutomatically": false
}' | dsc resource set --resource TSToy.Example/gotstoy
```

```yaml
beforeState:
  scope: machine
  ensure: absent
afterState:
  scope: machine
  ensure: present
  updateAutomatically: false
changedProperties:
- ensure
- updateAutomatically
```

## Manage state with `dsc config`

Save the following configuration file as `gotstoy.dsc.config.yaml`. It defines an instance
for both configuration scopes, disabling automatic updates in the machine scope and
enabling it with a 30-day frequency in the user scope.

```yaml
$schema: https://aka.ms/dsc/schemas/v3/bundled/config/document.json
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

Test whether the instances are in the desired state:

```sh
dsc config test --file gotstoy.dsc.config.yaml
```

```yaml
results:
- name: All Users Configuration
  type: TSToy.Example/gotstoy
  result:
    desiredState:
      scope: machine
      ensure: present
      updateAutomatically: false
    actualState:
      scope: machine
      ensure: present
      updateAutomatically: false
    inDesiredState: true
    differingProperties: []
- name: Current User Configuration
  type: TSToy.Example/gotstoy
  result:
    desiredState:
      scope: user
      ensure: present
      updateAutomatically: true
      updateFrequency: 30
    actualState:
      scope: user
      ensure: present
      updateAutomatically: true
      updateFrequency: 45
    inDesiredState: false
    differingProperties:
    - updateFrequency
messages: []
hadErrors: false
```

The machine scope is already in the desired state from the earlier `dsc resource set`; the
user scope has an incorrect update frequency. Enforce the configuration:

```sh
dsc config set --file gotstoy.dsc.config.yaml
```

```yaml
results:
- name: All Users Configuration
  type: TSToy.Example/gotstoy
  result:
    beforeState:
      scope: machine
      ensure: present
      updateAutomatically: false
    afterState:
      scope: machine
      ensure: present
      updateAutomatically: false
    changedProperties: []
- name: Current User Configuration
  type: TSToy.Example/gotstoy
  result:
    beforeState:
      scope: user
      ensure: present
      updateAutomatically: true
      updateFrequency: 45
    afterState:
      scope: user
      ensure: present
      updateAutomatically: true
      updateFrequency: 30
    changedProperties:
    - updateFrequency
messages: []
hadErrors: false
```

The results show that the resource corrected the update frequency for the user scope and
left the already-correct machine scope untouched.

Together, these steps minimally confirm that the resource can be used with DSC. DSC is
able to get, test, and set resource instances individually and in configuration documents.
