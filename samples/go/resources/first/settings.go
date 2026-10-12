// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
//
// This sample code is not supported under any Microsoft standard support program or service.
// This sample code is provided AS IS without warranty of any kind.

package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	dsc "github.com/LibreDsc/dsc-go-rdk"
)

// Settings models one TSToy configuration file as DSC state. The struct is
// the resource's contract: dsc-go-rdk generates the instance JSON Schema from its
// fields and tags, and every operation receives and returns it.
type Settings struct {
	Scope               string `json:"scope" enum:"machine,user"`
	Ensure              string `json:"ensure,omitempty" enum:"present,absent"`
	UpdateAutomatically *bool  `json:"updateAutomatically,omitempty"`
	UpdateFrequency     int    `json:"updateFrequency,omitempty"`
}

// Handler implements the resource's capabilities: Gettable and Settable.
// TSToy models existence with its own ensure property, so there is no
// Deletable — set with ensure:absent removes the file.
type Handler struct{}

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

// validateScope checks the required scope property. Validation failures map
// to DSC's invalid-input exit code (4).
func validateScope(scope string) error {
	switch scope {
	case "machine", "user":
		return nil
	case "":
		return dsc.NewExitCodeErrorf(dsc.ExitInvalidInput,
			"the scope property is required; must be one of: machine, user")
	default:
		return dsc.NewExitCodeErrorf(dsc.ExitInvalidInput,
			"invalid scope '%s'; must be one of: machine, user", scope)
	}
}

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
