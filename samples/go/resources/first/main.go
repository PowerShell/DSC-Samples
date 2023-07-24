// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package main

import (
	"os"

	"github.com/PowerShell/DSC-Samples/go/resources/first/cmd"
	"github.com/PowerShell/DSC-Samples/go/resources/first/input"
)

func main() {
	args := []string{}
	for index, arg := range os.Args {
		// skip the first index, because it's the application name
		if index > 0 {
			args = append(args, arg)
		}
	}

	// Check stdin and add any found JSON blob after an --inputJSON flag.
	args = input.HandleStdIn(args)

	// execute with the combined arguments
	cmd.Execute(args)
}
