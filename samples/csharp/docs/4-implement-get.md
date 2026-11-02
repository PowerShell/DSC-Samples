---
title:  Step 4 - Implement get functionality
weight: 4
dscs:
  menu_title: 4. Implement get
---

To implement the get command, the DSC Resource needs to be able to find and marshal the settings
from a specific `tstoy` configuration file.

Recall from [About the TSToy application][01] that you can use the `tstoy show path` command to get
the full path to the applications configuration files. The DSC Resource can use those commands
instead of trying to generate the paths itself. Recall we wrote a helper function in the last section to do this for us. Now we can implement the read functions for the get command.

## Define handlers for get subcommand

Open the `Program.cs` file and navigate to the last line in the main fuction where the return is defined: `return rootCommand.InvokeAsync(args).Result;`

Just above this and below the line we added the set command we will implement the handler for our get command. Start with the structure below. We are passing in the `scopeOption`, `allOption` and `inputJSON` to the handler and are defining local variables. 

```csharp
	rootCommand.AddCommand(setCommand);

	getCommand.SetHandler(async (scopeValue, allValue, jsonConfig) =>
	{
		
	},
	scopeOption, allOption, inputJSON);

	return rootCommand.InvokeAsync(args).Result;

```

Next inside the handler we need to read the json from stdio or from the parameter `--inputJSON` to ensure that we caputre input either way. When DSC passes info to a resource it may pipe this instead of binding to the argument. 

We will then need to use our Deserialization helper function to convert the json to a .net object we may use.

```csharp

	getCommand.SetHandler(async (scopeValue, allValue, jsonConfig) =>
	{
		if (Console.IsInputRedirected && string.IsNullOrEmpty(jsonConfig))
		{
			jsonConfig = Console.In.ReadToEnd();
		}

		if (!string.IsNullOrEmpty(jsonConfig))
		{
			var deserializedConfig = DeserializeConfig(jsonConfig);
			if (string.IsNullOrEmpty(scopeValue) && !string.IsNullOrEmpty(deserializedConfig.Scope))
			{
				scopeValue = deserializedConfig.Scope;
			}
		}

	},
	scopeOption, allOption, inputJSON);
```

Once the config has been deserialized and we have the scope, we need to get the configuration. Either for all of the instances or for a specific scope. 

If `--all` is passed to the command we will have the `allOption` defined, but we need a way to iterate over both machine and user configuration. For this we will define a temporary variable listing all of the completions for the `scopeOption` 

Now for our logic if `--all` is provided we will loop over `tempOptions` and read each config, otherwise we will read the provided scope. (note: don't worry about the `ReadConfig` function we will write that next)

```csharp
	getCommand.SetHandler(async (scopeValue, allValue, jsonConfig) =>
	{
		//... code from previous step here
		var tempOptions = scopeOption.GetCompletions();
		
		if (allValue)
		{
			foreach (var tempOptionsValue in tempOptions)
			{
				string tempValue = tempOptionsValue.ToString();
				await ReadConfig(tempValue);
			}
		}
		else
		{
			if (!string.IsNullOrEmpty(scopeValue))
				await ReadConfig(scopeValue);
			else
				throw new InvalidOperationException("must provide a scope");
		}
		},
	scopeOption, allOption, inputJSON);
```

Now that we have the get handler defined we need to create the function that will actually read and return the config from disk.

For this function we will need to define this outside the `Main` function and near the helper functions below. Since we are calling the handlers with the `async` keyword we need to implement `async Task` functions.

Start the signature with the following:

```csharp
	// other helper functions above here...
    internal static async Task ReadConfig(string scopeOfConfig)
    {

    }
```

## Define helper function ReadConfig

For this function we used earlier in the handler we passed the `scope` of the config, using the scope we need to retrieve the path to the file. We will use our helper function `GetConfigPath` to determine this path and store it as a string.

Additionally we will need a `TstoyConfig` object so that we can represent the state of the config to DSC as JSON: `{"ensure":"absent","scope":"machine"}`

```csharp
    internal static async Task ReadConfig(string scopeOfConfig)
    {
		string configPath = GetConfigPath(scopeOfConfig);   
		var configValues = new TstoyConfig
        {
            Ensure = FileExists(configPath) ? "present" : "absent",
            Scope = scopeOfConfig
        };
	}
```

Now that we have the path of the configuration from `tstoy` we can do a quick check to see if the file exists with out helper function `FileExists`.

If the file exists we will want to try and Deserialize the config file using the helper function `DeserializeConfigFile`. Recall the file only contains information about updates, so if those values are present we will want to update the `configValues` object for presentation to DSC.

```csharp
    internal static async Task ReadConfig(string scopeOfConfig)
    {
		//... code from previous step here
        if (FileExists(configPath))
        {
            try
            {
                TstoyFile fileContent = DeserializeConfigFile(configPath);
                if (fileContent != null && TstoyFileUpdates.IsValueNotNull(fileContent.Updates))
                {
                    configValues.UpdateAutomatically = fileContent.Updates.Automatic;
                    configValues.UpdateFrequency = fileContent.Updates.CheckFrequency;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error deserializing configuration file: {ex.Message}");
            }
        }
	}
```

Finally in this ReadConfig we will need to take our `configValues` object and try to serialize it back to JSON so we may successfully pass it to DSC. 

```csharp
	internal static async Task ReadConfig(string scopeOfConfig)
    {
		//... code from previous step here
 		try
        {
            var configOutput = JsonSerializer.Serialize<TstoyConfig>(configValues);
            Console.WriteLine(configOutput);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error serializing configuration: {ex.Message}");
        }
	}
```

Now that we have the `ReadConfig` function defined and the getCommand handler configured we should be able to read the configuration.

One last section we should add in our `Main` function just above the `getCommand.SetHandler` section is an explicit check for tstoy. Up to know we have been assuming that it will be present, but we should ensure it is and fail early if it is missing.

```csharp
	if (!FileExists("tstoy.exe"))
		throw new InvalidOperationException("tstoy.exe not found");
	
	#region handlers
	getCommand.SetHandler(async (scopeValue, allValue, jsonConfig) =>
	//... code from previous steps here
```

Your `Program.cs` should now include the following lines

```csharp
		// lines above removed for readability
		rootCommand.AddCommand(setCommand);

        if (!FileExists("tstoy.exe"))
            throw new InvalidOperationException("tstoy.exe not found");

        #region handlers
        getCommand.SetHandler(async (scopeValue, allValue, jsonConfig) =>
            {
                var tempOptions = scopeOption.GetCompletions();
                if (Console.IsInputRedirected && string.IsNullOrEmpty(jsonConfig))
                {
                    jsonConfig = Console.In.ReadToEnd();
                }

                if (!string.IsNullOrEmpty(jsonConfig))
                {
                    var deserializedConfig = DeserializeConfig(jsonConfig);
                    if (string.IsNullOrEmpty(scopeValue) && !string.IsNullOrEmpty(deserializedConfig.Scope))
                    {
                        scopeValue = deserializedConfig.Scope;
                    }
                }

                if (allValue)
                {
                    foreach (var tempOptionsValue in tempOptions)
                    {
                        string tempValue = tempOptionsValue.ToString();
                        await ReadConfig(tempValue);
                    }
                }
                else
                {
                    if (!string.IsNullOrEmpty(scopeValue))
                        await ReadConfig(scopeValue);
                    else
                        throw new InvalidOperationException("must provide a scope");
                }
            },
            scopeOption, allOption, inputJSON);
		
		return rootCommand.InvokeAsync(args).Result;
    }

	#region Helper Functions
	// lines removed for readability 

	internal static async Task ReadConfig(string scopeOfConfig)
    {
        string configPath = GetConfigPath(scopeOfConfig);
        var configValues = new TstoyConfig
        {
            Ensure = FileExists(configPath) ? "present" : "absent",
            Scope = scopeOfConfig
        };

        if (FileExists(configPath))
        {
            try
            {
                TstoyFile fileContent = DeserializeConfigFile(configPath);
                if (fileContent != null && TstoyFileUpdates.IsValueNotNull(fileContent.Updates))
                {
                    configValues.UpdateAutomatically = fileContent.Updates.Automatic;
                    configValues.UpdateFrequency = fileContent.Updates.CheckFrequency;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error deserializing configuration file: {ex.Message}");
            }
        }

        try
        {
            var configOutput = JsonSerializer.Serialize<TstoyConfig>(configValues);
            Console.WriteLine(configOutput);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error serializing configuration: {ex.Message}");
        }

    }
	#endregion
}
```

## Test the get command

Test the DSC Resource now and Run the updated command:

```sh
dotnet run get --all
dotnet run get --scope machine
dotnet run get --inputJSON '{"scope": "user"}'
dotnet run get --inputJSON '{"scope": "user"}' --scope machine
'{
    "scope":  "machine",
    "ensure": "present"
}' | dotnet run get 
```

```Output
{"ensure":"absent","scope":"machine"}
{"ensure":"absent","scope":"user"}

{"ensure":"absent","scope":"machine"}

{"ensure":"absent","scope":"user"}

{"ensure":"absent","scope":"machine"}

{"ensure":"absent","scope":"machine"}
```

[01]: /tstoy/about
