---
title:  Step 3 - Define the configuration properties
weight: 3
dscs:
  menu_title: 3. Define properties
---

You should define the properties of the DSC Resource before the methods. The properties define the
manageable settings for the resource instances. They're used in the methods.

The resource needs to manage four properties: `$ConfigurationScope`, `$Ensure`,
`$UpdateAutomatically`, and `$UpdateFrequency`.

## Define `$ConfigurationScope`

The `$ConfigurationScope` property defines which instance of the `tstoy` configuration file the
resource should manage. To define the `$ConfigurationScope` property in the resource, add the
following code in the class before the methods:

```powershell
[DscProperty(Key)] [TailspinScope]
$ConfigurationScope
```

This code defines `$ConfigurationScope` as a **Key** property of the resource. A **Key** property
is used to uniquely identify an instance of the resource. Adding this property meets one of the
requirements the **DscResource** attribute warned about when you scaffolded the class.

It also specifies that `$ConfigurationScope`'s type is **TailspinScope**. To define the
**TailspinScope** type, add the following **TailspinScope** enum after the class definition in
`DscSamples.TailspinToys.psm1`:

```powershell
enum TailspinScope {
    Machine
    User
}
```

This enumeration makes `Machine` and `User` the only valid values for the `$ConfigurationScope`
property of the resource.

## Define `$Ensure`

It's best practice to define an `$Ensure` property to control whether an instance of a resource
exists. An `$Ensure` property usually has two valid values, `Absent` and `Present`.

- If `$Ensure` is specified as `Present`, the resource creates the item if it doesn't exist.
- If `$Ensure` is `Absent`, the resource deletes the item if it exists.

For the **PSTailspinToys** resource, the item to create or delete is the configuration file for the
specified `$ConfigurationScope`.

Define **TailspinEnsure** as an enum after **TailspinScope**. It should have the values `Absent`
and `Present`.

```powershell
enum TailspinEnsure {
    Absent
    Present
}
```

Next, add the `$Ensure` property in the class after the `$ConfigurationScope` property. It should
have an empty **DscProperty** attribute and its type should be **TailspinEnsure**. It should default
to `Present`.

```powershell
[DscProperty()] [TailspinEnsure]
$Ensure = [TailspinEnsure]::Present
```

## Define `$UpdateAutomatically`

To manage automatic updates, define the `$UpdateAutomatically` property in the class after the
`$Ensure` property. Its **DscProperty** attribute should indicate that it's mandatory and its type
should be **boolean**.

```powershell
[DscProperty(Mandatory)] [bool]
$UpdateAutomatically
```

## Define `$UpdateFrequency`

To manage how often `tstoy` should check for updates, add the `$UpdateFrequency` property in the
class after the `$UpdateAutomatically` property. It should have an empty **DscProperty** attribute
and its type should be **int**. Use the **ValidateRange** attribute to limit the valid values for
`$UpdateFrequency` to between 1 and 90.

```powershell
[DscProperty()] [int] [ValidateRange(1, 90)]
$UpdateFrequency
```

## Add hidden cache properties

Next, add three hidden properties for caching the current state of the resource:
`$CachedCurrentState`, `$CachedData`, and `$CachedApplicationInfo`. Set the type of
`$CachedCurrentState` to **PSTailspinToys**, the same as the class and the return type for the
`Get()` method. Set the type of `$CachedData` to **PSCustomObject**. Set the type of
`$CachedApplicationInfo` to **System.Management.Automation.ApplicationInfo**. Prefix the properties
with the `hidden` keyword. Don't specify the **DscProperty** attribute for them.

```powershell
hidden [PSTailspinToys]                               $CachedCurrentState
hidden [PSCustomObject]                               $CachedData
hidden [System.Management.Automation.ApplicationInfo] $CachedApplicationInfo
```

These hidden properties will be used in the `Get()` and `Set()` methods that you define later.

## Review the module file

At this point, `DscSamples.TailspinToys.psm1` should define:

- The **PSTailspinToys** class with the properties `$ConfigurationScope`, `$Ensure`,
  `$UpdateAutomatically`, and `$UpdateFrequency`
- The **TailspinScope** enum with the values `Machine` and `User`
- The **TailspinEnsure** enum with the values `Present` and `Absent`
- The minimal implementations of the `Get()`, `Test()`, and `Set()` methods.

```powershell
[DscResource()]
class PSTailspinToys {
    [DscProperty(Key)] [TailspinScope]
    $ConfigurationScope

    [DscProperty()] [TailspinEnsure]
    $Ensure = [TailspinEnsure]::Present

    [DscProperty(Mandatory)] [bool]
    $UpdateAutomatically

    [DscProperty()] [int] [ValidateRange(1,90)]
    $UpdateFrequency

    hidden [PSTailspinToys]                               $CachedCurrentState
    hidden [PSCustomObject]                               $CachedData
    hidden [System.Management.Automation.ApplicationInfo] $CachedApplicationInfo
    hidden [string]                                       $CachedConfigFilePath

    [PSTailspinToys] Get() {
        $CurrentState = [PSTailspinToys]::new()
        return $CurrentState
    }

    [bool] Test() {
        $InDesiredState = $true
        return $InDesiredState
    }

    [void] Set() {}
}

enum TailspinScope {
    Machine
    User
}

enum TailspinEnsure {
    Absent
    Present
}
```

## Inspect the resource

Now that the resource class meets the requirements, you can use `Get-DscResource` to see it. In VS
Code, open a new PowerShell terminal.

```powershell
. ./Helpers.ps1
Get-DscResource -Name PSTailspinToys -Module DscSamples.TailspinToys | Format-List
Get-DscResource -Name PSTailspinToys -Module DscSamples.TailspinToys -Syntax
```

```console
ImplementationDetail : ClassBased
ResourceType         : PSTailspinToys
Name                 : PSTailspinToys
FriendlyName         :
Module               : DscSamples.TailspinToys
ModuleName           : DscSamples.TailspinToys
Version              : 0.0.1
Path                 : C:\code\dsc\DscSamples.TailspinToys\DscSamples.TailspinToys.psd1
ParentPath           : C:\code\dsc\DscSamples.TailspinToys
ImplementedAs        : PowerShell
CompanyName          : Unknown
Properties           : {ConfigurationScope, UpdateAutomatically, DependsOn, Ensure…}

PSTailspinToys [String] #ResourceName
{
    ConfigurationScope = [string]{ Machine | User }
    UpdateAutomatically = [bool]
    [DependsOn = [string[]]]
    [Ensure = [string]{ Absent | Present }]
    [PsDscRunAsCredential = [PSCredential]]
    [UpdateFrequency = [Int32]]
}
```
