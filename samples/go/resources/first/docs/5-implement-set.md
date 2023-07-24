---
title:  Step 5 - Implement set functionality
weight: 5
dscs:
  menu_title: 5. Implement set
---

Up to this point, the DSC Resource has been primarily concerned with representing and getting the
current state of an instance. To be fully useful, it needs to be able to change a configuration file
to enforce the desired state.

## Minimally implement set

Open the `cmd/set.go` file.

At the bottom of the file, create a new `setState` function that takes two parameters, a pointer to
`cobra.Command` and a slice of strings, and returns an error.

```go
func setState(cmd *cobra.Command, args []string) error {
	return nil
}
```

Replace the `Run` entry in the `setCmd` variable's definition with the `RunE` field set to the
`setState` function. Update the documentation for the command to be more specific to the DSC
Resource.

```go
var setCmd = &cobra.Command{
	Use:   "set",
	Short: "Sets a tstoy configuration file to the desired state.",
	Long: `The set command ensures that the tstoy configuration file for a
specific scope has the desired settings. It returns the updated settings state
as a JSON blob to stdout.`,
	RunE: setState,
}
```

Next, update the `setState` function to convert the inputs into an instance of `Settings`. For now,
the function should validate the desired state and print it.

```go
func setState(cmd *cobra.Command, args []string) error {
	enforcing := config.Settings{}

	if inputJSON != nil {
		enforcing = *inputJSON
	}
	if targetScope != config.ScopeUndefined {
		enforcing.Scope = targetScope
	}
	if targetEnsure != config.EnsureUndefined {
		enforcing.Ensure = targetEnsure
	}
	if rootCmd.PersistentFlags().Lookup("updateAutomatically").Changed {
		enforcing.UpdateAutomatically = &updateAutomatically
	}
	if updateFrequency != 0 {
		enforcing.UpdateFrequency = updateFrequency
	}

	err := enforcing.Validate()
	if err != nil {
		return fmt.Errorf("can't enforce settings; %s", err)
	}

	return enforcing.Print()
}
```

Verify the behavior for the set command.

```sh
go run ./main.go set --scope machine --ensure present --updateAutomatically=false

'{
    "scope": "user",
    "ensure": "present",
    "updateAutomatically": true,
    "updateFrequency": 45
}' | go run ./main.go set

'{
    "scope": "user",
    "ensure": "present",
    "updateAutomatically": true,
    "updateFrequency": 45
}' | go run ./main.go set --ensure absent
```

```Output
{"ensure":"present","scope":"machine","updateAutomatically":false}

{"ensure":"present","scope":"user","updateAutomatically":true,"updateFrequency":45}

{"ensure":"absent","scope":"user","updateAutomatically":true,"updateFrequency":45}
```

## Implement helper functions and methods for set { toc_md="Implement `set` helpers" }

At this point, the DSC Resource is able to validate the desired state. It needs to be able to
actually change the configuration files.

Open `config/config.go` and define an `Enforce` method for `Settings` that returns a pointer to an
instance of `Settings` and an error. It should:

1. Validate the settings.
1. Get the current settings for that scope.
1. Decide what it needs to do to enforce the desired state, if anything.

```go
func (s *Settings) Enforce() (*Settings, error) {
	err := s.Validate()
	if err != nil {
		return nil, err
	}

	current, err := s.GetConfigSettings()
	if err != nil {
		return nil, err
	}

	if s.Ensure == EnsureAbsent {
		// remove the config file
	}

	if current.Ensure == EnsureAbsent {
		// create the config file
	}

	// update the config file
	return s, nil
}
```

This shows that the method needs to handle three different change types for the configuration file:

1. It needs to remove the configuration file it's not supposed to exist.
1. It needs to create the configuration file when it's supposed to exist and doesn't exist.
1. It needs to update the configuration file when it's supposed to exist and does exist.

Remember that a DSC Resource should be idempotent, only making changes when required.

### Handle removing an instance

Implement the remove method first. It should take an instance of `Settings` as input and return
both a pointer to an instance of `Settings` and an error.

```go
func (s *Settings) remove(current Settings) (*Settings, error) {
	if current.Ensure == EnsureAbsent {
		return s, nil
	}

	// At this point, s.GetConfigPath() has already run without an error,
	// so we can rely on accessing the private field directly.
	err := os.Remove(s.configPath)
	if err != nil {
		return &current, err
	}

	return s, nil
}
```

If the file doesn't exist, the method returns the desired state and nil. If it does exist, the
method tries to delete the file. If the operation fails, it returns the current state and the error
message. If the operation succeeds, it returns the desired state and nil.

### Handle creating an instance

Next, implement the `create` method. It needs the same inputs and outputs as `remove`. It should
create the file and parent folders if needed, then compose the JSON for the configuration file and
write it.

```go
func (s *Settings) create(currentSettings Settings) (*Settings, error) {
	configDir := filepath.Dir(s.configPath)
	if err := os.MkdirAll(configDir, 0750); err != nil {
		return &currentSettings, fmt.Errorf(
			"failed to create folder for config file in '%s': %s",
			configDir,
			err,
		)
	}
	configFile, err := os.Create(s.configPath)
	if err != nil {
		return &currentSettings, fmt.Errorf(
			"failed to create config file '%s': %s",
			s.configPath,
			err,
		)
	}

	// Create the JSON for the tstoy configuration file.
	// Can't just marshal the Settings instance because it's a representation
	// of the settings, not a literal blob of the settings.
	settings := make(map[string]any)
	updates := make(map[string]any)
	addUpdates := false
	if s.UpdateAutomatically != nil {
		addUpdates = true
		updates["automatic"] = *s.UpdateAutomatically
	}
	if s.UpdateFrequency != 0 {
		addUpdates = true
		updates["checkFrequency"] = s.UpdateFrequency
	}
	if addUpdates {
		settings["updates"] = updates
	}

	configJSON, err := json.MarshalIndent(settings, "", "  ")
	if err != nil {
		return &currentSettings, fmt.Errorf(
			"unable to convert settings to json: %s",
			err,
		)
	}

	_, err = configFile.Write(configJSON)
	if err != nil {
		return &currentSettings, fmt.Errorf(
			"unable to write config file: %s",
			err,
		)
	}

	return s, nil
}
```

### Handle updating an instance

With `create` and `remove` implemented, the last method to implement is `update`. It needs the same
inputs and outputs as the others. It should:

1. Retrieve the actual map of settings in the configuration file.
1. Update only the settings that are out of sync.
1. Only update the configuration file if at least one setting needs enforcing.

```go
func (s *Settings) update(current Settings) (*Settings, error) {
	writeConfig := false

	currentMap, err := current.GetConfigMap()
	if err != nil {
		return nil, err
	}

	// ensure the map keys are all strings.
	maps.IntfaceKeysToStrings(currentMap)

	// Check for the update settings
	updates, ok := currentMap["updates"]
	if !ok {
		currentMap["updates"] = make(map[string]any)
		updates = currentMap["updates"]
	}

	// Only update if desired state defines UpdateAutomatically and:
	// 1. Current state doesn't define it, or
	// 2. Current state's setting doesn't match desired state.
	shouldSetUA := false
	if s.UpdateAutomatically != nil {
		if current.UpdateAutomatically == nil {
			shouldSetUA = true
		} else if *s.UpdateAutomatically != *current.UpdateAutomatically {
			shouldSetUA = true
		}
	}

	if shouldSetUA {
		writeConfig = true
		updates.(map[string]any)["automatic"] = *s.UpdateAutomatically
	} else if current.UpdateAutomatically != nil {
		updates.(map[string]any)["automatic"] = *current.UpdateAutomatically
	}

	// Only update if desired state defines UpdateFrequency and:
	// 1. Current state doesn't define it, or
	// 2. Current state's setting doesn't match desired state.
	if s.UpdateFrequency != 0 && s.UpdateFrequency != current.UpdateFrequency {
		writeConfig = true
		updates.(map[string]any)["checkFrequency"] = s.UpdateFrequency
	} else if current.UpdateFrequency != 0 {
		updates.(map[string]any)["checkFrequency"] = current.UpdateFrequency
	}

	// no changes made, leave config untouched
	if !writeConfig {
		return s, nil
	}

	currentMap["updates"] = updates.(map[string]any)

	configJson, err := json.MarshalIndent(currentMap, "", "  ")
	if err != nil {
		return &current, fmt.Errorf(
			"unable to convert updated settings to json: %s",
			err,
		)
	}

	err = os.WriteFile(s.configPath, configJson, 0750)
	if err != nil {
		return &current, fmt.Errorf(
			"unable to write updated config file: %s",
			err,
		)
	}

	return s, nil
}
```

## Finish implementing `set`

With the `create`, `remove`, and `update` methods implemented, update the `Enforce` method to
call them as required.

```go
func (s *Settings) Enforce() (*Settings, error) {
	err := s.Validate()
	if err != nil {
		return nil, err
	}

	current, err := s.GetConfigSettings()
	if err != nil {
		return nil, err
	}

	if s.Ensure == EnsureAbsent {
		return s.remove(current)
	}

	if current.Ensure == EnsureAbsent {
		return s.create(current)
	}

	return s.update(current)
}
```

Open `cmd/set.go` and edit the `setState` function to call the `Enforce` method.

```go
func setState(cmd *cobra.Command, args []string) error {
	enforcing := config.Settings{}

	if inputJSON != nil {
		enforcing = *inputJSON
	}
	if targetScope != config.ScopeUndefined {
		enforcing.Scope = targetScope
	}
	if targetEnsure != config.EnsureUndefined {
		enforcing.Ensure = targetEnsure
	}
	if rootCmd.PersistentFlags().Lookup("updateAutomatically").Changed {
		enforcing.UpdateAutomatically = &updateAutomatically
	}
	if updateFrequency != 0 {
		enforcing.UpdateFrequency = updateFrequency
	}

	final, err := enforcing.Enforce()
	if err != nil {
		return fmt.Errorf("can't enforce settings; %s", err)
	}

	return final.Print()
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
   go run ./main.go get --scope machine
   ```

   ```json
   {"ensure":"absent","scope":"machine"}
   ```

1. Enforce the desired state with the `set` command.

   ```sh
   go run ./main.go set --scope machine --ensure present --updateAutomatically=false
   ```

   ```json
   {"ensure":"present","scope":"machine","updateAutomatically":false}
   ```

1. Verify that the output from the `set` command matches the output from `get` after enforcing the
   desired state.

   ```sh
   go run ./main.go get --scope machine
   ```

   ```json
   {"ensure":"present","scope":"machine","updateAutomatically":false}
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
   }' | go run ./main.go set
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
