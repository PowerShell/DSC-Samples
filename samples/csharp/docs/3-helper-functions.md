---
title:  Step 3 - Helper Functions
weight: 3
dscs:
  menu_title: 3. Helper Functions
---

Now that we have defined the structure of the data we will need for our resource 
there are some helper functions that we need to define.

## Define FileExists Function

The tstoy application needs to be available in our `PATH` for the DSC resource to work additionally  
the DSC Resource is needs to be able to read and write the defined configuration path. To this end  
we should define a function to help us validate if a file exists.

Open the `Program.cs` file and after the closing `}` for the `main` function enter the following code:  

```csharp

    internal static bool FileExists(string fileName)
    {
        if (File.Exists(fileName))
            return true;

        var pathValue = Environment.GetEnvironmentVariable("PATH");
        if (!string.IsNullOrEmpty(pathValue))
        {
            foreach (var path in pathValue.Split(Path.PathSeparator))
            {
                if (File.Exists(Path.Combine(path, fileName)))
                    return true;
            }
        }
        return false;
    }

```


## Define DeserializeConfig and DeserializeConfigFile Function

Since we will be reading JSON from our application and from disk we need a consistent way to Deserialize 
The data to objects we may use in our get and set functions we will define later.
The `TstoyConfig` represents all fields (`Ensure`, `Scope`, `UpdateAutomatically`, and `UpdateFrequency`)
While `TstoyFile` represents the fields written to disk (`UpdateAutomatically` and `UpdateFrequency`)
Read more about Deserialization here [How to read JSON as .NET objects (deserialize)][01]

```csharp

    internal static TstoyConfig DeserializeConfig(string configText)
    {
        var options = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };
        TstoyConfig config = JsonSerializer.Deserialize<TstoyConfig>(configText, options)!;
        return config;
    }

    internal static TstoyFile DeserializeConfigFile(string configPath)
    {
        var options = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };
        var fileLines = File.ReadAllText(configPath);
        TstoyFile fileContent = JsonSerializer.Deserialize<TstoyFile>(fileLines, options)!;
        return fileContent;
    }
```

when adding the above functions you will likely need to add the following statement at the top of the file.

```csharp
using System.Text.Json;
```

## Define the GetConfigPath Function

The tstoy command outputs the path for the `user` and `machine` configuration using the commands  
`show path`. Since these may change in the future we want to ensure the resource may dynamically  
call the function to retreive the current path for these configurations. 

As a result we need to define a function to execute tstoy with the desired parameters and return
the path as a string.

First at the top of the file we need to declare a new namespace for `System.Diagnostics`
The top of `Program.cs` should look like this:

```csharp
using System.CommandLine;
using System.Text.Json;
using System.Diagnostics;
```

Further down below the `DeserializeConfigFile` function define the `GetConfigPath` Function.
This should still be outside the `Main` function

```csharp
    internal static string GetConfigPath(string scopeOfConfig)
    {
        var options = new HashSet<string> { "user", "machine" };
        string commandArguments(string scope) => options.Contains(scope) ? $" show path {scope}" : " show path";

        using var p = new Process
        {
            StartInfo = new ProcessStartInfo
            {
                FileName = "tstoy.exe",
                WindowStyle = ProcessWindowStyle.Hidden,
                Arguments = commandArguments(scopeOfConfig),
                UseShellExecute = false,
                RedirectStandardOutput = true
            }
        };
        try
        {
            p.Start();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error starting process: {ex.Message}");
        }

        var value = p.StandardOutput.ReadToEnd().Trim();
        p.WaitForExit();
        return value;
    }
```

At this point your `Program.cs` should look like the following:

```csharp
using System.CommandLine;
using System.Text.Json;
using System.Diagnostics;

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

    #region Helper Functions
    internal static bool FileExists(string fileName)
    {
        if (File.Exists(fileName))
            return true;

        var pathValue = Environment.GetEnvironmentVariable("PATH");
        if (!string.IsNullOrEmpty(pathValue))
        {
            foreach (var path in pathValue.Split(Path.PathSeparator))
            {
                if (File.Exists(Path.Combine(path, fileName)))
                    return true;
            }
        }
        return false;
    }
    internal static TstoyConfig DeserializeConfig(string configText)
    {
        var options = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };
        TstoyConfig config = JsonSerializer.Deserialize<TstoyConfig>(configText, options)!;
        return config;
    }

    internal static TstoyFile DeserializeConfigFile(string configPath)
    {
        var options = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true
        };
        var fileLines = File.ReadAllText(configPath);
        TstoyFile fileContent = JsonSerializer.Deserialize<TstoyFile>(fileLines, options)!;
        return fileContent;
    }
        internal static string GetConfigPath(string scopeOfConfig)
    {
        var options = new HashSet<string> { "user", "machine" };
        string commandArguments(string scope) => options.Contains(scope) ? $" show path {scope}" : " show path";

        using var p = new Process
        {
            StartInfo = new ProcessStartInfo
            {
                FileName = "tstoy.exe",
                WindowStyle = ProcessWindowStyle.Hidden,
                Arguments = commandArguments(scopeOfConfig),
                UseShellExecute = false,
                RedirectStandardOutput = true
            }
        };
        try
        {
            p.Start();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error starting process: {ex.Message}");
        }

        var value = p.StandardOutput.ReadToEnd().Trim();
        p.WaitForExit();
        return value;
    }
    #endregion
}
```

The DSC Resource should compile and now we may move on to writing our Get subcommand


[01]: https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/deserialization