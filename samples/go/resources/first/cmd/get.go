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

var all bool

// getCmd represents the get command
var getCmd = &cobra.Command{
	Use:   "get",
	Short: "Gets the current state of a tstoy configuration file.",
	Long: `The get command returns the current state of a tstoy configuration
file as a JSON blob to stdout.`,
	RunE: getState,
}

func init() {
	rootCmd.AddCommand(getCmd)
	getCmd.Flags().BoolVar(
		&all,
		"all",
		false,
		"Get the configurations for all scopes.",
	)
}

func getState(cmd *cobra.Command, args []string) error {
	list := []config.Settings{}
	if all {
		list = append(
			list,
			config.Settings{Scope: config.ScopeMachine},
			config.Settings{Scope: config.ScopeUser},
		)
	} else if targetScope != config.ScopeUndefined {
		// explicit --scope overrides JSON
		list = append(list, config.Settings{Scope: targetScope})
	} else if inputJSON != nil {
		list = append(list, *inputJSON)
	} else {
		// fails but with consistent messaging
		list = append(list, config.Settings{Scope: targetScope})
	}

	for _, s := range list {

		err := s.Validate()
		if err != nil {
			return fmt.Errorf("can't get settings; %s", err)
		}

		config, err := s.GetConfigSettings()
		if err != nil {
			return fmt.Errorf("failed to get settings; %s", err)
		}

		err = config.Print()
		if err != nil {
			return err
		}
	}

	return nil
}
