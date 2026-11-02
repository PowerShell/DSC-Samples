---
title: Write your first DSC Resource in Go
dscs:
  tutorials_title: In Go
  languages_title: Write a DSC Resource
platen:
  menu:
    collapse_section: true
---

With Microsoft DSC, you can author command-based DSC Resources in any language. This enables you
to manage applications in the programming language you and your team prefer, or in the
same language as the application you're managing.

This tutorial describes how you can implement a DSC Resource in Go to manage an
application's configuration files. While this tutorial creates a resource to manage the
fictional [TSToy application][02], the principles apply when you author any command-based
resource.

The resource is built with [dsc-go-rdk][03], a Go library that implements the Microsoft DSC
command-based resource protocol for you: subcommand dispatch, JSON input handling, output
framing, exit codes, JSON Schema generation, and manifest generation. You implement typed
`get` and `set` operations over a plain Go struct; the library handles everything the DSC
engine expects from the executable.

In this tutorial, you learn how to:

- Create a small Go application to use as a DSC Resource.
- Define the properties of the resource as a Go struct.
- See how the library handles JSON input and errors for you.
- Implement the `get` and `set` operations for the resource.
- Generate the resource's manifest.
- Manually test the resource.

## Prerequisites

- Familiarize yourself with the structure of a command-based DSC Resource.
- Read [About the TSToy application][02], install `tstoy`, and add it to your `PATH`.
- Go 1.26 or higher
- VS Code with the Go extension

## Steps

1. [Create the DSC Resource][04]
1. [Define the configuration settings][05]
1. [See how input is handled][06]
1. [Implement get][07]
1. [Implement set][08]
1. [Generate the DSC Resource manifest][09]
1. [Validate the DSC Resource with DSC][10]
1. [Review and next steps][11]

[02]: /tstoy/about/
[03]: https://github.com/LibreDsc/dsc-go-rdk
[04]: 1-create.md
[05]: 2-define-config-settings.md
[06]: 3-handle-input.md
[07]: 4-implement-get.md
[08]: 5-implement-set.md
[09]: 6-author-manifest.md
[10]: 7-validate.md
[11]: review.md
