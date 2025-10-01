---
title:  Step 1 - Create the DSC Resource
weight: 1
dscs:
  menu_title: 1. Create the resource
---

After installing the prequsities of VS Code, ms-dotnettools.csdevkit and .net 8  
Navigate to development folder in a system shell and create a new project  
```sh
mkdir ~\dev
cd ~\dev
dotnet new console -n csharptstoy
```

Open the newly created csharptstoy folder in VS Code this should create a `.sln` file for your project  

In this tutorial, you'll be creating a DSC Resource with [System.Commandline][01]. System.Commandline helps you create a  
command line application in C#. It handles argument parsing, setting flags, shell completions, and autogenerates help.  

Launch the integrated terminal in VS Code and Use the following command to install `System.Commandline`.  
Note: This library is still in preview but is stable enough for our purpose here.  

```sh
dotnet add package System.Commandline --prerelease
```

.net by nature compiles an application that is dynamically linked at runtime against the the target runtime.  
This requires the .net runtime be installed on the system where you are using your resource.  
Since this may not be possible in all of our Iot edge deployments we will make the resource selfcontained.  
This make the binary larger and does not require us to install the runtime on the target machine  

Open the `csharptstoy.csproj` file and add the following lines under the `<PropertyGroup>` tag.  

```xml
 <PropertyGroup>
    ...
    <SelfContained>true</SelfContained>
    <RuntimeIdentifier>win-x64</RuntimeIdentifier>
    <PublishSingleFile>true</PublishSingleFile>
    ...
</PropertyGroup>
```

Once you have done the steps above opne the `Program.cs` file and replace the contents with the following.  
This code block sets up the options (i.e `--scope`), rootcommand (`csharptstoy`), and subcommands (`get` and `set`)  

```c#
using System.CommandLine;

namespace csharptstoy;

class Program
{
    static async Task<int> Main(string[] args)
    {
        var ensureOption = new Option<string>(
            name: "--ensure",
            description: "Whether the configuration file should exist.",
            getDefaultValue: () => "present")
            .FromAmong(
                "present",
                "absent"
            );
        var inputJSON = new Option<string>(
            name: "--inputJSON",
            description: "Specify options as a JSON blob instead of using the scope, ensure, and update* flags.");
        var scopeOption = new Option<string>(
            name: "--scope",
            description: "The target scope for the configuration.")
            .FromAmong(
                "machine",
                "user"
            );
        var updateAutomaticallyOption = new Option<bool>(
            name: "--updateAutomatically",
            description: "Whether the configuration should set the app to automatically update.");
        var updateFrequencyOption = new Option<int>(
            name: "--updateFrequency",
            description: "How frequently the configuration should update, between 1 and 90 days inclusive.");

        var allOption = new Option<bool>(
            name: "--all",
            description: " Get the configurations for all scopes.");

        var rootCommand = new RootCommand("csharp DSC Resource for tstoy application");

        rootCommand.AddGlobalOption(scopeOption);
        rootCommand.AddGlobalOption(ensureOption);
        rootCommand.AddGlobalOption(updateAutomaticallyOption);
        rootCommand.AddGlobalOption(updateFrequencyOption);
        rootCommand.AddGlobalOption(inputJSON);

        var getCommand = new Command("get", "Gets the current state of a tstoy configuration file.")
        {
            allOption
        };

        var setCommand = new Command("set", "Sets a tstoy configuration file to the desired state.")
        {
        };

        rootCommand.AddCommand(getCommand);
        rootCommand.AddCommand(setCommand);

        return rootCommand.InvokeAsync(args).Result;
    }

}
```

Not that you have a basic layout of your resource you may run the following command from the VS Code  
integrated terminal to compile it.  

```sh
dotnet run
```

It should output the following text  

```text
Required command was not provided.

Description:
  csharp DSC Resource for tstoy application

Usage:
  csharptstoy [command] [options]

Options:
  --scope <machine|user>               The target scope for the configuration.
  --ensure <absent|present>            Whether the configuration file should exist. [default: present]
  --updateAutomatically                Whether the configuration should set the app to automatically update.
  --updateFrequency <updateFrequency>  How frequently the configuration should update, between 1 and 90 days inclusive.
  --inputJSON <inputJSON>              Specify options as a JSON blob instead of using the scope, ensure, and update* flags.
  --version                            Show version information
  -?, -h, --help                       Show help and usage information

Commands:
  get  Gets the current state of a tstoy configuration file.
  set  Sets a tstoy configuration file to the desired state.
```

With the command scaffolded, you need to understand the application the DSC Resource manages before  
you can implement the commands. By now, you should have read [About the TSToy application][02].

[01]: https://www.nuget.org/packages/System.CommandLine#readme-body-tab
[02]: /tstoy/about
