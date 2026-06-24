---
title:  Step 2 - Define the configuration settings
weight: 2
dscs:
  menu_title: 2. Define settings
---

## Create the data structure for the json configuration 

Create the `json.cs` file in the project root. This file defines the  
configuration types of the DSC Resource. It will also be used when we  
serialize our objects to a file. Learn more at [How to write .NET objects as JSON (serialize)][01] 

```sh
dotnet new class -n json
```

Replace the default contents of the `json.cs` file with the following content:  

```csharp
using System.Text.Json.Serialization;
namespace csharptstoy;
```

Now you will define the structure of the the Tstoy Configuration File.  
The configuration file should only contain the `updates` section.
The `Ensure` option for tstoy is represented by the file being absent or present
and the `Scope` option for tstoy is represented by the path of the config file.

C# desires that Public properties be uppercase, but tstoy's configuration is case  
sensitive and requires us to overwrite the property name with `[JsonPropertyName("updates")]` 

Below the `namespace` decleration enter the following class:

```csharp
/// <summary>
/// Represents the Tstoy file
/// </summary>
public class TstoyFile
{
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    [JsonPropertyName("updates")]
    public TstoyFileUpdates? Updates { get; set; }
}
```

In C# nested JSON objects need to be represented by other classes, so we need to define the  
`TstoyFileUpdates` class. We also are going to define a `IsValueNotNull` method as well to do a quick  
comparison of the properties that may be defined.

Enter the following below the `TstoyFile` class:

```csharp
/// <summary>
/// Represents the updates in a Tstoy file
/// </summary>
public class TstoyFileUpdates
{
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingDefault)]
    [JsonPropertyName("automatic")]
    public bool Automatic { get; set; }
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingDefault)]
    [JsonPropertyName("checkFrequency")]
    public int CheckFrequency { get; set; }

    /// <summary>
    /// Checks if the TstoyFileUpdates object is not null.
    /// </summary>
    /// <param name="tstoyProperty">The TstoyFileUpdates object to check.</param>
    /// <returns>True if the object is not null, false otherwise.</returns>
    public static bool IsValueNotNull(TstoyFileUpdates tstoyProperty) => tstoyProperty != null;
}
```

Finally since the we need to read and return the current state of all fields `Ensure`, `Scope`,  
`UpdateAutomatically`, and `UpdateFrequency` to DSC in JSON format we should declare a  
Class which represents this object. There are more advanced ways to write custom contracts in  
C# for JSON, but this duplication of items will server our current purposes.

When using the `[JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingDefault)]` attribute we will  
ignore any "default" or undefined values. [How to ignore properties with System.Text.Json][02]

Enter the following Class below `TstoyFileUpdates`

```csharp
/// <summary>
/// Represents the Tstoy configuration
/// </summary>
public class TstoyConfig
{
    [JsonPropertyName("ensure")]
    public string? Ensure { get; set; }

    [JsonPropertyName("scope")]
    public string? Scope { get; set; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingDefault)]
    [JsonPropertyName("updateAutomatically")]
    public bool UpdateAutomatically { get; set; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingDefault)]
    [JsonPropertyName("updateFrequency")]
    public int UpdateFrequency{ get; set; }
}
```

Now that we have these data structures defined we may move on to handling input to the resource

[01]: https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/how-to
[02]: https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/ignore-properties