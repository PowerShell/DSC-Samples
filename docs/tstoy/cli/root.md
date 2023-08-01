---
title:  "`tstoy`"
weight: 1
---

## Synopsis

A fictional application to demonstrate writing a DSC Resource.

## Description

This is a fictional application with a handful of configuration options defined so you can write a
Desired State Configuration (DSC) Resource against a known application.

While a real application could define its own manifest for a DSC Resource, tstoy doesn't. Instead,
the DSC documentation includes example DSC Resources all managing this application but written in
different programming languages.

## Options

```cli-syntax
    --config string          config file
-h, --help                   help for tstoy
    --update-automatically   Specifies whether the app should update automatically
    --update-frequency int   Specifies the frequency window for updates in days.
```

### `--config` { #option-config }

This parameter enables you to specify a configuration file to use for the application. When
this parameter isn't specified, the application merges the user-scope configuration over the
machine-scope configuration.

### `-h` / `--help` { #option-help toc_md="`--help`" }

This parameter displays the help info for the current command. When you specify this parameter, the
application ignores all other parameters.

### `--update-automatically` { #option-update-automatically }

This flag parameter specifies whether the application should update automatically if the update
frequency window has elapsed. When you specify this flag, the value overrides any settings from
configuration. If you specify this flag without the `=<value>` suffix, the value is `true`.

To set automatic updates to `false` with this parameter, use this syntax:

```sh
tstoy --update-automatically=false
```

### `--update-frequency` { #option-update-frequency }

This parameter specifies the length of the application's update frequency window in days. When you
specify this parameter, the value overrides any settings from configuration.

## Related links

- [tstoy show](./show/_index.md) - Shows the merged configuration options for the application.
