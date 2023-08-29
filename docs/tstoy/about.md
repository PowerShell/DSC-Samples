---
title:     About the TSToy application
linktitle: About
---

## Overview

For the purposes of the command-based DSC Resource tutorials, you're creating a DSC Resource to
manage the fictional Tailspin Toys application, `tstoys`.

The application has configuration options that control whether it should look for updates and how
frequently to do so. Like many real applications, `tstoy` uses a combination of arguments,
environment variables, and configuration files. For these tutorials, the DSC Resource only needs to
manage the configuration files.

## Installing TSToy

```````````tabs
---
id:        install-instructions
placement: start
---
``````tab { name="From Archive" }
[Download the latest release][t1] for your operating system. After you download
the release archive, you need to expand the archive and add it to your `PATH`.
You'll need the application while following any of the tutorials in this
section.

[t1]: https://github.com/PowerShell/DSC-Samples/tree/main/tstoy/latest
``````

``````tab { name="With Go" }
If you have Go installed on your system, you can use `go install` to get the
latest version of the application and install it to your `GOPATH`.

```sh
go install github.com/PowerShell/DSC-Samples/tstoy@latest
```
``````
```````````

<!-- Add tabbed examples for doing so -->

Once you have `tstoy` installed and added to your path, you can call it to see the available
commands:

```sh
tstoy
```

You can enable shell completions for the application to make interacting with it easier.

```````````tabs
---
id: enable-shell-completions
placement: start
class: shell-completion
---
``````tab { name="Bash" }
```bash
# bash
tstoy completion bash --help
source <(tstoy completion bash)
```
``````

``````tab { name="fish" }
```fish
# fish
tstoy completion fish --help
tstoy completion fish | source
```
``````

``````tab { name="PowerShell" }
```powershell
# PowerShell
tstoy completion powershell --help
tstoy completion powershell | Out-String | Invoke-Expression
```
``````

``````tab { name="ZSH" }
```zsh
# zsh
tstoy completion zsh --help
source <(tstoy completion zsh)
```
``````
```````````

## TSToy configuration

The TSToy application uses two configuration files. The configuration for all users is the
_machine_-scope configuration file. The configuration for the current user is the _user_-scope
configuration file.

When TSToy runs, it starts with a default configuration. If the machine-scope configuration file
exists, TSToy overrides the default configuration with the settings in that file. Then, if the
user-scope configuration file exists, TSToy overrides the configuration with the settings in that
file.

The DSC Resource needs to be able to manage both the machine and user scope configuration files.

TSToy expects the configuration files to be JSON files. It uses settings in the `updates`
key of that JSON file to control the update behavior.

TSToy uses this default configuration:

```json
{
    "updates": {
        "automatic": true,
        "checkFrequency": 90
    }
}
```

When `automatic` is set to `true`, TSToy looks for updates when it starts. The value of
`checkFrequency` indicates how many days it should wait before looking for updates
again. TSToy only considers the `checkFrequency` setting valid when it's an integer
between `1` and `90`, inclusive.

Your DSC Resource needs to manage:

- Whether the configuration file in a specific scope should exist
- Whether it sets the configuration to automatically update
- How many days it sets the configuration to wait before looking for updates

## TSToy commands

While working through the tutorials, you'll need to retrieve the configuration files path that
`tstoy` uses. You can get the paths to the configuration files with the `show path` command:

```sh
# Outputs both paths, with the machine-scope configuration file first.
tstoy show path
# Outputs only the path to the machine-scope configuration file.
tstoy show path machine
# Outputs only the path to the user-scope configuration file.
tstoy show path user
```

``````tabs
---
id: command-output
---
````tab { name="On Windows" }
```powershell
tstoy show path
```
```text
C:\ProgramData\TailSpinToys\tstoy\tstoy.config.json
C:\Users\mikey\AppData\Local\TailSpinToys\tstoy\tstoy.config.json
```
```powershell
tstoy show path machine
```
```text
C:\ProgramData\TailSpinToys\tstoy\tstoy.config.json
```
```powershell
tstoy show path user
```
```text
C:\Users\mikey\AppData\Local\TailSpinToys\tstoy\tstoy.config.json
```
````

````tab { name="On Ubuntu" }
```sh
tstoy show path
```
```text
/etc/xdg/TailSpinToys/tstoy/tstoy.config.json
/home/mikey/.config/TailSpinToys/tstoy/tstoy.config.json
```
```sh
tstoy show path machine
```
```text
/etc/xdg/TailSpinToys/tstoy/tstoy.config.json
```
```sh
tstoy show path user
```
```text
/home/mikey/.config/TailSpinToys/tstoy/tstoy.config.json
```
````
``````

You may also want to see how TSToy is interpreting the configuration files to validate your work.
Use the `show` command to get the application's default settings, the settings from each
configuration scope, and the final merged settings.

```sh
# Show all settings
tstoy show
```

```yaml
Default configuration: {
  "Updates": {
    "Automatic": false,
    "CheckFrequency": 90
  }
}
Machine configuration: {}
User configuration: {}
Final configuration: {
  "Updates": {
    "Automatic": false,
    "CheckFrequency": 90
  }
}
```

Use the `--only` flag to get a subset of configuration.

```sh
tstoy show --only machine,user
```

```yaml
Machine configuration: {}
User configuration: {}
```
