using System.CommandLine;
using System.Diagnostics;
using System.Text.Json;

namespace csharptstoy;

class Program
{
    static async Task<int> Main(string[] args)
    {
        #region Options
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
        #endregion

        #region Commands
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
        #endregion

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