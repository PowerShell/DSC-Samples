---
title:  Step 3 - Handle input
weight: 3
dscs:
  menu_title: 3. Handle input
---

Now that the valid values for settings are defined, the root command of the DSC Resource needs to
handle when users specify those values.

## Define the flag variables

Open the `cmd/root.go` file in the editor.

Add variables for each of the fields of the `Settings` type so users can specify those values at
the command line.

```go
var targetScope config.Scope
var targetEnsure config.Ensure
var updateAutomatically bool
var updateFrequency config.Frequency
```

## Handle arguments as input

The first input method the resource should support is command line arguments. This makes using the
resource outside of DSC easier, like when iteratively developing the command. It's also the most
common way users expect to call a command directly.

### Define the persistent flags

Next, find the `init` function at the bottom of the file. Inside it, define persistent flags so
users can pass the values to both `get` and `set` as arguments.

```go
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
}
```

Use the `enumflag` module to for the `ensure` and `scope` flags. It handles parsing the user inputs
and converting them to the enumeration values. Use the flag completion functions you defined
earlier to ensure that users can opt into shell completions for those flags.

### Validate input flags

With the `Settings` defined and command line flags added to the root command, you can begin
validating that the settings flags work as expected.

Open the `cmd/get.go` file in the editor.

At the bottom of the file, create a new `getState` function that takes two parameters, a pointer to
`cobra.Command` and a slice of strings, and returns an error.

```go
func getState(cmd *cobra.Command, args []string) error {
	return nil
}
```

Replace the `Run` entry in the `getCmd` variable's definition with the `RunE` field set to the
`getState` function. Update the documentation for the command to be more specific to the DSC
Resource.

```go
var getCmd = &cobra.Command{
	Use:   "get",
	Short: "Gets the current state of a tstoy configuration file.",
	Long: `The get command returns the current state of a tstoy configuration
file as a JSON blob to stdout.`,
	RunE: getState,
}
```

Next, update the `getState` function to report the value of any specified flags. You'll replace
this implementation later, but it's useful for validating that the flags work as expected.

```go
func getState(cmd *cobra.Command, args []string) error {
	if targetScope != config.ScopeUndefined {
		fmt.Println("Specified --scope as", targetScope)
	}
	if targetEnsure != config.EnsureUndefined {
		fmt.Println("Specified --ensure as", targetEnsure)
	}
	if rootCmd.PersistentFlags().Lookup("updateAutomatically").Changed {
		fmt.Println("Specified --updateAutomatically as", updateAutomatically)
	}
	if updateFrequency != 0 {
		fmt.Println("Specified --updateFrequency as", updateFrequency)
	}
	return nil
}
```

Run the DSC Resource with different flags to verify the output.

```sh
go run ./main.go get --scope machine --ensure absent
go run ./main.go get --updateAutomatically --updateFrequency 45
go run ./main.go get --updateAutomatically=false --ensure Absent
```

```Output
Specified --ensure as absent
Specified --scope as machine

Specified --updateAutomatically as true
Specified --updateFrequency as 45

Specified --ensure as absent
Specified --updateAutomatically as false
```

Next, you can test that the arguments are validating correctly:

```sh
go run ./main.go get --scope 1
go run ./main.go get --scope incorrect
go run ./main.go get --updateFrequency 100
```

```Output
Error: invalid argument "1" for "--scope" flag: must be 'machine', 'user'

Error: invalid argument "incorrect" for "--scope" flag: must be 'machine', 'user'

Error: invalid argument "100" for "--updateFrequency" flag: invalid value 100;
must be an integer between 1 and 90, inclusive
```

With validation confirmed, the command can accept command-line arguments.

## Handle JSON input over stdin

When command-based DSC Resources are called by `dsc` itself, they may get their input as a JSON
blob over `stdin`. While specifying flags at the command line is useful for testing, it's more
robust for the DSC Resource to support sending input over `stdin`. This also makes it easier for
other integrating tools to interact with the DSC Resource.

### Add handlers for JSON input

Create the `input` folder in the project root. Inside it, create the `input.go` file. This file
defines how you handle input from `stdin`.

```sh
mkdir ./input
touch ./input/input.go
```

Open `input/input.go` and set the package name to `input`.

```go
package input
```

Now you need to ensure that the DSC Resource can handle a JSON blob as input along with the other
flags. Implement a new type that satisfies the [pflag.Value][05] interface.

Define a type called `JSONFlag` as a struct with the `Target` field as the `any` type.

```go
type JSONFlag struct {
	Target any
}
```

Implement the `String`, `Set`, and `Type` methods for `JSONFlag`.

```go
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
```

### Add handler for stdin

Next, the DSC Resource needs a function that can handle reading from `stdin`. The function must
operate on the list of arguments for the DSC Resource. If there's input on `stdin`, it's added to
the list of arguments with the `--inputJSON` flag.

```go
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
```

The function doesn't need to validate that the input is valid JSON. Instead, the `JSONFlag` and the
command handle the validation. Implementing the function to append the JSON as an argument also
gives the user the choice to pass a JSON blob as a normal argument.

### Add inputJSON to the root command { toc_md="Add `inputJSON` flag" }

Before you can pass a JSON blob to the commands, you must update the root command to accept the
`--inputJson` flag.

Open `cmd/root.go` and add the `inputJSON` variable with its type as a pointer to
`config.Settings`.

```go
var inputJSON *config.Settings
```

In the `init` function, add a new persistent flag for `--inputJSON`.

```go
rootCmd.PersistentFlags().Var(
	&input.JSONFlag{Target: &inputJSON},
	"inputJSON",
	"Specify options as a JSON blob instead of using the scope, ensure, and update* flags.",
)
```

The new flag uses the `JSONFlag` type defined in the `input` package and sets the `Target` field to
the `inputJSON` variable. Because that variable has the `Settings` type, when the flag
automatically unmarshals the input, it deserializes the blob to `Settings` for the DSC Resource.

### Update root command to handle stdin { toc_text "Update root command for stdin" }

Finally, you must update the `Execute` function to take a list of arguments, because argument
passing must be explicitly handled to support `stdin`.

```go
// Unlike normal cobra apps, this one sets the args explicitly from main to
// account for JSON blobs sent from stdin.
func Execute(args []string) {
	rootCmd.SetArgs(args)
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}
```

### Update main to handle `stdin`

Now that the `HandleStdIn` function is defined and the root command is updated, `main` needs to be
updated to pass the arguments to the `Execute` function and handle JSON over `stdin`.

Open `main.go` and replace the `main` function.

```go
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
```

## Verify using JSON as input

Now that the DSC Resource can accept JSON as input over `stdin` or as an argument, the `get`
command needs to handle that input.

Open `cmd/get.go` and ensure that the `getState` function prints the value for the `inputJSON`
variable if it's not null.

```go
func getState(cmd *cobra.Command, args []string) error {
	if inputJSON != nil {
		fmt.Println("Specified inputJSON as:")
		(*inputJSON).Print()
	}
	if targetScope != config.ScopeUndefined {
		fmt.Println("Specified --scope as", targetScope)
	}
	if targetEnsure != config.EnsureUndefined {
		fmt.Println("Specified --ensure as", targetEnsure)
	}
	if rootCmd.PersistentFlags().Lookup("updateAutomatically").Changed {
		fmt.Println("Specified --updateAutomatically as", updateAutomatically)
	}
	if updateFrequency != 0 {
		fmt.Println("Specified --updateFrequency as", updateFrequency)
	}
	return nil
}
```

You can verify the behavior with a few commands:

```sh
go run ./main.go get --inputJSON '{ "scope": "machine" }'
go run ./main.go get --inputJSON '{ "scope": "machine" }' --scope user
'{ "scope": "machine" }'  | go run ./main.go get
'{ "scope": "machine" }'  | go run ./main.go get --scope user
'{ "ensure": "present" }' | go run ./main.go get
```

```Output
Specified inputJSON as:
{"scope":"machine"}

Specified inputJSON as:
{"scope":"machine"}
Specified --scope as user

Specified inputJSON as:
{"scope":"machine"}

Specified inputJSON as:
{"scope":"machine"}
Specified --scope as user

Specified inputJSON as:
{"ensure":"present"}
```

The DSC Resource is now fully implemented to handle input as arguments and as a JSON blob over
stdin.

[05]: https://pkg.go.dev/github.com/spf13/pflag#Value
