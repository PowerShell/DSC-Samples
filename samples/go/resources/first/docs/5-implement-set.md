---
title:  Step 5 - Implement set functionality
weight: 5
dscs:
  menu_title: 5. Implement set
---

Up to this point, the DSC Resource has been primarily concerned with representing and
getting the current state of an instance. To be fully useful, it needs to be able to
change a configuration file to enforce the desired state.

## Validate the desired state

Set accepts more properties than get, so it needs more validation: `ensure` must be a
valid value (defaulting to `present` when omitted, matching the schema default), and
`updateFrequency` must be in range. Add this to `settings.go`:

```go
// validateDesired normalizes and validates a desired state before set.
func validateDesired(s *Settings) error {
    if err := validateScope(s.Scope); err != nil {
        return err
    }
    switch s.Ensure {
    case "":
        s.Ensure = "present"
    case "present", "absent":
    default:
        return dsc.NewExitCodeErrorf(dsc.ExitInvalidInput,
            "invalid ensure '%s'; must be one of: present, absent", s.Ensure)
    }
    if s.Ensure == "present" && s.UpdateFrequency != 0 &&
        (s.UpdateFrequency < 1 || s.UpdateFrequency > 90) {
        return dsc.NewExitCodeErrorf(dsc.ExitInvalidInput,
            "invalid updateFrequency %d; must be an integer between 1 and 90, inclusive",
            s.UpdateFrequency)
    }
    return nil
}
```

## Implement the Set method

Add the `Set` method to the handler. Implementing `Set` makes the handler satisfy the
library's `Settable` interface — the resource, and the manifest you generate in the next
step, gain the set capability from this method's existence alone.

The method handles three cases: remove the file (`ensure: absent`), create it, or update
it. The create and update paths collapse into one, because the method merges the desired
settings into whatever the file currently contains — preserving settings the resource
doesn't manage.

```go
// Set enforces the desired state and returns the state after enforcement.
func (Handler) Set(_ context.Context, desired Settings) (Settings, error) {
    if err := validateDesired(&desired); err != nil {
        return desired, err
    }

    path, err := configPath(desired.Scope)
    if err != nil {
        return desired, err
    }

    if desired.Ensure == "absent" {
        if err := os.Remove(path); err != nil && !errors.Is(err, fs.ErrNotExist) {
            return desired, fmt.Errorf("failed to remove config file '%s': %w", path, err)
        }
        return Settings{Scope: desired.Scope, Ensure: "absent"}, nil
    }

    // Read the existing config file as a raw map so settings this resource
    // doesn't manage are preserved.
    cfg, err := readConfigMap(path)
    if err != nil && !errors.Is(err, fs.ErrNotExist) {
        return desired, err
    }
    if cfg == nil {
        cfg = map[string]any{}
    }

    updates, _ := cfg["updates"].(map[string]any)
    if updates == nil {
        updates = map[string]any{}
    }
    if desired.UpdateAutomatically != nil {
        updates["automatic"] = *desired.UpdateAutomatically
    }
    if desired.UpdateFrequency != 0 {
        updates["checkFrequency"] = desired.UpdateFrequency
    }
    if len(updates) > 0 {
        cfg["updates"] = updates
    }

    if err := os.MkdirAll(filepath.Dir(path), 0o750); err != nil {
        return desired, fmt.Errorf("failed to create folder for config file: %w", err)
    }
    data, err := json.MarshalIndent(cfg, "", "  ")
    if err != nil {
        return desired, fmt.Errorf("unable to convert settings to json: %w", err)
    }
    if err := os.WriteFile(path, data, 0o640); err != nil {
        return desired, fmt.Errorf("unable to write config file: %w", err)
    }

    // Re-read from disk so the returned after-state is the actual state.
    return settingsAt(desired.Scope, path)
}
```

Details worth noticing:

- Removing an already-absent file succeeds. Set must be _idempotent_ — DSC may enforce
  the same configuration repeatedly, and enforcing an already-correct state is success,
  not an error.
- The `*bool` pointer earns its keep here: `updates["automatic"]` is only touched when the
  user actually specified `updateAutomatically`, so an unspecified property never
  overwrites the current value.
- The method returns `settingsAt(...)` rather than `desired`: the contract for set output
  is the _actual_ state after enforcement, which may include properties the desired state
  didn't mention (like an update frequency already in the file).

## Declare the set behavior

Tell the library what set returns by extending the `ResourceConfig` in `main.go`:

```go
        // Set prints the state after enforcement; the resource is idempotent
        // and validates state itself, so DSC skips its pre-set test.
        SetReturn:         dsc.SetReturnState,
        ImplementsPretest: true,
```

`SetReturn: dsc.SetReturnState` declares that set prints the post-enforcement state —
the library frames the output and the manifest advertises `return: state`.
`ImplementsPretest: true` tells DSC the resource handles being invoked unconditionally, so
the engine doesn't need to run a test before every set.

## Try it out

Enforce a desired state for the user scope and read it back:

```sh
go run . set --input '{
  "scope": "user",
  "updateAutomatically": true,
  "updateFrequency": 30
}'
go run . get --input '{ "scope": "user" }'
```

```json
{"scope":"user","ensure":"present","updateAutomatically":true,"updateFrequency":30}
{"scope":"user","ensure":"present","updateAutomatically":true,"updateFrequency":30}
```

Then remove it:

```sh
go run . set --input '{ "scope": "user", "ensure": "absent" }'
```

```json
{"scope":"user","ensure":"absent"}
```

The resource is now fully implemented. The remaining step before DSC can use it is the
resource manifest, which with the RDK, you don't have to write by hand.
