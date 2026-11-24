---
title:  Step 7 - Validate the DSC Resource with DSC and PSDSC
weight: 7
dscs:
  menu_title: 7. Validate the resource
---

With the DSC Resource fully implemented, you can now test its behavior with PowerShell DSC and DSCv3.

## Validate with PowerShell DSC

PowerShell DSC Resources can be invoked directly with the `Invoke-DscResource` cmdlet from the
**PSDesiredStateConfiguration** module. This section describes a set of scenarios to test the
resource against.

Before testing each scenario, close your VS Code terminal and open a new one. Dot-source the
`Helpers.ps1` script. For each test scenario, create the `$DesiredState` hashtable containing the
shared parameters and call the methods in the following order:

1. `Get()`, to retrieve the initial state of the DSC Resource
1. `Test()`, to see whether the DSC Resource considers it to be in the desired state
1. `Set()`, to enforce the desired state
1. `Test()`, to see whether the DSC Resource considers it to be set correctly
1. `Get()`, to confirm the final state of the DSC Resource

### Scenario: Disable automatic updating in user scope { toc_md="Disable updates in user scope" }

In this scenario, the existing configuration in the user scope needs to be configured not to update
automatically. All other settings should be left untouched.

```powershell
. ./Helpers.ps1

$DesiredState = @{
    Name     = 'PSTailspinToys'
    Module   = 'DscSamples.TailspinToys'
    Property = @{
        ConfigurationScope  = 'User'
        UpdateAutomatically = $false
        Ensure              = 'Present'
    }
}

Get-Content -Path $UserPath

Invoke-DscResource @DesiredState -Method Get
Invoke-DscResource @DesiredState -Method Test
Invoke-DscResource @DesiredState -Method Set
Invoke-DscResource @DesiredState -Method Test
Invoke-DscResource @DesiredState -Method Get

Get-Content -Path $UserPath
```

```console
{
    "unmanaged_key": true,
    "updates": {
        "automatic": true,
        "checkFrequency": 30
    }
}

ConfigurationScope  Ensure UpdateAutomatically UpdateFrequency
------------------  ------ ------------------- ---------------
              User Present                True              30

InDesiredState
--------------
         False

RebootRequired
--------------
         False

InDesiredState
--------------
          True

ConfigurationScope  Ensure UpdateAutomatically UpdateFrequency
------------------  ------ ------------------- ---------------
              User Present               False              30

{
  "unmanaged_key": true,
  "updates": {
    "checkFrequency": 30,
    "automatic": false
  }
}
```

### Scenario: Enable automatic updating in the user scope { toc_md="Enable updates in user scope" }

In this scenario, the existing configuration in the user scope needs to be configured to update
automatically. All other settings should be left untouched.

```powershell
. ./Helpers.ps1

$DesiredState = @{
    Name     = 'PSTailspinToys'
    Module   = 'DscSamples.TailspinToys'
    Property = @{
        ConfigurationScope  = 'User'
        UpdateAutomatically = $true
        Ensure              = 'Present'
    }
}

Get-Content -Path $UserPath

Invoke-DscResource @DesiredState -Method Get
Invoke-DscResource @DesiredState -Method Test
Invoke-DscResource @DesiredState -Method Set
Invoke-DscResource @DesiredState -Method Test
Invoke-DscResource @DesiredState -Method Get

Get-Content -Path $UserPath
```

```console
{
  "unmanaged_key": true,
  "updates": {
    "checkFrequency": 30,
    "automatic": false
  }
}

ConfigurationScope  Ensure UpdateAutomatically UpdateFrequency
------------------  ------ ------------------- ---------------
              User Present               False              30

InDesiredState
--------------
         False

RebootRequired
--------------
         False

InDesiredState
--------------
          True

ConfigurationScope  Ensure UpdateAutomatically UpdateFrequency
------------------  ------ ------------------- ---------------
              User Present                True              30

{
  "unmanaged_key": true,
  "updates": {
    "checkFrequency": 30,
    "automatic": true
  }
}
```

### Scenario: Update daily in the user scope { toc_md="Update daily in user scope" }

In this scenario, the existing configuration in the user scope needs to be configured to update
automatically and daily. All other settings should be left untouched.

```powershell
. ./Helpers.ps1

$DesiredState = @{
    Name     = 'PSTailspinToys'
    Module   = 'DscSamples.TailspinToys'
    Property = @{
        ConfigurationScope  = 'User'
        UpdateAutomatically = $true
        UpdateFrequency     = 1
        Ensure              = 'Present'
    }
}

Get-Content -Path $UserPath

Invoke-DscResource @DesiredState -Method Get
Invoke-DscResource @DesiredState -Method Test
Invoke-DscResource @DesiredState -Method Set
Invoke-DscResource @DesiredState -Method Test
Invoke-DscResource @DesiredState -Method Get

Get-Content -Path $UserPath
```

```console
{
  "unmanaged_key": true,
  "updates": {
    "checkFrequency": 30,
    "automatic": true
  }
}

ConfigurationScope  Ensure UpdateAutomatically UpdateFrequency
------------------  ------ ------------------- ---------------
              User Present                True              30

InDesiredState
--------------
         False

RebootRequired
--------------
         False

InDesiredState
--------------
          True

ConfigurationScope  Ensure UpdateAutomatically UpdateFrequency
------------------  ------ ------------------- ---------------
              User Present                True               1

{
  "unmanaged_key": true,
  "updates": {
    "automatic": true,
    "checkFrequency": 1
  }
}
```

### Scenario: No user scope configuration { toc_md="No user scope configuration" }

In this scenario, the configuration file for TSToy in the user scope shouldn't exist. If it does,
the DSC Resource should delete the file.

```powershell
. ./Helpers.ps1

$DesiredState = @{
    Name     = 'PSTailspinToys'
    Module   = 'DscSamples.TailspinToys'
    Property = @{
        ConfigurationScope  = 'User'
        UpdateAutomatically = $true
        Ensure              = 'Absent'
    }
}

Get-Content -Path $UserPath

Invoke-DscResource @DesiredState -Method Get
Invoke-DscResource @DesiredState -Method Test
Invoke-DscResource @DesiredState -Method Set
Invoke-DscResource @DesiredState -Method Test
Invoke-DscResource @DesiredState -Method Get

Test-Path -Path $UserPath
```

```console
{
  "unmanaged_key": true,
  "updates": {
    "checkFrequency": 30,
    "automatic": true
  }
}

ConfigurationScope  Ensure UpdateAutomatically UpdateFrequency
------------------  ------ ------------------- ---------------
              User Present                True              30

InDesiredState
--------------
         False

RebootRequired
--------------
         False

InDesiredState
--------------
          True

ConfigurationScope Ensure UpdateAutomatically UpdateFrequency
------------------ ------ ------------------- ---------------
              User Absent               False               0

False
```

### Scenario: Update weekly in the machine scope { toc_md="Update weekly in machine scope" }

In this scenario, there's no defined configuration in the machine scope. The machine scope needs to
be configured to update automatically and daily. The DSC Resource should create the file and any
parent folders as required.

```powershell
. ./Helpers.ps1

$DesiredState = @{
    Name     = 'PSTailspinToys'
    Module   = 'DscSamples.TailspinToys'
    Property = @{
        ConfigurationScope  = 'Machine'
        UpdateAutomatically = $true
        Ensure              = 'Present'
    }
}

Test-Path -Path $MachinePath, (Split-Path -Path $MachinePath)

Invoke-DscResource @DesiredState -Method Get
Invoke-DscResource @DesiredState -Method Test
Invoke-DscResource @DesiredState -Method Set
Invoke-DscResource @DesiredState -Method Test
Invoke-DscResource @DesiredState -Method Get

Get-Content -Path $MachinePath
```

```console
False
False

ConfigurationScope Ensure UpdateAutomatically UpdateFrequency
------------------ ------ ------------------- ---------------
           Machine Absent               False               0

InDesiredState
--------------
         False

RebootRequired
--------------
         False

InDesiredState
--------------
          True

ConfigurationScope  Ensure UpdateAutomatically UpdateFrequency
------------------  ------ ------------------- ---------------
           Machine Present                True               0

{
  "updates": {
    "automatic": true
  }
}
```

## Validate with DSCv3

The `DSC/PowerShellGroup` resource provider enables invoking instances of PowerShell DSC Resources
and declaring them in DSC Configuration Documents.

### List the resource with `dsc resource list` { toc_md="List the resource" }

You can list the resource with the `dsc resource list` command. Specify the resource's module and
name as the argument, like `<ModuleName>/<ResourceName>`.

```powershell
dsc --format yaml resource list DscSamples.TailspinToys/PSTailspinToys
```

```yaml
type: DscSamples.TailspinToys/PSTailspinToys
version: 0.0.1
path: C:\code\dsc\DscSamples.TailspinToys\DscSamples.TailspinToys.psd1
description: null
directory: C:\code\dsc\DscSamples.TailspinToys
implementedAs: ClassBased
author: ''
properties:
- ConfigurationScope
- DependsOn
- Ensure
- PsDscRunAsCredential
- UpdateAutomatically
- UpdateFrequency
requires: DSC/PowerShellGroup
manifest: null
```

### Manage state with `dsc resource`

Once you've confirmed that DSCv3 can find the resource, you can invoke it directly.

Define a new desired state for the machine-scope configuration:

```powershell
$Desired = @{
    ConfigurationScope = 'Machine'
    Ensure             = 'Absent'
} | ConvertTo-Json
```

Get the current state of the machine-scope configuration file.

```powershell
$Desired | dsc resource get --resource DscSamples.TailspinToys/PSTailspinToys
```

```yaml
actualState:
  ConfigurationScope: 0
  Ensure: 1
  UpdateAutomatically: true
  UpdateFrequency: 0
  CachedCurrentState: null
  CachedData: null
  CachedApplicationInfo: null
  CachedConfigurationFilePath: null
```

Test whether the machine configuration is in the desired state:

```powershell
$Desired | dsc resource test --resource DscSamples.TailspinToys/PSTailspinToys
```

```yaml
desiredState:
  ConfigurationScope: Machine
  Ensure: Absent
  type: DscSamples.TailspinToys/PSTailspinToys
actualState:
  InDesiredState: false
inDesiredState: false
differingProperties:
- ConfigurationScope
- Ensure
- type
```

Enforce the desired state:

```powershell
$Desired | dsc resource set --resource DscSamples.TailspinToys/PSTailspinToys
```

```yaml
beforeState:
  ConfigurationScope: 0
  Ensure: 1
  UpdateAutomatically: true
  UpdateFrequency: 0
  CachedCurrentState: null
  CachedData: null
  CachedApplicationInfo: null
  CachedConfigurationFilePath: null
afterState:
  RebootRequired: false
changedProperties:
- RebootRequired
```

Because DSCv3's result output includes the before and after state for the resource, you don't need
to call `dsc resource get` again.

### Manage state with `dsc config`

Save the following configuration file as `PSTailspinToys.dsc.config.yaml`. It defines an instance
for both configuration scopes, disabling automatic updates in the machine scope and enabling it
with a 30-day frequency in the user scope.

```yaml
$schema: https://schemas.microsoft.com/dsc/2023/03/configuration.schema.json
resources:
- name: TSToy PowerShell resources
  type: DSC/PowerShellGroup
  properties:
    resources:
      - name: All Users Configuration
        type: DscSamples.TailspinToys/PSTailspinToys
        properties:
          ConfigurationScope:  Machine
          Ensure:              Present
          UpdateAutomatically: false
      - name: Current User Configuration
        type: DscSamples.TailspinToys/PSTailspinToys
        properties:
          ConfigurationScope:  User
          Ensure:              Present
          UpdateAutomatically: true
          UpdateFrequency:     30
```

Get the current state of the resource instances.

```powershell
Get-Content -Path ./PSTailspinToys.dsc.config.yaml | dsc config get
```

```yaml
results:
- name: TSToy PowerShell resources
  type: DSC/PowerShellGroup
  result:
    actualState:
    - ConfigurationScope: 0
      Ensure: 0
      UpdateAutomatically: false
      UpdateFrequency: 0
      CachedCurrentState: null
      CachedData: null
      CachedApplicationInfo: null
      CachedConfigurationFilePath: null
    - ConfigurationScope: 1
      Ensure: 0
      UpdateAutomatically: false
      UpdateFrequency: 0
      CachedCurrentState: null
      CachedData: null
      CachedApplicationInfo: null
      CachedConfigurationFilePath: null
messages: []
hadErrors: false
```

Test whether the instances are in the desired state.

```powershell
Get-Content -Path ./PSTailspinToys.dsc.config.yaml | dsc config test
```

```yaml
results:
- name: TSToy PowerShell resources
  type: DSC/PowerShellGroup
  result:
    desiredState:
      resources:
      - name: All Users Configuration
        type: DscSamples.TailspinToys/PSTailspinToys
        properties:
          ConfigurationScope: Machine
          Ensure: Present
          UpdateAutomatically: false
      - name: Current User Configuration
        type: DscSamples.TailspinToys/PSTailspinToys
        properties:
          ConfigurationScope: User
          Ensure: Present
          UpdateAutomatically: true
          UpdateFrequency: 30
    actualState:
    - InDesiredState: false
    - InDesiredState: false
    inDesiredState: false
    differingProperties:
    - resources
messages: []
hadErrors: false
```

Set the instances to the desired state.

```powershell
Get-Content -Path ./PSTailspinToys.dsc.config.yaml | dsc config set
```

```yaml
results:
- name: TSToy PowerShell resources
  type: DSC/PowerShellGroup
  result:
    beforeState:
    - ConfigurationScope: 0
      Ensure: 0
      UpdateAutomatically: false
      UpdateFrequency: 0
      CachedCurrentState: null
      CachedData: null
      CachedApplicationInfo: null
      CachedConfigurationFilePath: null
    - ConfigurationScope: 1
      Ensure: 0
      UpdateAutomatically: false
      UpdateFrequency: 0
      CachedCurrentState: null
      CachedData: null
      CachedApplicationInfo: null
      CachedConfigurationFilePath: null
    afterState:
    - RebootRequired: false
    - RebootRequired: false
    changedProperties: []
messages: []
hadErrors: false
```
