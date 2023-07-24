---
title:      "`tstoy show`"
link title: "`show`"
weight:     2
---

## Synopsis

Shows the merged configuration options for the application.

## Description

This command shows the merged configuration options for the application. The settings are applied
first from the machine-level, then the user-level, then any environment variables, and finally any
flags passed to the command.

```
tstoy show [flags]
```

## Options

```cli-syntax
-h, --help           help for show
    --only strings   The list of configuration values to retrieve.
```

### `-h` / `--help` { #option-help toc_md="`--help`" }

This parameter displays the help info for the current command. When this parameter is specified,
the application ignores all other parameters.

### `--only` { #option-only }

This parameter filters the list of configuration values to display. Valid values are:

- `default` - The application's default configuration, independent of any configuration files.
- `machine` - The machine-scope configuration file settings.
- `user` - The user-scope configuration file settings.
- `final` - The effective configuration, after merging the defined configuration files over the
  default configuration.

By default, the command shows every configuration value.

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

- [tstoy](../_index.md) - A fictional application to demonstrate writing a DSC Resource.
- [tstoy show path](show-path.md) - Retrieves the path to the machine and user configs.
