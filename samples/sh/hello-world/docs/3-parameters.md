---
title:  Step 3 - Add parameters to the shell script DSC Resource
weight: 1
dscs:
  menu_title: 3. Add shell script parameters
---

In this step, we continue from [step 2](./2-functional.md) by adding parameter input to the shell
scripts used by the DSC resource.

In this example, we pass key value pairs in JSON format to `dsc`. For each property, DSC creates an
environment variable in the process where the Resource runs the script.

Open a terminal and return to the project created in step 2, if you aren't already in the project
folder. Open the `.json` manifest file in your preferred text editor, such as `nano`.

```sh
cd ./dsc-sample-sh-helloworld
nano ./helloworld.dsc.resource.json
```

Update the file by adding the `input` property in the `get.sh` section.

```json
{
    "manifestVersion": "1.0",
    "type": "sh.Example/helloworld",
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

After you make the changes, save the file and close the editor.

Next, open `get.sh` in your preferred text editor, such as `nano`.

```sh
nano ./get.sh
```

Replace `'hello, world'` with `"$contentMatch"` and replace `/tmp/helloworld` with `"$path"`.

```sh
#!/usr/bin/bash
[ -f "$path" ] || _exists=false && match=$(grep "$contentMatch" "$path")
printf "{\"contentMatch\":\"$match\",\"path\":\"$path\",\"_exists\":$_exists}"
```

After you have pasted into the editor, save and close the file.

The changes to the file replace the static strings with variables. When the Resource executes, DSC
sets the variables from the JSON input.

Next, open `set.sh` in your preferred text editor, such as `nano`.

```sh
nano ./set.sh
```

Replace `'hello, world'` with `"$contentMatch"` and replace `/tmp/helloworld` with `"$path"`.

```sh
#!/usr/bin/bash
printf "$contentMatch" >> "$path"
```

After you have pasted into the editor, save and close the file.

Test the DSC resource using the `dsc` command with the `resource` parameters.

First, make sure the path for the resource project is in the `PATH` environment variable. If you're
in the same terminal session from step 2, you don't need to do this again.

```sh
export PATH=$PATH':<full path to your project folder'
```

If you created the test file in steps 1 or 2, run this command to delete the file.

```sh
rm /tmp/helloworld
```

Next, run the `dsc` command to test the DSC Resource.

```sh
'{"contentMatch": "hello, world","path": "/tmp/helloworld"}' | dsc resource get --resource sh.Example/helloworld
```

Expect the following output.

```yaml
actualState:
  contentMatch: ''
  path: /tmp/helloworld
  _exists: false
```

Now, test DSC writing the file using the `set` method.

```sh
'{"contentMatch": "hello, world","path": "/tmp/helloworld"}' | dsc resource set --resource sh.Example/helloworld
```

Expect the following output.

```yaml
beforeState:
  contentMatch: ''
  path: /tmp/helloworld
afterState:
  contentMatch: hello, world
  path: /tmp/helloworld
  _exists: true
changedProperties:
- contentMatch
```

The state of `contentMatch` changed because the file now has the text `hello, world`. You can
experiment with modifying the JSON input to check other paths for text strings and appending text
to a test file.

In the next example, we add metadata to the DSC Resource.
