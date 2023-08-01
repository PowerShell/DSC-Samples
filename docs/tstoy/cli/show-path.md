---
title:      "`tstoy show path`"
link title: "`path`"
weight:     3
---

## Synopsis

Retrieves the path to the machine and user configs

## Description

You can use this command to retrieve the path to the configuration files that the application looks
for on your system.

If you don't specify any arguments for this command, it returns the paths to both files, with the
machine scope configuration file first.

```cli-syntax
tstoy show path [option flags] [scope]
```

## Scope

This command accepts a single argument specifying which configuration file path to return. When you
specify `machine`, the command returns the path to the machine-scope configuration file on your
computer. When you specify `user`, the command returns the path to the user-scope configuration
file.

## Options

```cli-syntax
  -h, --help   help for path
```

### `-h` / `--help` { #option-help toc_md="`--help`" }

This parameter displays the help info for the current command. When you specify this parameter, the
application ignores all other parameters.

## Inherited options

```cli-syntax
    --config string          config file
    --update-automatically   Specifies whether the app should update automatically
    --update-frequency int   Specifies the frequency window for updates in days.
```

### `--config` { #inherited-option-config }

This parameter enables you to specify a configuration file to use for the application. When
this parameter isn't specified, the application merges the user-scope configuration over the
machine-scope configuration.

### `--update-automatically` { #inherited-option-update-automatically }

This flag parameter specifies whether the application should update automatically if the update
frequency window has elapsed. When you specify this flag, the value overrides any settings from
configuration. If you specify this flag without the `=<value>` suffix, the value is `true`.

To set automatic updates to `false` with this parameter, use this syntax:

```sh
tstoy --update-automatically=false
```

### `--update-frequency` { #inherited-option-update-frequency }

This parameter specifies the length of the application's update frequency window in days. When you
specify this parameter, the value overrides any settings from configuration.

## Related links

- [tstoy show](./_index.md) - Shows the merged configuration options for the application.
