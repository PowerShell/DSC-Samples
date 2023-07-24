---
title:  Review and next steps
weight: 100
---

In this tutorial, you:

1. Scaffolded a new Go app as a DSC Resource.
1. Defined the configurable settings to manage the TSToy application's configuration files and
   update behavior.
1. Added flags to enable users to configure TSToy in the terminal with validation and completion
   suggestions.
1. Added handling so the DSC Resource can use JSON input with a flag or from `stdin`.
1. Implemented the `get` command to return the current state of a TSToy configuration file as an
   instance of the DSC Resource.
1. Added handling so the `get` command can retrieve every instance of the DSC Resource.
1. Implemented the `set` command to idempotently enforce the desired state for TSToy's
   configuration files.
1. Tested the DSC Resource as a standalone application.
1. Authored a DSC Resource manifest and defined a JSON Schema for instances of the DSC Resource.
1. Tested the integration of the DSC Resource with DSC itself.

At the end of this implementation, you have a functional command-based DSC Resource written in Go.

## Clean up

If you're not going to continue to work with this DSC Resource, delete the `gotstoy` folder and the
files in it.

## Next steps

1. Read about command-based DSC Resources, learn how they work, and consider why the DSC Resource
   in this tutorial is implemented this way.
1. Consider how this DSC Resource can be improved. Are there any edge cases or features it doesn't
   handle? Can you make the user experience in the terminal more delightful? Update the
   implementation with your improvements.
