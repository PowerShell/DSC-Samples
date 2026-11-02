---
title:  Step 4 - Implement get functionality
weight: 4
dscs:
  menu_title: 4. Implement get
---

To implement the get operation, the DSC Resource needs to find a specific `tstoy`
configuration file and translate its contents into an instance of `Settings`.

Recall from [About the TSToy application][01] that you can use the `tstoy show path`
command to get the full path to the application's configuration files. The DSC Resource
can use that command instead of trying to generate the paths itself.

## Define get helper functions { toc_md="Define `get` helpers" }

Open `settings.go`. Add the `configPath` function, which asks `tstoy` where the config
file for a scope lives:

```go
// configPath asks the tstoy application where the scope's config file lives.
func configPath(scope string) (string, error) {
    out, err := exec.Command("tstoy", "show", "path", scope).Output()
    if err != nil {
        return "", fmt.Errorf(
            "failed to query tstoy for the %s config file path (is tstoy on PATH?): %w",
            scope, err)
    }
    return strings.TrimSpace(string(out)), nil
}
```

Next, add `readConfigMap` to read a config file as a raw map. Reading into a map instead
of a struct matters for set later: it preserves any settings in the file that this
resource doesn't manage.

```go
func readConfigMap(path string) (map[string]any, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, err
    }
    var cfg map[string]any
    if err := json.Unmarshal(data, &cfg); err != nil {
        return nil, fmt.Errorf("config file '%s' is not valid JSON: %w", path, err)
    }
    return cfg, nil
}
```

Finally, add `settingsAt`, which turns a config file into the resource's state model:

```go
// settingsAt reads the config file into the resource's state model. A
// missing file is the valid "absent" state, not an error.
func settingsAt(scope, path string) (Settings, error) {
    cfg, err := readConfigMap(path)
    if errors.Is(err, fs.ErrNotExist) {
        return Settings{Scope: scope, Ensure: "absent"}, nil
    }
    if err != nil {
        return Settings{Scope: scope}, err
    }

    current := Settings{Scope: scope, Ensure: "present"}
    if updates, ok := cfg["updates"].(map[string]any); ok {
        if auto, ok := updates["automatic"].(bool); ok {
            current.UpdateAutomatically = &auto
        }
        if freq, ok := updates["checkFrequency"].(float64); ok {
            current.UpdateFrequency = int(freq)
        }
    }
    return current, nil
}
```

The first branch encodes an important DSC convention: when the instance doesn't exist, get
reports that as valid state (`ensure: absent`) — not as an error. DSC needs the "it's
not there" answer to decide whether set has work to do.

## Implement the Get method

Replace the stub `Get` method with the real implementation:

```go
// Get returns the current state of the config file for the requested scope.
func (Handler) Get(_ context.Context, in Settings) (Settings, error) {
    if err := validateScope(in.Scope); err != nil {
        return in, err
    }
    path, err := configPath(in.Scope)
    if err != nil {
        return in, err
    }
    return settingsAt(in.Scope, path)
}
```

That's the entire get operation. The library already handles parsing the input JSON into
`Settings`, serializing the returned state as one compact JSON line on stdout, and mapping
any returned error to a trace message and exit code.

## Try it out

With `tstoy` on your `PATH`, get the current state of both scopes:

```sh
go run . get --input '{ "scope": "machine" }'
echo '{ "scope": "user" }' | go run . get
```

```json
{"scope":"machine","ensure":"absent"}
{"scope":"user","ensure":"absent"}
```

If you've never configured TSToy, both scopes report `ensure: absent` — the files don't
exist yet. Create one with the `tstoy` application itself and see the resource pick it up:

```sh
tstoy set user --auto=true --frequency 45
go run . get --input '{ "scope": "user" }'
```

```json
{"scope":"user","ensure":"present","updateAutomatically":true,"updateFrequency":45}
```

The resource now reports real state. Next, you'll teach it to change that state.

[01]: /tstoy/about
