// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
//
// This sample code is not supported under any Microsoft standard support program or service.
// This sample code is provided AS IS without warranty of any kind.

package main

import dsc "github.com/LibreDsc/dsc-go-rdk"

func main() {
	r := dsc.MustResource[Settings](Handler{}, dsc.ResourceConfig{
		Type:        "TSToy.Example/gotstoy",
		Version:     "0.1.0",
		Description: "A DSC Resource written in Go to manage TSToy.",
		Tags:        []string{"tstoy", "example", "go"},

		// Set prints the state after enforcement; the resource is idempotent
		// and validates state itself, so DSC skips its pre-set test.
		SetReturn:         dsc.SetReturnState,
		ImplementsPretest: true,

		SchemaOptions: dsc.SchemaOptions{
			SchemaDescription: "Golang TSToy Resource",
			Descriptions: map[string]string{
				"scope":  "Defines which of TSToy's config files to manage.",
				"ensure": "Defines whether the config file should exist.",
				"updateAutomatically": "Indicates whether TSToy should check for" +
					" updates when it starts.",
				"updateFrequency": "Indicates how many days TSToy should wait" +
					" before checking for updates.",
			},
			// Constraints the struct tags can't express.
			Overrides: func(schema map[string]any) {
				props := schema["properties"].(map[string]any)
				props["ensure"].(map[string]any)["default"] = "present"
				frequency := props["updateFrequency"].(map[string]any)
				frequency["minimum"] = 1
				frequency["maximum"] = 90
			},
		},
	})
	r.Main("gotstoy")
}
