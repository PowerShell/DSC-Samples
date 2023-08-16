---
title:  Step 6 - Implement the Set method
weight: 6
dscs:
  menu_title: 6. Implement `Set()`
---

Now that the `Get()` and `Test()` methods reliably work, you can define the `Set()` method to
actually enforce the desired state.

In the minimal implementation, the `Set()` method does nothing.

```powershell
[void] Set() {}
```

## Minimally handle sub-operations

The `Set()` method needs to handle three different sub-operations:

- If the configuration file doesn't exist and should exist, the resource needs to _create_ it.
- If the configuration file exists and should exist, but has out-of-state properties, the resource
  needs to _update_ the file.
- If the configuration file exists and shouldn't exist, the resource needs to _remove_ it.

```powershell
[void] Set() {
    if ($this.Test()) {
            return
    }

    $CurrentState   = $this.CachedCurrentState
    $IsAbsent       = $CurrentState.Ensure -eq [TailspinEnsure]::Absent
    $ShouldBeAbsent = $this.Ensure         -eq [TailspinEnsure]::Absent

    if ($IsAbsent) {
        # Create
    } elseif ($ShouldBeAbsent) {
        # Remove
    } else {
        # Update
    }
}
```

`Set()` first calls the `Test()` method to determine if the resource actually needs to do anything.
Some tools, like DSCv3 and Azure Automanage's machine configuration feature, ensure that the
`Set()` method is only called after the `Test()` method. However, there's no such guarantee when
you use the `Invoke-DscResource` cmdlet directly.

Since the `Test()` method calls `Get()`, which caches the current state, the resource can access
the cached current state without having to call the `Get()` method again.

Next, the resource needs to distinguish between create, remove, and update behaviors for the
configuration file.

Create three new methods to handle these operations and call them in the `Set()` method as needed.
The return type for all three should be **void**.

```powershell
[void] Set() {
    if ($this.Test()) {
            return
    }

    $CurrentState   = $this.CachedCurrentState
    $IsAbsent       = $CurrentState.Ensure -eq [TailspinEnsure]::Absent
    $ShouldBeAbsent = $this.Ensure         -eq [TailspinEnsure]::Absent

    if ($IsAbsent) {
        $this.Create()
    } elseif ($ShouldBeAbsent) {
        $this.Remove()
    } else {
        $this.Update()
    }
}

[void] Create() {}
[void] Remove() {}
[void] Update() {}
```

## Handle Converting Properties to JSON { toc_md="`ToConfigurationJson()`" }

The resource needs to be able to handle representing the instance properties in the application's
actual JSON data model. It also needs to be able to update only the data the instance is enforcing.
It shouldn't ever alter unmanaged data except by deleting the file when `$Ensure` is `Absent`.

### Implement `ToConfigurationJson()` helper method { toc_md="Implement the helper method" }

Create a new method called `ToConfigurationJson()`. Its return type should be **string**. This
method converts the resource instance into the JSON that the configuration file expects. You can
start with the following minimal implementation:

```powershell
[string] ToConfigurationJson() {
    $config = @{}

    return ($config | ConvertTo-Json)
}
```

The minimal implementation returns an empty JSON object as a string. To make it useful, it needs to
return the actual JSON representation of the settings in TSToy's configuration file.

First, prepopulate the `$config` hashtable with the mandatory automatic updates setting by
adding the `updates` key with its value as a **hashtable**. The hashtable should have the
`automatic` key. Assign the value of the class's `$UpdateAutomatically` property to the `automatic`
key.

```powershell
[string] ToConfigurationJson() {
    $config = @{
        updates = @{
            automatic = $this.UpdateAutomatically
        }
    }

    return ($config | ConvertTo-Json)
}
```

This code translates the resource instance representation of TSToy's settings to the structure that
TSToy's configuration file expects.

Next, the method needs to check whether the class has cached the data from an existing
configuration file. The cached data allows the resource to manage the defined settings without
overwriting or removing unmanaged settings.

```powershell
[string] ToConfigurationJson() {
    $config = @{
        updates = @{
            automatic = $this.UpdateAutomatically
        }
    }

    if ($this.CachedData) {
        # Copy unmanaged settings without changing the cached values
        $this.CachedData |
            Get-Member -MemberType NoteProperty |
            Where-Object -Property Name -NE -Value 'updates' |
            ForEach-Object -Process {
                $setting = $_.Name
                $config.$setting = $this.CachedData.$setting
            }

        # Add the checkFrequency to the hashtable if it is set in the cache
        if ($frequency = $this.CachedData.updates.checkFrequency) {
            $config.updates.checkFrequency = $frequency
        }
    }

    # If the user specified an UpdateFrequency, use that value
    if ($this.UpdateFrequency -ne 0) {
        $config.updates.checkFrequency = $this.UpdateFrequency
    }

    return ($config | ConvertTo-Json -Depth 99)
}
```

If the class has cached the settings from an existing configuration, it:

1. Inspects the cached data's properties, looking for any properties the resource doesn't
   manage. If it finds any, the method inserts those unmanaged properties into the `$config`
   hashtable.

   Because the resource only manages the update settings, every setting except for `updates` is
   inserted.
1. Checks to see if the `checkFrequency` setting in `updates` is set. If it's set, the method
   inserts this value into the `$config` hashtable.

   This operation allows the resource to ignore the `$UpdateFrequency` property if the user
   doesn't specify it.

1. Finally, the method needs to check if the user specified the `$UpdateFrequency` property and
   insert it into the `$config` hashtable if they did.

With this code, the `ToConfigurationJson()` method:

1. Returns an accurate JSON representation of the desired state that the TSToy application expects
   in its configuration file
1. Respects any of TSToy's settings that the resource doesn't explicitly manage
1. Respects the existing value for TSToy's update frequency if the user didn't specify one,
   including leaving it undefined in the configuration file

### Validate `ToConfigurationJson()` { toc_md="Validate the method" }

To test this new method, close your VS Code terminal and open a new one. Execute the `using`
statement to load the **DscSamples.TailspinToys** module's classes and enums into your current
session and dot-source the `Helpers.ps1` script.

```powershell
using module ./DscSamples.TailspinToys.psd1
. ./Helpers.ps1
$Example = [PSTailspinToys]::new()
Get-Content -Path $(tstoy show path user)
$Example.ConfigurationScope = 'User'
$Example.ToConfigurationJson()
```

Before the `Get()` method is called, the only value in the output of the **ToJsonConfig** method is
the converted value for the `$UpdateAutomatically` property.

```console
{
    "unmanaged_key": true,
    "updates": {
        "automatic": true,
        "checkFrequency": 30
    }
}

{
  "updates": {
    "automatic": false
  }
}
```

After you call `Get()`, the output includes an unmanaged top-level key, `unmanaged_key`. It also
includes the existing setting in the configuration file for `$UpdateFrequency` since it wasn't
explicitly set on the resource instance.

```powershell
$Example.Get()
$Example.ToConfigurationJson()
```

```console
 Ensure ConfigurationScope UpdateAutomatically UpdateFrequency
 ------ ------------------ ------------------- ---------------
Present               User                True              30

{
  "unmanaged_key": true,
  "updates": {
    "checkFrequency": 30,
    "automatic": false
  }
}
```

After `$UpdateFrequency` is set, the output reflects the specified value.

```powershell
$Example.UpdateFrequency = 7
$Example.ToConfigurationJson()
```

```console
{
  "unmanaged_key": true,
  "updates": {
    "checkFrequency": 7,
    "automatic": false
  }
}
```

## Implement the `Create()` method { toc_md="Implement `Create()`" }

To implement the `Create()` method, we need to convert the user-specified properties for the DSC
Resource into the JSON that TSToy expects in its configuration file and write it to that file.

```powershell
[void] Create() {
    $ErrorActionPreference = 'Stop'

    $Json = $this.ToConfigurationJson()

    $FilePath   = $this.GetConfigurationFilePath()
    $FolderPath = Split-Path -Path $FilePath

    if (!(Test-Path -Path $FolderPath)) {
        New-Item -Path $FolderPath -ItemType Directory -Force
    }

    Set-Content -Path $FilePath -Value $Json -Encoding utf8 -Force
}
```

The method uses the `ToConfigurationJson()` method to get the JSON for the configuration file. It
checks whether the configuration file's folder exists and creates it if necessary. Finally, it
creates the configuration file and writes the JSON to it.

## Implement the `Remove()` method { toc_md="Implement `Remove()`" }

The `Remove()` method has the simplest behavior. If the configuration file exists, delete it.

```powershell
[void] Remove() {
    Remove-Item -Path $this.GetConfigurationFilePath() -Force -ErrorAction Stop
}
```

## Implement the `Update()` method { toc_md="Implement `Update()`" }

The `Update()` method implementation is like the implementation for the `Create()` method. It needs
to convert the user-specified properties for the resource instance into the JSON that TSToy expects
in its configuration file and replace the settings in that file.

```powershell
[void] Update() {
    $ErrorActionPreference = 'Stop'

    $Json       = $this.ToConfigurationJson()
    $FilePath   = $this.GetConfigurationFilePath()

    Set-Content -Path $FilePath -Value $Json -Encoding utf8 -Force
}
```

## Review

With the `ToConfigurationJson()`, `Create()`, `Remove()`, and `Update()` helper methods defined,
the `Set()` method can now idempotently manage resource instances. The method:

- Returns immediately if the configuration file is in the desired state.
- Creates the configuration file with the correct settings when `$Ensure` is `Present` and the file
  doesn't exist.
- Removes the configuration file when `$Ensure` is `Absent`.
- Updates the file contents when `$Ensure` is `Present`, the file exists, and
  `$UpdateAutomatically` or `$UpdateFrequency` are out of the desired state. When it updates the
  file, it doesn't alter the unmanaged settings.
