---
title:  Review and next steps
weight: 100
---

In this tutorial, you:

1. Created a new Go module and turned it into a working DSC protocol CLI with dsc-go-rdk.
1. Defined the configurable settings for TSToy's configuration files as a plain Go struct,
   and generated the instance JSON Schema from it.
1. Saw how the library handles JSON input, structured error output, and exit codes, and
   added the resource's own semantic validation.
1. Implemented the get operation to return the current state of a TSToy configuration file
   as an instance of the DSC Resource.
1. Implemented the set operation to idempotently enforce the desired state for TSToy's
   configuration files.
1. Generated the DSC Resource manifest from the resource's configuration and capabilities.
1. Tested the integration of the DSC Resource with DSC itself.

At the end of this implementation, you have a functional command-based DSC Resource
written in Go. The code you wrote is almost entirely TSToy domain logic — the protocol
details (argument parsing, stdin handling, output framing, exit codes, schema, and
manifest) live in the library, where they're implemented once and tested against the DSC
engine's contract.

## Clean up

If you're not going to continue to work with this DSC Resource, delete the `gotstoy`
folder and the files in it. Remove any TSToy configuration files you created:

```sh
tstoy show path machine
tstoy show path user
```

Delete those files if they exist.

## Next steps

The capability model makes the resource easy to grow — each new interface your handler
implements is automatically dispatched, framed, and advertised in the manifest:

1. Implement `Export` (`Export(ctx, filter) ([]Settings, error)`) to enumerate both
   scopes, then try `dsc resource export`.
1. Implement `Test` with domain-aware comparison (for example, treating an unspecified
   `updateFrequency` as "don't care") and see the manifest gain a `test` method.
1. Implement `SetWhatIf` and try `dsc config set --what-if` with native what-if output.
1. Read about command-based DSC Resources, learn how they work, and consider why the DSC
   Resource in this tutorial is implemented this way.
