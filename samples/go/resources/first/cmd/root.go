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
	"os"

	"github.com/PowerShell/DSC-Samples/go/resources/first/config"
	"github.com/PowerShell/DSC-Samples/go/resources/first/input"
	"github.com/spf13/cobra"
	"github.com/thediveo/enumflag"
)

var targetScope config.Scope
var targetEnsure config.Ensure
var updateAutomatically bool
var updateFrequency config.Frequency
var inputJSON *config.Settings

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "gotstoy",
	Short: "A brief description of your application",
	Long: `A longer description that spans multiple lines and likely contains
examples and usage of using your application. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	// Uncomment the following line if your bare application
	// has an action associated with it:
	// Run: func(cmd *cobra.Command, args []string) { },
}

// Unlike normal cobra apps, this one sets the args explicitly from main to
// account for JSON blobs sent from stdin.
func Execute(args []string) {
	rootCmd.SetArgs(args)
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}

func init() {
	rootCmd.PersistentFlags().Var(
		enumflag.New(&targetScope, "scope", config.ScopeMap, enumflag.EnumCaseInsensitive),
		"scope",
		"The target scope for the configuration.",
	)
	rootCmd.RegisterFlagCompletionFunc("scope", config.ScopeFlagCompletion)

	rootCmd.PersistentFlags().Var(
		enumflag.New(&targetEnsure, "ensure", config.EnsureMap, enumflag.EnumCaseInsensitive),
		"ensure",
		"Whether the configuration file should exist.",
	)
	rootCmd.RegisterFlagCompletionFunc("ensure", config.EnsureFlagCompletion)

	rootCmd.PersistentFlags().BoolVar(
		&updateAutomatically,
		"updateAutomatically",
		false,
		"Whether the configuration should set the app to automatically update.",
	)

	rootCmd.PersistentFlags().Var(
		&updateFrequency,
		"updateFrequency",
		"How frequently the configuration should update, between 1 and 90 days inclusive.",
	)

	rootCmd.PersistentFlags().Var(
		&input.JSONFlag{Target: &inputJSON},
		"inputJSON",
		"Specify options as a JSON blob instead of using the scope, ensure, and update* flags.",
	)
}
