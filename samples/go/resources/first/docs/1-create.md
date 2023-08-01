---
title:  Step 1 - Create the DSC Resource
weight: 1
dscs:
  menu_title: 1. Create the resource
---

Create a new folder called `gotstoy` and open it in VS Code. This folder is the root folder for the
project.

```sh
mkdir ./gotstoy
code ./gotstoy
```

Open the integrated terminal in VS Code. In that terminal, initialize the folder as a Go module.

```sh
go mod init "github.com/<your_github_id>/gotstoy"
```

In this tutorial, you'll be creating a DSC Resource with [Cobra][01]. Cobra helps you create a
command line application in Go. It handles argument parsing, setting flags, shell completions, and
help.

Use the following command to install `cobra-cli`.

```sh
go install github.com/spf13/cobra-cli@latest
```

Use `cobra-cli` to scaffold the DSC Resource application and add the `get` and `set` commands.

```sh
cobra-cli init
cobra-cli add get
cobra-cli add set
```

Run the following commands to get the Go modules you'll be using outside of the standard library.

```sh
go get github.com/thediveo/enumflag@v0.10.1
go get github.com/TylerBrock/colorjson@v0.0.0-20200706003622-8a50f05110d2
go get github.com/knadh/koanf/maps@v0.1.1
```

The `enumflag` module simplifies using enumerations as command line flags. The `colorjson` module
enables you to pretty-print output in the console. The `maps` module makes interacting with
arbitrary maps easier.

Verify that the new application can run and has the expected commands.

```sh
go run ./main.go
```

```text
A longer description that spans multiple lines and likely contains
examples and usage of using your application. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.

Usage:
  gotstoy [command]

Available Commands:
  completion  Generate the autocompletion script for the specified shell
  get         A brief description of your command
  help        Help about any command
  set         A brief description of your command

Flags:
  -h, --help     help for gotstoy
  -t, --toggle   Help message for toggle

Use "gotstoy [command] --help" for more information about a command.
```

With the command scaffolded, you need to understand the application the DSC Resource manages before
you can implement the commands. By now, you should have read [About the TSToy application][02].

[01]: https://cobra.dev/
[02]: /tstoy/about
