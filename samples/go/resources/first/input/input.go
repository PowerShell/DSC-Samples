// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.
//
// This sample code is not supported under any Microsoft standard support program or service.
// This sample code is provided AS IS without warranty of any kind. Microsoft disclaims all implied
// warranties including, without limitation,  any implied warranties of merchantability or of
// fitness for a particular purpose. The entire risk arising out of the use or performance of the
// sample code and documentation remains with you. In no event shall Microsoft, its authors, or
// anyone else involved in the creation, production, or delivery of the scripts be liable for any
// damages whatsoever (including, without limitation, damages for loss of business  profits,
// business interruption, loss of business information, or other pecuniary loss) arising out of the
// use of or inability to use the  sample scripts or documentation, even if Microsoft has been
// advised of the possibility of such damages.

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
