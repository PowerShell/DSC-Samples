// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package input

import (
	"encoding/json"
	"io"
	"os"
	"strings"
)

type JSONFlag struct {
	Target any
}

func (f *JSONFlag) String() string {
	b, err := json.Marshal(f.Target)
	if err != nil {
		return "failed to marshal object"
	}
	return string(b)
}

func (f *JSONFlag) Set(v string) error {
	return json.Unmarshal([]byte(v), f.Target)
}

func (f *JSONFlag) Type() string {
	return "json"
}

func HandleStdIn(args []string) []string {
	info, _ := os.Stdin.Stat()
	if (info.Mode() & os.ModeCharDevice) == os.ModeCharDevice {
		// do nothing
	} else {
		stdin, err := io.ReadAll(os.Stdin)
		if err != nil {
			panic(err)
		}

		// remove surrounding whitespace
		jsonBlob := strings.Trim(string(stdin), "\n")
		jsonBlob = strings.Trim(jsonBlob, "\r")
		jsonBlob = strings.TrimSpace(jsonBlob)
		// only add to arguments if the string is non-empty.
		if jsonBlob != "" {
			args = append(args, "--inputJSON", jsonBlob)
		}
	}

	return args
}
