---
title:  Step 5 - Implement set functionality
weight: 5
dscs:
  menu_title: 5. Implement set
---

Up to this point, the DSC Resource has been primarily concerned with representing and getting the
current state of an instance. To be fully useful, it needs to be able to change a configuration file
to enforce the desired state.

## Define handlers for set subcommand

Open the `Program.cs` file and navigate to the last line in the main fuction where the return is defined `return rootCommand.InvokeAsync(args).Result;` just below the end of the `getCommand` Handler enter the following code

```csharp
	scopeOption, allOption, inputJSON);
	// above is end of getCommand.SetHandler
	setCommand.SetHandler(async (scopeValue, ensureValue, updateAutomaticallyValue, updateFrequencyValue, jsonConfig) =>
	{
		
	},
	scopeOption, ensureOption, updateAutomaticallyOption, updateFrequencyOption, inputJSON);
	#endregion
	return rootCommand.InvokeAsync(args).Result;
```

Unlike the getCommand handler we will need more information to set the configuration. Now we are passing in the `scopeOption`, `ensureOption`, `updateAutomaticallyOption`, `updateFrequencyOption` and `inputJSON`. These are used to instantiate our `TstoyConfig` object as a base.

```csharp
	setCommand.SetHandler(async (scopeValue, ensureValue, updateAutomaticallyValue, updateFrequencyValue, jsonConfig) =>
	{
		var config = new TstoyConfig
		{
			Ensure = ensureValue,
			Scope = scopeValue,
			UpdateAutomatically = updateAutomaticallyValue,
			UpdateFrequency = updateFrequencyValue
		};
	},
	scopeOption, ensureOption, updateAutomaticallyOption, updateFrequencyOption, inputJSON);
```

Recall in our getCommand handler we needed to read JSON from stdio or from the `--inputJSON` parameter. We will repeat the same actions here attempting to read the string if it is piped to the command and then attempt to Deserialize the config using our helper function `DeserializeConfig`  

Anything passed in as JSON takes precedence over the named parameters.  

```csharp
	    //... code from previous steps here

		if (Console.IsInputRedirected && string.IsNullOrEmpty(jsonConfig))
		{
			jsonConfig = Console.In.ReadToEnd();
		}
		
		if (jsonConfig != null)
		{
			var deserializedConfig = DeserializeConfig(jsonConfig);
			if (deserializedConfig != null)
			{
				config = deserializedConfig;
			}
			else
			{
				Console.WriteLine("Failed to deserialize config.");
				return;
			}
		}

		//... code from previous steps here
```

Finally in our `setCommand` handler we need to try and write the configuration to disk with our helper function `WriteConfig` (note: don't worry about the `WriteConfig` function we will write that next)

```csharp
		//... code from previous steps here
		try
		{
			await WriteConfig(config);
		}
		catch (Exception ex)
		{
			Console.WriteLine($"Error writing configuration: {ex.Message}");
		}
		//... code from previous steps here
```

## Define helper function WriteConfig

While for our GetConfig helper function we only required the `scope` value, for our WriteConfig we will need to know all values of the Config. As a Result we will be passing the `TstoyConfig` object to our function.

Start the signature of the function in the following way. This should be outside the main function below the `GetConfig` helper function.

```csharp
    internal static async Task WriteConfig(TstoyConfig inputConfig)
    {
        
    }
    #endregion
```

Before writing the configuration we should ensure that the object passed in is not empty. This will save us from all sorts of issues in the future.

```csharp
    internal static async Task WriteConfig(TstoyConfig inputConfig)
    {
		if (inputConfig.Scope != null)
        {
            
        }
        else
        {
            throw new InvalidOperationException("config is empty");
        }
	}
    #endregion
```

Inside our `if` block we may now start defining some required variables. We need the `scopeOfConfig` so we can get the correct configuration to update with `GetConfigPath`. 

After that we have some options we need to pass to our Serialization functions to match what is being done by the `gotstoy` DSC Resource. 

```csharp
		if (inputConfig.Scope != null)
        {

			string scopeOfConfig = inputConfig.Scope;
            string configPath = GetConfigPath(scopeOfConfig);
            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true,
                WriteIndented = true
            };
		}
```

For the `Ensure` option we really only have two options either create or delete the file. If we want to ensure the file is absent then we should delte it only if the `FileExists`.

```csharp
	// inside the 'if (inputConfig.Scope != null)'
		if (inputConfig.Ensure == "present")
		{
			// We will fill this in during the next steps
		}
		else
		{
			if (FileExists(configPath))
			{
				File.Delete(configPath);
			}
		}
```

For our file creation we have a different JSON object defined for the file structure since this differes from the JSON object we have been returning to our console. For this we defined our `fileContent` variable.

If the `FileExists` for the configuration we are updating we will attempt to `DeserializeConfigFile` from disk and update the file content. If the file doesn't exists we will start assigning the desired values 

```csharp
		if (inputConfig.Ensure == "present")
		{
			TstoyFile fileContent = new TstoyFile { };

			if (FileExists(configPath))
			{
				try
				{
					fileContent = DeserializeConfigFile(configPath);
				}
				catch (Exception ex)
				{
					Console.WriteLine($"Error deserializing configuration file: {ex.Message}");
				}

				if (fileContent.Updates != null)
				{
					if (fileContent.Updates.Automatic != inputConfig.UpdateAutomatically)
						fileContent.Updates.Automatic = inputConfig.UpdateAutomatically;

					if (fileContent.Updates.CheckFrequency != inputConfig.UpdateFrequency)
						fileContent.Updates.CheckFrequency = inputConfig.UpdateFrequency;
				}
			}
			else
			{
				TstoyFileUpdates updateValues = new TstoyFileUpdates
				{
					Automatic = inputConfig.UpdateAutomatically,
					CheckFrequency = inputConfig.UpdateFrequency
				};
				if (TstoyFileUpdates.IsValueNotNull(updateValues))
					fileContent.Updates = updateValues;
				else
					fileContent.Updates = null;
			}
		}
```

At this point we should have a fully formed `TstoyFile` object we may attempt to write to disk. For convenince we will create the directories if they don't currently exist.

Before writing this file to disk we need to try and serialize the object to JSON.

```csharp
		if (inputConfig.Ensure == "present")
		{
			//... code from previous steps here
			try
			{
				Directory.CreateDirectory(Path.GetDirectoryName(configPath));

				await using FileStream createStream = File.Create(configPath);
				await JsonSerializer.SerializeAsync<TstoyFile>(createStream, fileContent);
			}
			catch (Exception ex)
			{
				Console.WriteLine($"Error writing configuration file: {ex.Message}");
			}
		}
```

Finally, since we will need to return the JSON config to DSC we are going to Serialize the inputConfig so we can return this to the shell. 

```csharp
	// inside the 'if (inputConfig.Scope != null)'
		try
		{
			string configOutput = JsonSerializer.Serialize<TstoyConfig>(inputConfig);
			Console.WriteLine(configOutput);
		}
		catch (Exception ex)
		{
			Console.WriteLine($"Error serializing configuration: {ex.Message}");
		}
```

Your `Program.cs` should now include the following lines

```csharp
	// lines above removed for readability
        	scopeOption, allOption, inputJSON);
		
		setCommand.SetHandler(async (scopeValue, ensureValue, updateAutomaticallyValue, updateFrequencyValue, jsonConfig) =>
        {
            var config = new TstoyConfig
            {
                Ensure = ensureValue,
                Scope = scopeValue,
                UpdateAutomatically = updateAutomaticallyValue,
                UpdateFrequency = updateFrequencyValue
            };

            if (Console.IsInputRedirected && string.IsNullOrEmpty(jsonConfig))
            {
                jsonConfig = Console.In.ReadToEnd();
            }
            
            if (jsonConfig != null)
            {
                var deserializedConfig = DeserializeConfig(jsonConfig);
                if (deserializedConfig != null)
                {
                    config = deserializedConfig;
                }
                else
                {
                    Console.WriteLine("Failed to deserialize config.");
                    return;
                }
            }

            try
            {
                await WriteConfig(config);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error writing configuration: {ex.Message}");
            }
        },
        scopeOption, ensureOption, updateAutomaticallyOption, updateFrequencyOption, inputJSON);
        #endregion

		return rootCommand.InvokeAsync(args).Result;
    }

	#region Helper Functions
	// lines removed for readability
	internal static async Task WriteConfig(TstoyConfig inputConfig)
    {
        if (inputConfig.Scope != null)
        {
            string scopeOfConfig = inputConfig.Scope;
            string configPath = GetConfigPath(scopeOfConfig);
            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true,
                WriteIndented = true
            };

            if (inputConfig.Ensure == "present")
            {
                TstoyFile fileContent = new TstoyFile { };

                if (FileExists(configPath))
                {
                    try
                    {
                        fileContent = DeserializeConfigFile(configPath);
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error deserializing configuration file: {ex.Message}");
                    }

                    if (fileContent.Updates != null)
                    {
                        if (fileContent.Updates.Automatic != inputConfig.UpdateAutomatically)
                            fileContent.Updates.Automatic = inputConfig.UpdateAutomatically;

                        if (fileContent.Updates.CheckFrequency != inputConfig.UpdateFrequency)
                            fileContent.Updates.CheckFrequency = inputConfig.UpdateFrequency;
                    }
                }
                else
                {
                    TstoyFileUpdates updateValues = new TstoyFileUpdates
                    {
                        Automatic = inputConfig.UpdateAutomatically,
                        CheckFrequency = inputConfig.UpdateFrequency
                    };
                    if (TstoyFileUpdates.IsValueNotNull(updateValues))
                        fileContent.Updates = updateValues;
                    else
                        fileContent.Updates = null;

                }
                try
                {
                    Directory.CreateDirectory(Path.GetDirectoryName(configPath));

                    await using FileStream createStream = File.Create(configPath);
                    await JsonSerializer.SerializeAsync<TstoyFile>(createStream, fileContent);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error writing configuration file: {ex.Message}");
                }
            }
            else
            {
                if (FileExists(configPath))
                {
                    File.Delete(configPath);
                }
            }

            try
            {
                string configOutput = JsonSerializer.Serialize<TstoyConfig>(inputConfig);
                Console.WriteLine(configOutput);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error serializing configuration: {ex.Message}");
            }
        }
        else
        {
            throw new InvalidOperationException("config is empty");
        }
    }
    #endregion
}
```


## Verify behavior

With the set command fully implemented, you can verify the behavior:

1. Show TSToy's configuration information before changing any state.

   ```sh
   tstoy show
   ```

   ```Output
   Default configuration: {
     "Updates": {
       "Automatic": false,
       "CheckFrequency": 90
     }
   }
   Machine configuration: {}
   User configuration: {}
   Final configuration: {
     "Updates": {
       "Automatic": false,
       "CheckFrequency": 90
     }
   }
   ```

1. Run the `get` command to see how the DSC Resource reports on current state:

   ```sh
   dotnet run get --scope machine
   ```

   ```json
   {"ensure":"absent","scope":"machine"}
   ```

1. Enforce the desired state with the `set` command.

   ```sh
   dotnet run set --scope machine --ensure present 
   ```

   ```json
   {"ensure":"present","scope":"machine"}
   ```

1. Verify that the output from the `set` command matches the output from `get` after enforcing the
   desired state.

   ```sh
   dotnet run get --scope machine
   ```

   ```json
   {"ensure":"present","scope":"machine"}
   ```

1. Use the `tstoy show` command to see how the configuration changes affected TSToy.

   ```sh
   tstoy show --only machine,final
   ```

   ```Output
	Machine configuration: {
	"Updates": {
		"Automatic": false
	}
	}
	Final configuration: {
	"Updates": {
		"Automatic": false,
		"CheckFrequency": 90
	}
	}
   ```

1. Enforce desired state for the user-scope configuration file.

   ```sh
   '{
       "scope": "user",
       "ensure": "present",
       "updateAutomatically": true,
       "updateFrequency": 45
   }' | dotnet run set
   ```

   ```json
   {"ensure":"present","scope":"user","updateAutomatically":true,"updateFrequency":45}
   ```

1. Use the `tstoy show` command to see how the configuration changes affected TSToy.

   ```sh
   tstoy show
   ```

   ```Output
	Default configuration: {
	"Updates": {
		"Automatic": false,
		"CheckFrequency": 90
	}
	}
	Machine configuration: {
	"Updates": {
		"Automatic": false
	}
	}
	User configuration: {
	"Updates": {
		"Automatic": true,
		"CheckFrequency": 45
	}
	}
	Final configuration: {
	"Updates": {
		"Automatic": true,
		"CheckFrequency": 45
	}
	}
   ```
