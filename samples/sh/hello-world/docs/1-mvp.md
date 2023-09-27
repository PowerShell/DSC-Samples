---
title:  Step 1 - Create a minimally viable DSC Resource
weight: 1
dscs:
  menu_title: 1. Create mvp
---

Create a new project folder called `dsc-sh-helloworld`.

```sh
mkdir ./dsc-sh-helloworld
```

Create and open a new file in your preferred editor.
For this example, we use `nano`.

```sh
cd ./dsc-sample-sh-helloworld
nano ./helloworld.dsc.resource.json
```

Copy and paste the following contents into the editor. Then save the file and exit.

```json
{
    "$schema": "https://raw.githubusercontent.com/PowerShell/DSC/main/schemas/2023/08/bundled/resource/manifest.json",
    "type": "sh.Example/helloworld",
    "version": "0.1.0",
    "get": {
        "executable": "echo",
        "args": [
            "{\"return\": \"hello, world\"}"
        ]
    },
    "schema": {
        "embedded": {}
    }
}
```

What did we just create? The `.json` file provides metadata to the `dsc` executable
about the DSC Resource. There are 5 sections in the file that you should understand
before moving on.

1) **$schema**: Identifies the version of DSC Resource schema used to validate the file for
  editors that support language service.
1) **type**__**: A type name for the resource. This is the name for the resource used
  by commands like `dsc resource list`, and in configuration files.
1) **version**: The version of this DSC Resource.
1) **get**: A section to describe details about executing `get` operations.
1) **schema**: The parameters for the resource (not used in this example).

More properties are available but DSC requires these 5.
A resource with the minimum viable properties only has the `get` method defined.
When only `get` is available, the resource is useful for auditing state but can't
manage or change the state.

This sample uses the `echo` command to return a small jSON formatted output.
A single key value pair of `return` and `hello, world` provides a minimum viable output
for DSC to function and return the "actualState" of a resource.

Test the DSC resource using the `dsc` command with the `resource` parameters.

First, make sure the path for the resource project is in the `PATH` environment variable.

```sh
export PATH=$PATH':<full path to your project folder'
```

Next, run the `dsc resource list` command an observe that `dsc` has found the resource.

```sh
dsc resource list sh.Example/helloworld
```

The output should include the resource name and version.

```sh
Type                   Version  Requires  Description
-----------------------------------------------------
sh.Example/helloworld  0.1.0
```

Run the `dsc` command to test the DSC Resource.

```sh
dsc resource get --resource sh.Example/helloworld
```

Expect the following output.

```yaml
actualState:
  return: hello, world
```

Add the `--f` parameter and observe the output in JSON format as well.

```sh
dsc --format pretty-json resource get --resource sh.Example/helloworld
```

Expect the following output.

```json
{
  "actualState": {
    "return": "hello, world"
  }
}
```

The state in this sample is only for the sake of demonstration.
In the next example, we add functional script that evaluates contents of a file.
