---
title:     Contributing a tutorial
linktitle: Tutorials
weight:    30
---

The samples repository includes two types of tutorials.

The first type of tutorial is the general DSC tutorial. These tutorials document how to use DSC
itself for different tasks and contexts.

The other type of tutorial is the DSC Resource tutorial. These tutorials show how a user can author
a resource or extend an existing resource's functionality. The resource tutorials are organized by
learning goal. Each tutorial may have any number of language-specific implementations. Every
implementation for a given tutorial must result in the same functionality and learned lessons when
a reader completes the tutorial.

When a new resource tutorial is created, a tutorial specification is documented for it. If you're
contributing a new tutorial, the documentation team will work with you on the specification. You
don't need to write the specification yourself.

## Submitting a tutorial

To submit a new tutorial of any type, first file an issue in the repository. The documentation team
will work with you on your submission to help refine it. You can just file requests for new
tutorials without any intent to author the tutorial yourself.

## Adding a tutorial implementation

To submit a new language implementation for an existing resource tutorial, follow these steps:

1. Read the specification documentation for that tutorial. Your sample code must fulfill the
   tutorial's specification.
1. Implement the sample code to the tutorial's specifications.
1. Submit the sample code as a pull request and indicate whether you're authoring the draft of the
   tutorial yourself. The author of the sample code for a tutorial implementation doesn't need to
   author the documentation for it.
1. Collaborate with the documentation team to refine your sample code and the documentation.
