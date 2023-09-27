---
title:  Step 4 - Add metadata to the shell script DSC Resource
weight: 1
dscs:
  menu_title: 4. Add shell script metadata
---

In this step, we continue from [step 3](./3-parameters.md) by adding metadata to the DSC resource.

Adding metadata is a best practice. Review the optional properties and think about how you can make
the resource more securable and sharable.

Open a terminal and return to the project created in step 3, if you aren't already in the project
folder. Open the `.json` manifest file in your preferred text editor, such as `nano`.

```sh
cd ./dsc-sample-sh-helloworld
nano ./helloworld.dsc.resource.json
```

Update the file by adding the following list of properties.

- `description`: Human readable text that explains the intention of the resource.
- `tags`: Single-word strings to make the resource easier to find in a filtered list.

```json
{
    "$schema": "https://raw.githubusercontent.com/PowerShell/DSC/main/schemas/2023/08/bundled/resource/manifest.json",
    "type": "sh.Example/helloworld",
    "description": "Sample to demonstrate common practices in DSC Resource authoring.",
    "tags": [
      "Sample",
      "HelloWorld"
    ],
    "version": "0.1.0",
    "get": {
        "executable": "get.sh",
        "input": "env"
    },
    "set": {
        "executable": "set.sh",
        "input": "env"
    },
    "schema": {
        "embedded": {}
    }
}
```

Next, we add to the `schema` section. DSC uses the resource schema to validate input. The following
sample adds properties used in steps 2 and 3, including a description and type. Users working with
the resource benefit from schema details because DSC will validate input before running. The schema
is also used by language services in text editors to assist authors creating a configuration file.

By setting the `additionalProperties` field to `false`, we prevent input other than what is defined
by the schema.

```json
{
    "$schema": "https://raw.githubusercontent.com/PowerShell/DSC/main/schemas/2023/08/bundled/resource/manifest.json",
    "type": "sh.Example/helloworld",
    "description": "Sample to demonstrate common practices in DSC Resource authoring.",
    "tags": [
      "Sample",
      "HelloWorld"
    ],
    "version": "0.1.0",
    "get": {
        "executable": "get.sh",
        "input": "env"
    },
    "set": {
        "executable": "set.sh",
        "input": "env"
    },
    "schema": {
      "embedded": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "sh.Example/helloworld",
        "description": "Sample to demonstrate common practices in DSC Resource authoring.",
        "markdownDescription": "**Sample** to demonstrate common practices in DSC Resource authoring.",
        "type": "object",
        "required": ["contentMatch","path"],
        "properties": {
            "contentMatch": {
              "title": "Content to match",
              "description": "A string to search in the file such as \"my text\".",
              "markdownDescription": "A string to search in the file.\n\n*Note:If more than one instance is found, all instances are turned with no seperator.*", 
              "type": "string"
            },
            "path": {
              "title": "File path",
              "description": "File location such as /folder/file.",
              "markdownDescription": " Indicates the path to a file or folder represented in DOS, UNC, or Files System Hierarchy format. Should not be used for Internet locations.", 
              "type": "string"
            }
        },
        "additionalProperties": false
      }
    }
}
```

Now the resource provides more information to users. We validate the metadata by testing `list`
operations and by evaluating input that should fail.

```powershell
dsc resource list sh.Example/helloworld
``````

Expect the following output.

```sh
Type                   Version  Requires  Description
-----------------------------------------------------------------------------------------------------------
sh.Example/helloworld  0.1.0              Sample to demonstrate common practices in DSC Resource authoring.
```

The `list` operation now includes a "Description".

Finally, attempt to use input that we believe should cause an error.


```sh
'{"BADINPUT": "no-op","contentMatch": "hello, world","path": "/tmp/helloworld"}' | dsc resource get --resource sh.Example/helloworld
```

Expect the following output.

```sh
Error: Schema: Additional properties are not allowed ('BADINPUT' was unexpected)
NativeCommandExitException: Program "dsc" ended with non-zero exit code: 2.
```

You are well on your way to authoring DSC resources in shell scripts! There are many more features
of DSC to explore including configurations where you can use your custom resources through new
capabilities in DSC version 3.
