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
instead of trying to generate the paths itself.

## Define get helper functions and methods { toc_md="Define `get` helpers" }

Open the `config/config.go` file. In it, add the `getAppConfigPath` function. It should take a
`Scope` value as input and return a string and error.

```go
func getAppConfigPath(s Scope) (string, error) {
	args := []string{"show", "path", s.String()}

	output, err := exec.Command("tstoy", args...).Output()
	if err != nil {
		return "", err
	}

	// We need to trim trailing whitespace automatically emitted for the path.
	path := string(output)
	path = strings.Trim(path, "\n")
	path = strings.Trim(path, "\r")

	return path, nil
}
```

The function generates the arguments to send to `tstoy` and calls the command.

Next, update the `Settings` struct to include a private field for the configuration path and
implement the public `GetConfigPath` function to retrieve the path for the instance of the
configuration file.

```go
type Settings struct {
	Ensure              Ensure    `json:"ensure,omitempty"`
	Scope               Scope     `json:"scope,omitempty"`
	UpdateAutomatically *bool     `json:"updateAutomatically,omitempty"`
	UpdateFrequency     Frequency `json:"updateFrequency,omitempty"`
	configPath          string
}

func (s *Settings) GetConfigPath() (string, error) {
	if s.configPath == "" {
		path, err := getAppConfigPath(s.Scope)
		if err != nil {
			return "", err
		}
		s.configPath = path
	}

	return s.configPath, nil
}
```

The `GetConfigPath` function reduces the number of calls the DSC Resource needs to make to the
application when you implement the `set` command.

Now that the DSC Resource can find the correct path, it needs to be able to retrieve settings from
the configuration file. You need to implement two more private functions:

1. `getAppConfigMap` to retrieve the configuration file settings as a generic `map[string]any`
   object.
1. `getAppConfigSettings` to convert the generic map into a `Settings` instance.

First, implement `getAppConfigMap` to read the configuration file and unmarshal the JSON.

```go
func getAppConfigMap(path string) (map[string]any, error) {
	var config map[string]any

	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	err = json.Unmarshal(data, &config)
	return config, err
}
```

Next, implement `getAppConfigSettings` to convert the map into a `Settings` instance.

```go
func getAppConfigSettings(scope Scope, config map[string]any) (Settings, error) {
	// ensure the map keys are all strings.
	maps.IntfaceKeysToStrings(config)

	// Since we found the config, we know the scope and ensure state.
	settings := Settings{
		Scope:  scope,
		Ensure: EnsurePresent,
	}

	// Check for the update settings
	updates, ok := config["updates"]
	if ok {
		for key, value := range updates.(map[string]any) {
			switch key {
			case "automatic":
				auto := value.(bool)
				settings.UpdateAutomatically = &auto
			case "checkFrequency":
				intValue := int(value.(float64))
				frequency := Frequency(intValue)
				settings.UpdateFrequency = frequency
			}
		}
	}

	return settings, nil
}
```

With those private functions implemented, you can add methods to `Settings` for retrieving the map
of settings and the actual state.

```go
func (s *Settings) GetConfigMap() (map[string]any, error) {
	path, err := s.GetConfigPath()
	if err != nil {
		return nil, err
	}
	return getAppConfigMap(path)
}

func (s *Settings) GetConfigSettings() (Settings, error) {
	config, err := s.GetConfigMap()
	if errors.Is(err, os.ErrNotExist) {
		return Settings{
			Ensure: EnsureAbsent,
			Scope:  s.Scope,
		}, nil
	} else if err != nil {
		return Settings{}, err
	}

	return getAppConfigSettings(s.Scope, config)
}
```

## Update getState to return one instance { toc_md="Support returning one instance" }

Open the `cmd/get.go` file and return to the `getState` function. Instead of printing the inputs,
the function should:

1. Create an instance of `Settings` from the inputs.
1. Validate the instance.
1. Get the current settings from the system.
1. Print the results.

```go
func getState(cmd *cobra.Command, args []string) error {
	// Only the scope is used when retrieving current state.
	s := config.Settings{
		Scope: targetScope,
	}

	err := s.Validate()
	if err != nil {
		return fmt.Errorf("can't get settings; %s", err)
	}

	config, err := s.GetConfigSettings()
	if err != nil {
		return fmt.Errorf("failed to get settings; %s", err)
	}

	return config.Print()
}
```

Now you can run the updated command to see how it works:

```sh
go run ./main.go get
go run ./main.go get --scope machine
go run ./main.go get --inputJSON '{ "scope": "user" }'
'{ "scope": "user" }' | go run ./main.go get --scope machine
go run ./main.go get --scope machine --ensure present
```

```Output
Error: can't get settings; the Scope setting isn't defined. Must define a Scope
for Settings

{"ensure":"absent","scope":"machine"}

{"ensure":"absent","scope":"user"}

{"ensure":"absent","scope":"machine"}

{"ensure":"absent","scope":"machine"}
```

## Update getState to return all instances { toc_md="Support returning all instances" }

DSC Resources may optionally return the current state for every manageable instance. This is
convenient for users who want to get information about a resource with a single command. It's also
useful for higher-order tools that can cache current state.

To add this functionality, add the `all` variable as a boolean in `cmd/get.go`.

```go
var all bool
```

In the `init` function, add `--all` as a new flag for the command.

```go
func init() {
	rootCmd.AddCommand(getCmd)
	getCmd.Flags().BoolVar(
		&all,
		"all",
		false,
		"Get the configurations for all scopes.",
	)
}
```

Update the `getState` function to handle the new flag by making the behavior loop. The function
should handle a few different cases for the input:

- If the `--all` flag is used, the function should return the instance for both scopes.
- If the `--targetScope` flag is used, the function should return the instance for that scope.
- If `--targetScope` is used with a JSON blob from `--inputJSON` or stdin, the JSON value should be
  ignored.
- If the command receives a JSON blob from `--inputJSON` or stdin without the `--targetScope` flag,
  the command should use that value.

```go
func getState(cmd *cobra.Command, args []string) error {
	list := []config.Settings{}
	if all {
		list = append(
			list,
			config.Settings{Scope: config.ScopeMachine},
			config.Settings{Scope: config.ScopeUser},
		)
	} else if targetScope != config.ScopeUndefined {
		// explicit --scope overrides JSON
		list = append(list, config.Settings{Scope: targetScope})
	} else if inputJSON != nil {
		list = append(list, *inputJSON)
	} else {
		// fails but with consistent messaging
		list = append(list, config.Settings{Scope: targetScope})
	}

	for _, s := range list {

		err := s.Validate()
		if err != nil {
			return fmt.Errorf("can't get settings; %s", err)
		}

		config, err := s.GetConfigSettings()
		if err != nil {
			return fmt.Errorf("failed to get settings; %s", err)
		}

		err = config.Print()
		if err != nil {
			return err
		}
	}

	return nil
}
```

Run the updated command:

```sh
go run ./main.go get --all
go run ./main.go get --scope machine
go run ./main.go get --inputJSON '{"scope": "user"}'
go run ./main.go get --inputJSON '{"scope": "user"}' --scope machine
'{
    "scope":  "machine",
    "ensure": "present"
}' | go run ./main.go get
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
