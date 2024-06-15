---
title:  Review and next steps
weight: 100
---

In this tutorial, you:

1. Scaffolded a new PowerShell module with a class-based DSC Resource.
1. Defined the configurable settings to manage the TSToy application's configuration files and
   update behavior.
1. Implemented the `get` method to return the current state of a TSToy configuration file as an
   instance of the resource.
1. Implemented the `test` method to return whether the configuration file for a specified scope is
   in the desired state.
1. Implemented the `set` command to idempotently enforce the desired state for TSToy's
   configuration files.
1. Tested using the resource in PSDSC with the `Invoke-DscResource` cmdlet.
1. Tested the resource in DSCv3 by invoking the resource with the `dsc resource` commands and
   managing instances of the resource in a configuration document.

At the end of this implementation, you have a functional class-based PowerShell DSC Resource.

## Clean up

If you're not going to continue to work with this resource, delete the `DscSamples.TailspinToys`
folder and the files in it.

## Next steps

1. Read about class-based DSC Resources, learn how they work, and consider why the resource
   in this tutorial is implemented this way.
1. Consider how this resource can be improved. Are there any edge cases or features it doesn't
   handle? Can you make the user experience in the terminal more delightful? Update the
   implementation with your improvements.
