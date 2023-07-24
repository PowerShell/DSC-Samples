// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package cmd

import (
	"fmt"
	"path/filepath"

	"github.com/PowerShell/DSC-Samples/app/config"
	"github.com/spf13/cobra"
)

// PathCmd represents the path command
var PathCmd = &cobra.Command{
	Use:   "path",
	Short: "Retrieves the path to the machine and user configs",
	Long: `You can use this command to retrieve the path to the configuration
	files that the application looks for on your system.
	
	If you don't specify any arguments for this command, it returns the paths
	to both files, with the machine scope configuration file first.`,
	Run:       showPath,
	ValidArgs: []string{"machine", "user"},
	Args:      cobra.MatchAll(cobra.MaximumNArgs(2), cobra.OnlyValidArgs),
}

func init() {
	ShowCmd.AddCommand(PathCmd)
}

func showPath(cmd *cobra.Command, args []string) {
	if len(args) == 0 {
		printConfigPath("machine")
		printConfigPath("user")
	} else {
		for _, scope := range args {
			printConfigPath(scope)
		}
	}
}

func printConfigPath(scope string) {
	folder := config.MachineFolder
	if scope == "user" {
		folder = config.UserFolder
	}
	path := filepath.Join(folder, config.FileName)
	path = fmt.Sprintf("%s.%s", path, config.FileExtension)
	fmt.Println(path)
}
