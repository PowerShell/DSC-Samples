---
title:  Step 2 - Add functional shell scripts to the DSC Resource
weight: 1
dscs:
  menu_title: 2. Add functional shell script
---

In this step, we continue from [step 1](./1-mvp.md) by adding shell scripts as external files used
by the DSC resource. In each script file, we add shell commands. The first script checks the
contents of a file. Next, we add the ability to set the contents of a file.

In this example, the shell scripts _are_ the executable command for each method. The intention is
to develop and test code using the tool ecosystem for the language used by the DSC Resource instead
of embedding the code in JSON.

Open a terminal and return to the project created in step 1. Open the `.json` manifest file in your
preferred text editor, such as `nano`.

```sh
cd ./dsc-sample-sh-helloworld
nano ./helloworld.dsc.resource.json
```

Update the file. Remove the `args` line and edit the `executable` line by replace the value with
`get.sh`.

```json
{
    "$schema": "https://raw.githubusercontent.com/PowerShell/DSC/main/schemas/2023/08/bundled/resource/manifest.json",
    "type": "sh.Example/helloworld",
    "version": "0.1.0",
    "get": {
        "executable": "get.sh"
    },
    "schema": {
        "embedded": {}
    }
}
```

Next, add a section named `set`. Within the new section, add an `executable` property with a value
of `set.sh`. Also add a property `input` with value `env`. Although we aren't using any input in
this sample, `dsc` requires the property.

```json
{
    "$schema": "https://raw.githubusercontent.com/PowerShell/DSC/main/schemas/2023/08/bundled/resource/manifest.json",
    "type": "sh.Example/helloworld",
    "version": "0.1.0",
    "get": {
        "executable": "get.sh"
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

After you make the changes, save the file and close the editor.

In the sample from step 1, the manifest referenced script arguments provided "inline" as values in
the JSON properties. After making the preceding changes, the JSON file refers to external shell
script files. Now, we create the shell script files.

Create and open `get.sh` in your preferred text editor, such as `nano`.

```sh
nano ./get.sh
```

Copy and paste the following text into the file.

```sh
#!/usr/bin/env bash
[ -f "/tmp/helloworld" ] || _exists=false && match=$(grep "hello, world" "/tmp/helloworld")
printf "{\"contentMatch\":\"$match\",\"path\":\"/tmp/helloworld\",\"_exists\":$_exists}"
```

After you have pasted into the editor, save and close the file.

The shell script `get.sh` first uses the "shebang" character sequence to define the executable to
run the script environment. Next, the script checks if the file exists.

The turnery operators `||` and `&&` run the appropriate commands. If the file doesn't exist then
the `_exists` variable is `false`. If the file does exist, then the `match` variable is the output
of `grep`. The `grep` command evaluates the file at path `/tmp/helloworld` for all instances of
text that match `hello, world`. If the file exists and it has at least one match for the text, The
`contentMatch` property provides evidence to display as `actualState`. The `dsc` command expects
the JSON output from DSC Resources so as a final step, the script outputs a key value pair in JSON
format.

The third property in the JSON output is `_exists`. The property named `_exists` is a "well known"
name that any resource can output. The intention is to standardize similar behaviors across
resources. In this case, the property makes the output more intuitive by showing that the file at
the `path` location either does or doesn't exist.

Next, create and open `set.sh` in your preferred text editor, such as `nano`.

```sh
nano ./set.sh
```

Copy and paste the following text into the file.

```sh
#!/usr/bin/bash
printf 'hello, world' >> /tmp/helloworld
```

After you have pasted into the editor, save and close the file.

The `>>` character sequence appends text to the file. If you want to replace all text, use the `>`
character instead.

Now you are ready to test the DSC resource using the `dsc` command with the `resource` parameters.

First, make sure the path for the resource project is in the `PATH` environment variable.

```sh
export PATH=$PATH':<full path to your project folder'
```

Next, run the `dsc` command to test your changes to the DSC Resource.

```sh
dsc resource get --resource sh.Example/helloworld
```

Expect the following output.

```yaml
actualState:
  contentMatch: ''
  path: ''
  _exists: false
```

Now, test DSC writing the file using the `set` method. Even though we're not using parameters yet,
DSC requires input for `set` so we pass an empty JSON.

```sh
{}| dsc resource set --resource sh.Example/helloworld
```

We don't need to run `get` again manually. The output from `set` indicates the state has changed.

Expect the following output.

```sh
beforeState:
  contentMatch: ''
afterState:
  contentMatch: 'hello, world'
changedProperties:
- contentMatch
```

The state of `contentMatch` changed because the file now has the text `hello, world`. In the next
example, we add parameters to input `contentMatch` and `path` at run time.
