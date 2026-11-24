---
title:  Step 5 - Implement the Test method
weight: 5
dscs:
  menu_title: 5. Implement `Test()`
---

With the `Get()` method implemented, you can verify whether the current state is compliant with the
desired state.

The `Test()` method minimal implementation always returns `$true`.

```powershell
[bool] Test() {
    return $true
}
```

You can verify that by running `Invoke-DscResource`.

```powershell
$SharedParameters = @{
    Name     = 'PSTailspinToys'
    Module   = 'DscSamples.TailspinToys'
    Property = @{
        ConfigurationScope = 'User'
        UpdateAutomatically = $false
    }
}

Invoke-DscResource -Method Get @SharedParameters
Invoke-DscResource -Method Test @SharedParameters
```

```console
ConfigurationScope  Ensure UpdateAutomatically UpdateFrequency
------------------  ------ ------------------- ---------------
              User Present                True              30

InDesiredState
--------------
          True
```

## Test the `$Ensure` property { toc_md="Test `$Ensure`" }

You need to make the `Test()` method accurately reflect whether the DSC Resource is in the desired
state. The `Test()` method should always call the `Get()` method to have the current state to
compare against the desired state. Then check whether the `$Ensure` property is correct. If it
isn't, return `$false` immediately. No further checks are required if the `$Ensure` property is out
of the desired state.

```powershell
[bool] Test() {
    $CurrentState = $this.Get()

    if ($CurrentState.Ensure -ne $this.Ensure) {
        return $false
    }

    return $true
}
```

Now you can verify the updated behavior.

```powershell
$TestParameters = @{
    Name     = 'PSTailspinToys'
    Module   = 'DscSamples.TailspinToys'
    Property = @{
        ConfigurationScope  = 'User'
        UpdateAutomatically = $false
        Ensure              = 'Absent'
    }
}

Invoke-DscResource -Method Test @TestParameters

$TestParameters.Property.Ensure = 'Present'

Invoke-DscResource -Method Test @TestParameters
```

```console
InDesiredState
--------------
         False

InDesiredState
--------------
          True
```

Next, check to see if the value of `$Ensure` is `Absent`. If the configuration file doesn't exist
and shouldn't exist, there's no reason to check the remaining properties.

```powershell
[bool] Test() {
    $CurrentState = $this.Get()

    if ($CurrentState.Ensure -ne $this.Ensure) {
        return $false
    }

    if ($CurrentState.Ensure -eq [TailspinEnsure]::Absent) {
        return $true
    }

    return $true
}
```

## Test the `$UpdateAutomatically` property { toc_md="Test `$UpdateAutomatically`" }

Now that the method handles the `$Ensure` property, it should check if the `$UpdateAutomatically`
property is in the correct state. If it isn't, return `$false`.

```powershell
[bool] Test() {
    $CurrentState = $this.Get()

    if ($CurrentState.Ensure -ne $this.Ensure) {
        return $false
    }

    if ($CurrentState.Ensure -eq [TailspinEnsure]::Absent) {
        return $true
    }

    if ($CurrentState.UpdateAutomatically -ne $this.UpdateAutomatically) {
        return $false
    }

    return $true
}
```

## Test the `$UpdateFrequency` property { toc_md="Test `$UpdateFrequency`" }

To compare `$UpdateFrequency`, we need to determine if the user specified the value. Because
`$UpdateFrequency` is initialized to `0` and the property's **ValidateRange** attribute specifies
that it must be between `1` and `90`, we know that a value of `0` indicates that the property wasn't
specified.

With that information, the `Test()` method should:

1. Return `$true` if the user didn't specify `$UpdateFrequency`
1. Return `$false` if the user did specify `$UpdateFrequency` and the value of the system doesn't
   equal the user-specified value
1. Return `$true` if neither of the prior conditions were met

```powershell
[bool] Test() {
    $CurrentState = $this.Get()

    if ($CurrentState.Ensure -ne $this.Ensure) {
        return $false
    }

    if ($CurrentState.Ensure -eq [TailspinEnsure]::Absent) {
        return $true
    }

    if ($CurrentState.UpdateAutomatically -ne $this.UpdateAutomatically) {
        return $false
    }

    if ($this.UpdateFrequency -eq 0) {
        return $true
    }

    if ($CurrentState.UpdateFrequency -ne $this.UpdateFrequency) {
        return $false
    }

    return $true
}
```

## Review and validate the `Test()` method { toc_md="Review and Validate" }

Now the `Test()` method uses the following order of operations:

1. Retrieve the current state of TSToy's configuration.
1. Return `$false` if the configuration exists when it shouldn't or doesn't exist when it should.
1. Return `$true` if the configuration doesn't exist and shouldn't exist.
1. Return `$false` if the configuration's automatic update setting doesn't match the desired one.
1. Return `$true` if the user didn't specify a value for the update frequency setting.
1. Return `$false` if the user's specified value for the update frequency setting doesn't match the
  configuration's setting.
1. Return `$true` if none of the prior conditions were met.

You can verify the `Test()` method locally:

```powershell
$SharedParameters = @{
    Name     = 'PSTailspinToys'
    Module   = 'DscSamples.TailspinToys'
    Property = @{
        ConfigurationScope  = 'User'
        Ensure              = 'Present'
        UpdateAutomatically = $false
    }
}

Invoke-DscResource -Method Get @SharedParameters

Invoke-DscResource -Method Test @SharedParameters

$SharedParameters.Property.UpdateAutomatically = $true
Invoke-DscResource -Method Test @SharedParameters

$SharedParameters.Property.UpdateFrequency = 1
Invoke-DscResource -Method Test @SharedParameters
```

```console
ConfigurationScope  Ensure UpdateAutomatically UpdateFrequency
------------------  ------ ------------------- ---------------
              User Present                True              30

InDesiredState
--------------
         False

InDesiredState
--------------
          True

InDesiredState
--------------
         False
```

With this code, the `Test()` method is able to accurately determine whether the configuration file
is in the desired state.
