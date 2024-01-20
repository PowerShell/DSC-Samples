---
title: Write your first DSC Resource using shell scripts
dscs:
  tutorials_title: In shell scripts
  languages_title: Write a DSC Resource
platen:
  menu:
    collapse_section: true
---

With Desired State Configuration (DSC) version 3, the intention is that anyone managing the state
of an environment, operating system, or application, can use their preferred programming or
scripting language to perform automation tasks.

This tutorial describes how you can implement a "hello, world" example DSC Resource using shell
scripts.

In this tutorial, you learn the fundamental parts of a Resource in DSC version 3, and how to embed
shell scripts that write "hello, world" to a temporary file.

## Prerequisites

- DSC version 3
- A Linux instance for testing (this could be a container)
- Your preferred text editor

## Steps

1. [Create a minimally viable DSC Resource][01]
1. [Add functional shell scripts to the DSC Resource][02]
1. [Add parameters to the shell script DSC Resource][03]
1. [Add metadata to the shell script DSC Resource][04]

[01]: 1-mvp.md
[02]: 2-funcitonal.md
[03]: 3-parameters.md
[04]: 4-metadata.md
