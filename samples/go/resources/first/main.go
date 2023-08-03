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
