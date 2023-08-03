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

package cmd

import (
	"fmt"

	"github.com/PowerShell/DSC-Samples/go/resources/first/config"
	"github.com/spf13/cobra"
)

// setCmd represents the set command
var setCmd = &cobra.Command{
	Use:   "set",
	Short: "Sets a tstoy configuration file to the desired state.",
	Long: `The set command ensures that the tstoy configuration file for a
specific scope has the desired settings. It returns the updated settings state
as a JSON blob to stdout.`,
	RunE: setState,
}

func init() {
	rootCmd.AddCommand(setCmd)
}

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
