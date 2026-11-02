---
title: Write your first DSC Resource in C#
dscs:
  tutorials_title: In Csharp
  languages_title: Write a DSC Resource
platen:
  menu:
    collapse_section: true
---

With DSC v3, you can author command-based DSC Resources in any language. This enables you to manage
applications in the programming language you and your team prefer, or in the same language as the
application you're managing.

This tutorial describes how you can implement a DSC Resource in Go to manage an application's
configuration files. While this tutorial creates a resource to manage the fictional
[TSToy application][02], the principles apply when you author any command-based resource.

In this tutorial, you learn how to:

- Create a small C# application to use as a DSC Resource.
- Define the properties of the resource.
- Implement `get` and `set` commands for the resource.
- Write a manifest for the resource.
- Manually test the resource.

## Prerequisites

- Familiarize yourself with the structure of a command-based DSC Resource.
- Read [About the TSToy application][02], install `tstoy`, and add it to your `PATH`.
- .net8 
- VS Code with the ms-dotnettools.csdevkit

## Steps

1. [Create the DSC Resource][03]
1. [Define the configuration settings][04]
1. [Helper Functions][05]
1. [Implement get][06]
1. [Implement set][07]
1. [Author the DSC Resource manifest][08]
1. [Validate the DSC Resource with DSC][09]
1. [Review and next steps][10]

[02]: /tstoy/about/
[03]: 1-create.md
[04]: 2-define-config-settings.md
[05]: 3-helper-functions.md
[06]: 4-implement-get.md
[07]: 5-implement-set.md
[08]: 6-author-manifest.md
[09]: 7-validate.md
[10]: review.md
