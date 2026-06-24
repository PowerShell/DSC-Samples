---
title: Write your first DSC Resource in PowerShell
dscs:
  tutorials_title: In PowerShell
  languages_title: Write a DSC Resource
platen:
  menu:
    collapse_section: true
---

With DSC v3, you can author command-based DSC Resources in any language. This enables you to manage
applications in the programming language you and your team prefer, or in the same language as the
application you're managing.

DSC v3 also supports authoring DSC Resources in PowerShell. PowerShell resources are made available
through the `DSC/PowerShellGroup` resource provider and the **PSDesiredStateConfiguration**
PowerShell module.

This tutorial describes how you can implement a DSC Resource as a PowerShell class to manage an
application's configuration files. While this tutorial creates a resource to manage the fictional
[Tailspin Toys `tstoy` application][01], the principles apply when you author any class-based
PowerShell resource.

In this tutorial, you learn how to:

- Create a small Go application to use as a DSC Resource.
- Define the properties of the resource.
- Implement `get` and `set` commands for the resource.
- Write a manifest for the resource.
- Manually test the resource.

## Prerequisites

- Familiarize yourself with the structure of a command-based DSC Resource.
- Read [About the TSToys application][01], install `tstoy`, and add it to your `PATH`.
- PowerShell 7.2 or higher.
- VS Code with the PowerShell extension.

## Steps

1. [Scaffold a DSC Resource module][02]
1. [Add a class-based DSC Resource][03]
1. [Define the configuration properties][04]
1. [Implement the Get method][05]
1. [Implement the Test method][06]
1. [Implement the Set method][07]
1. [Validate the DSC Resource with DSC and PSDSC][08]
1. [Review and next steps][09]

[01]: /tstoy/about/
[02]: 1-scaffold-module.md
[03]: 2-add-class-based-resource.md
[04]: 3-define-properties.md
[05]: 4-implement-get.md
[06]: 5-implement-test.md
[07]: 6-implement-set.md
[08]: 7-validate.md
[09]: review.md
