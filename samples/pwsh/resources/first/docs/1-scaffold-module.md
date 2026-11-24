---
title:  Step 1 - Scaffold a DSC Resource module
weight: 1
dscs:
  menu_title: 1. Scaffold a module
---

PowerShell resources are defined in PowerShell modules.

## Create the module folder

Create a new folder called `DscSamples.TailspinToys`. This folder is used as the root folder for
the module and all code in this tutorial.

```powershell
New-Item -Path './DscSamples.TailspinToys' -ItemType Directory
```

```console
    Directory: C:\code\dsc

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d----           8/14/2023  3:56 PM                DscSamples.TailspinToys
```

### Use VS Code to author the module

Open the `DscSamples.TailspinToys` folder in VS Code. Open the integrated terminal in VS Code. Make
sure your terminal is running PowerShell or Windows PowerShell.

```alert
---
variant: primary
---

For the rest of this tutorial, run the specified commands in the integrated
terminal at the root of the module folder. This is the default working
directory in VS Code.
```

### Create the module files

Create the module manifest with the `New-ModuleManifest` cmdlet. Use
`./DscSamples.TailspinToys.psd1` as the **Path**. Specify **RootModule** as
`DscSamples.TailspinToys.psm1` and **DscResourcesToExport** as `Tailspin`.

```powershell
$ModuleSettings = @{
    RootModule           = 'DscSamples.TailspinToys.psm1'
    DscResourcesToExport = 'PSTailspinToys'
}

New-ModuleManifest -Path ./DscSamples.TailspinToys.psd1 @ModuleSettings
Get-Module -ListAvailable -Name ./DscSamples.TailspinToys.psd1 | Format-List
```

```console
Name              : DscSamples.TailspinToys
Path              : C:\code\dsc\DscSamples.TailspinToys\DscSamples.TailspinToys.psd1
Description       :
ModuleType        : Script
Version           : 0.0.1
PreRelease        :
NestedModules     : {}
ExportedFunctions :
ExportedCmdlets   :
ExportedVariables :
ExportedAliases   :
```

Create the root module file as `DscSamples.TailspinToys.psm1`.

```powershell
New-Item -Path ./DscSamples.TailspinToys.psm1
```

```console
    Directory: C:\code\dsc\DscSamples.TailspinToys

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---            9/8/2022  1:57 PM              0 DscSamples.TailspinToys.psm1
```

Create a script file called `Helpers.ps1`.

```powershell
New-Item -Path ./Helpers.ps1
```

```console
    Directory: C:\code\dsc\DscSamples.TailspinToys

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---            9/8/2022  1:58 PM              0 Helpers.ps1
```

Open `Helpers.ps1` in VS Code. Add the following lines.

```powershell
$env:PSModulePath      += [System.IO.Path]::PathSeparator + $pwd
$MachinePath, $UserPath = tstoy show path
```

Open `DscSamples.TailspinToys.psm1` in VS Code. The module is now scaffolded and ready for you to
author a PowerShell DSC Resource.
