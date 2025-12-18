---
title:  Step 4 - Implement the Get method
weight: 4
dscs:
  menu_title: 4. Implement `Get()`
---

The `Get()` method retrieves the current state of the DSC Resource. It's used to inspect a resource
instance manually and is called by the `Test()` method.

The `Get()` method has no parameters and returns an instance of the class as its output. For the
`PSTailspinToys` resource, the minimal implementation looks like this:

```powershell
[PSTailspinToys] Get() {
    $CurrentState = [PSTailspinToys]::new()
    return $CurrentState
}
```

The only thing this implementation does is create an instance of the **PSTailspinToys** class and
return it. You can call the method with `Invoke-DscResource` to see this behavior.

```powershell
Invoke-DscResource -Name PSTailspinToys -Module DscSamples.TailspinToys -Method Get -Property @{
    ConfigurationScope  = 'User'
    UpdateAutomatically = $true
}
```

```console
ConfigurationScope  Ensure UpdateAutomatically UpdateFrequency
------------------  ------ ------------------- ---------------
           Machine Present               False               0
```

The returned object's properties are all set to their default value.

## Define `Get` helpers

To implement the get command, the resource needs to be able to find and load the settings from a
specific `tstoy` configuration file.

Recall from [About the TSToy application][01] that you can use the `tstoy show path` command to get
the full path to the applications configuration files. The resource can use those commands instead
of trying to generate the paths itself.

### Define `GetApplicationInfo()` { toc_md="`GetApplicationInfo()`" }

The resource needs to retrieve the `tstoy` command to call it. Define a new method for the class
called `GetApplicationInfo()`. The method should have no parameters and return a
**System.Management.Automation.ApplicationInfo** object.

```powershell
[System.Management.Automation.ApplicationInfo] GetApplicationInfo() {
    if ($null -ne $this.CachedApplicationInfo) {
        return $this.CachedApplicationInfo
    }

    try {
        $Parameters = @{
            Name        = 'tstoy'
            CommandType = 'Application'
            ErrorAction = 'Stop'
        }
        $this.CachedApplicationInfo = Get-Command @Parameters
    } catch [System.Management.Automation.CommandNotFoundException] {
        throw [System.Management.Automation.CommandNotFoundException]::new(
            "tstoy application not found, unable to retrieve path to configuration file",
            $_
        )
    }

    return $this.CachedApplicationInfo
}
```

The method generates the parameters to search for the `tstoy` command, caching it in the
`$CachedApplicationInfo` property before returning it. If the command has already been cached, the
method returns that value. If the command can't be found, the method throws an error.

### Define `GetConfigurationFilePath()` { toc_md="`GetConfigurationFilePath()`" }

Now that the resource can get a handle for the `tstoy` application, it can call the application as
a command to return the path to the configuration file for the desired scope.

Define the `GetConfigurationFilePath()` method. The method should have no parameters and return a
**String**.

```powershell
[string] GetConfigurationFilePath() {
    if (-not ([string]::IsNullOrEmpty($this.CachedConfigurationFilePath))) {
        return $this.CachedConfigurationFilePath
    }

    $this.GetApplicationInfo()

    $Arguments = @(
        'show'
        'path'
        $this.ConfigurationScope.ToString().ToLower()
    )

    $this.CachedConfigurationFilePath = & $this.CachedApplicationInfo @Arguments

    return $this.CachedConfigurationFilePath
}
```

The method calls `tstoy show path <scope>` and caches the result string as the value for
`$CachedConfigurationFilePath`. If the path has already been cached, it returns that value instead.

### Define `GetConfigurationData()` { toc_md="`GetConfigurationData()`" }

The last helper required for `Get` is to retrieve and cache the configuration data from the scope
configuration file.

Define the `GetConfigurationData()` method. The method should have no parameters and return a
**PSCustomObject**.

```powershell
[PSCustomObject] GetConfigurationData() {
    if ($null -ne $this.CachedData) {
        return $this.CachedData
    }

    $ConfigurationFilePath = $this.GetConfigurationFilePath()

    if (-not (Test-Path -Path $ConfigurationFilePath)) {
        return $null
    }

    try {
        $GetParameters = @{
            Path        = $ConfigurationFilePath
            Raw         = $true
        }

        $this.CachedData = Get-Content @GetParameters
        | ConvertFrom-Json -ErrorAction Stop
    } catch [Newtonsoft.Json.JsonReaderException] {
        throw [Newtonsoft.Json.JsonReaderException]::new(
            "Unable to load TSToy configuration data from $ConfigurationFilePath",
            $_
        )
    }

    return $this.CachedData
}
```

### Verify helper methods

With the three helper methods defined, you can test them. Execute the `using` statement to load the
**DscSamples.TailspinToys** module's classes and enums into your current session.

```powershell
using module ./DscSamples.TailspinToys.psd1

$machine = [PSTailspinToys]@{ ConfigurationScope = 'Machine' }
$machine.GetApplicationInfo()
$machine.GetConfigurationFilePath()
$null -eq $machine.GetConfigurationData()

$user = [PSTailspinToys]@{ ConfigurationScope = 'User' }
$user.GetConfigurationFilePath()
$null -eq $user.GetConfigurationData()
```

```console
CommandType  Name       Version  Source
-----------  ----       -------  ------
Application  tstoy.exe  0.0.0.0   C:\Users\mikey\go\bin\tstoy.exe

C:\ProgramData\TailSpinToys\tstoy\tstoy.config.json

True

C:\Users\mikey\AppData\Local\TailSpinToys\tstoy\tstoy.config.json

True
```

The `GetConfigurationData()` method returned `$null` because the configuration files doesn't exist
yet.

Create the user scope configuration file.

```powershell
New-Item -Path (tstoy show path user) -Force -Value @'
{
    "unmanaged_key": true,
    "updates": {
        "automatic": true,
        "checkFrequency": 30
    }
}
'@
```

```console
    Directory: C:\Users\mikey\AppData\Local\TailSpinToys\tstoy

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---           8/15/2023 11:47 AM              0 tstoy.config.json
```

Call the `GetConfigurationData()` method for the user-scope again.

```powershell
$user.GetConfigurationData()
```

```console
unmanaged_key updates
------------- -------
         True @{automatic=True; checkFrequency=30}
```

Exit the terminal in VS Code and open a new terminal. Dot-source `Helpers.ps1`.

```powershell
. ./Helpers.ps1
```

Now you can write the rest of the `Get()` method.

## Return the actual state

The value of `$ConfigurationScope` should always be the value the user supplied. To make the
`Get()` method useful, it must return the actual state of the resource instance.

```powershell
[PSTailspinToys] Get() {
    $CurrentState = [PSTailspinToys]::new()

    $CurrentState.ConfigurationScope = $this.ConfigurationScope

    $this.CachedCurrentState = $CurrentState

    return $CurrentState
}
```

The `$this` variable references the working instance of the resource. Now, if you use
`Invoke-DscResource` again, `$ConfigurationScope` has the correct value.

```powershell
Invoke-DscResource -Name PSTailspinToys -Module DscSamples.TailspinToys -Method Get -Property @{
    ConfigurationScope  = 'User'
    UpdateAutomatically = $true
}
```

```console
ConfigurationScope  Ensure UpdateAutomatically UpdateFrequency
------------------  ------ ------------------- ---------------
              User Present               False               0
```

Now you can write the rest of the `Get()` method.

```powershell
[PSTailspinToys] Get() {
    $CurrentState = [PSTailspinToys]::new()

    $CurrentState.ConfigurationScope = $this.ConfigurationScope

    $FilePath = $this.GetConfigurationFilePath()

    if (!(Test-Path -path $FilePath)) {
        $CurrentState.Ensure = [TailspinEnsure]::Absent
        return $CurrentState
    }

    $Data = $this.GetConfigurationData()

    if ($null -ne $Data.Updates.Automatic) {
        $CurrentState.UpdateAutomatically = $Data.Updates.Automatic
    }

    if ($null -ne $Data.Updates.CheckFrequency) {
        $CurrentState.UpdateFrequency = $Data.Updates.CheckFrequency
    }

    $this.CachedCurrentState = $CurrentState

    return $CurrentState
}
```

After setting the `$ConfigurationScope` and determining the configuration file's path, the method
checks to see if the file exists. If it doesn't exist, setting `$Ensure` to `Absent` and returning
the result is all that's needed.

If the file does exist, the method needs to retrieve the configuration data. The
`GetConfigurationData()` method returns the data and caches it. Caching the data allows you to
inspect the data during development and will be useful when implementing the `Set()` method.

Next, the method checks to see if the managed keys have any value before
assigning them to the current state's properties. If they're not specified, the resource must
consider them unset and in their default state.

You can verify this behavior locally.

```powershell
$GetParameters = @{
    Name     = 'PSTailspinToys'
    Module   = 'DscSamples.TailspinToys'
    Method   = 'Get'
    Property = @{
        ConfigurationScope = 'Machine'
    }
}

Invoke-DscResource @GetParameters

$GetParameters.Property.ConfigurationScope = 'User'
Invoke-DscResource @GetParameters
```

```console
ConfigurationScope Ensure UpdateAutomatically UpdateFrequency
------------------ ------ ------------------- ---------------
           Machine Absent               False               0

ConfigurationScope  Ensure UpdateAutomatically UpdateFrequency
------------------  ------ ------------------- ---------------
              User Present                True              30
```

The `Get()` method now returns accurate information about the current state of the resource
instance.

[01]: /tstoy/about/
