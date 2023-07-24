---
title:  Step 2 - Define the configuration settings
weight: 2
dscs:
  menu_title: 2. Define settings
---

## Create the config module

Create the `config` folder in the project root. Inside it, create the `config.go` file. This file
defines the configuration types and functions of the DSC Resource.

```sh
mkdir ./config
touch ./config/config.go
```

Set the package name at the top of the file to `config`:

```go
package config
```

Create a new type called `Settings` as a struct. The fields of the struct are the settings the DSC
Resource manages. In the struct, define the `Ensure`, `Scope`, `UpdateAutomatically`, and
`UpdateFrequency` fields. Set their types to `any`.

```go
type Settings struct {
	Ensure              any
	Scope               any
	UpdateAutomatically any
	UpdateFrequency     any
}
```

Defining the fields this way is convenient but also inaccurate. To make the DSC Resource more
reliable, you need to define the fields to match their purpose.

## Define Ensure

The `Ensure` field follows a common pattern in DSC for managing whether an instance of a DSC
Resource should exist. To use this pattern, the field should be an enumeration with the valid
values `absent` and `present`.

Create a new type called `Ensure` as an integer.

```go
type Ensure int
```

Define three constants of the `Ensure` type to use as enumerations: `EnsureUndefined`,
`EnsureAbsent`, and `EnsurePresent`.

```go
const (
	EnsureUndefined Ensure = iota
	EnsureAbsent
	EnsurePresent
)
```

Implement the [fmt.Stringer][01] interface for the `Ensure` type. This interface translates the
values into strings. It should return `"absent"`, `"present"`, or `"undefined"`.

```go
func (e Ensure) String() string {
	switch e {
	case EnsureAbsent:
		return "absent"
	case EnsurePresent:
		return "present"
	}

	return "undefined"
}
```

Implement a function called `ParseEnsure` that converts an input string into an `Ensure` enum and
returns an error if the input can't be parsed as `EnsurePresent` or `EnsureAbsent`.

```go
func ParseEnsure(s string) (Ensure, error) {
	switch strings.ToLower(s) {
	case "absent":
		return EnsureAbsent, nil
	case "present":
		return EnsurePresent, nil
	}

	return EnsureUndefined, fmt.Errorf(
		"unable to convert '%s' to Ensure, must be one of: absent, present",
		s,
	)
}
```

Implement the `MarshalJSON` and `UnmarshalJSON` methods for `Ensure` that convert to and from JSON
as the enum's label instead of the integer value.

```go
func (e Ensure) MarshalJSON() ([]byte, error) {
	return json.Marshal(e.String())
}

func (ensure *Ensure) UnmarshalJSON(data []byte) (err error) {
	var e string
	if err := json.Unmarshal(data, &e); err != nil {
		return err
	}
	if *ensure, err = ParseEnsure(e); err != nil {
		return err
	}

	return nil
}
```

Create a variable called `EnsureMap` to map the enumeration value to its string. This map is used
when you define the command line flags for the DSC Resource.

```go
var EnsureMap = map[Ensure][]string{
	EnsureAbsent:  {"absent"},
	EnsurePresent: {"present"},
}
```

Create a function called `EnsureFlagCompletion`. This function provides shell completion for the
command-line flags of the DSC Resource.

```go
func EnsureFlagCompletion(
	cmd *cobra.Command,
	args []string,
	toComplete string,
) ([]string, cobra.ShellCompDirective) {
	completions := []string{
		"absent\tThe configuration file shouldn't exist.",
		"present\tThe configuration file should exist.",
	}
	return completions, cobra.ShellCompDirectiveNoFileComp
}
```

Update the `Ensure` field of the `Settings` type to use the newly defined `Ensure` value instead of
`any`.

```go
type Settings struct {
	Ensure              Ensure
	Scope               any
	UpdateAutomatically any
	UpdateFrequency     any
}
```

## Define Scope

The `Scope` field of the `Settings` struct defines which instance of the `tstoy` configuration file
the DSC Resource should manage. Like `Ensure`, it should be an enumeration.

Define the `Scope` as an integer. Add constant values for the enumeration as `ScopeUndefined`,
`ScopeMachine`, and `ScopeUser`.

```go
type Scope int

const (
	ScopeUndefined Scope = iota
	ScopeMachine
	ScopeUser
)
```

`Scope` needs the same functions and methods you defined for `Ensure`, but for its own enumeration
values.

```go
func (s Scope) String() string {
	switch s {
	case ScopeMachine:
		return "machine"
	case ScopeUser:
		return "user"
	}

	return "undefined"
}

func ParseScope(s string) (Scope, error) {
	switch strings.ToLower(s) {
	case "machine":
		return ScopeMachine, nil
	case "user":
		return ScopeUser, nil
	}

	return ScopeUndefined, fmt.Errorf(
		"unable to convert '%s' to Scope, must be one of: machine, user",
		s,
	)
}

func (s Scope) MarshalJSON() ([]byte, error) {
	return json.Marshal(s.String())
}

func (scope *Scope) UnmarshalJSON(data []byte) (err error) {
	var e string
	if err := json.Unmarshal(data, &e); err != nil {
		return err
	}
	if *scope, err = ParseScope(e); err != nil {
		return err
	}

	return nil
}

var ScopeMap = map[Scope][]string{
	ScopeMachine: {"machine"},
	ScopeUser:    {"user"},
}

func ScopeFlagCompletion(
	cmd *cobra.Command,
	args []string,
	toComplete string,
) ([]string, cobra.ShellCompDirective) {
	completions := []string{
		"machine\tThe configuration file should exist.",
		"user\tThe configuration file shouldn't exist.",
	}
	return completions, cobra.ShellCompDirectiveNoFileComp
}
```

When you've implemented the `Scope` type, enumerations, methods, and functions, update the `Scope`
field of the `Settings` type.

```go
type Settings struct {
	Ensure              Ensure
	Scope               Scope
	UpdateAutomatically any
	UpdateFrequency     any
}
```

## Define UpdateAutomatically

Like `Ensure` and `Scope`, whether the `tstoy` application should be configured for automatic
updates only has two options. Unlike `Ensure` and `Scope`, you can represent those options as a
boolean.

Update the `UpdateAutomatically` field of the `Settings` type to be a pointer to a boolean value.
Using a pointer for this field allows the value to be `nil`, which enables the DSC Resource to
distinguish between the setting not being specified and being specified as `false`.

```go
type Settings struct {
	Ensure              Ensure
	Scope               Scope
	UpdateAutomatically *bool
	UpdateFrequency     any
}
```

If the value wasn't a pointer, the DSC Resource would need extra handling to distinguish between
whether the value is false because the user or configuration file specified the value as `false` or
because it wasn't specified at all.

## Define UpdateFrequency

The `UpdateFrequency` field represents a count of days between `1` and `90`, inclusive. To add
validation for the field, define a new type called `Frequency` as an integer.

```go
type Frequency int
```

Next, define the `Validate` method to check whether a `Frequency` value is valid for the setting.
It should return an error when the integer value of the Frequency is out of range.

```go
func (f Frequency) Validate() error {
	v := int(f)
	if v < 1 || v > 90 {
		return fmt.Errorf(
			"invalid value %v; must be an integer between 1 and 90, inclusive",
			v,
		)
	}
	return nil
}
```

To make the new type usable as a command line flag, you need to implement the `Set`, `Type`, and
`String` methods of the [pflag.Value interface][02].

```go
func (f *Frequency) Set(s string) error {
	v, err := strconv.ParseInt(s, 0, 64)
	if err != nil {
		return err
	}

	*f = Frequency(v)

	return f.Validate()
}

func (f *Frequency) Type() string {
	return "int"
}

func (f *Frequency) String() string {
	return strconv.Itoa(int(*f))
}
```

Finally, update the `UpdateFrequency` field of `Settings` to use the defined `Frequency` type.

```go
type Settings struct {
	Ensure              Ensure
	Scope               Scope
	UpdateAutomatically *bool
	UpdateFrequency     Frequency
}
```

## Ensure Settings serializes to JSON correctly { toc_text="Serialize Settings to JSON" }

Now that the `Settings` type is defined and has the correct value types for each field, you need to
add tags to the fields so they can be marshalled to and unmarshalled from JSON correctly.

```go
type Settings struct {
	Ensure              Ensure    `json:"ensure,omitempty"`
	Scope               Scope     `json:"scope,omitempty"`
	UpdateAutomatically *bool     `json:"updateAutomatically,omitempty"`
	UpdateFrequency     Frequency `json:"updateFrequency,omitempty"`
}
```

The tags should all be in the format `json:"<key_name>,omitempty"`. The first value defines the
name of the key that the DSC Resource expects from JSON input and uses for returning an instance of
`Settings` to DSC. The `omitempty` value indicates that if the fields value is the same as its zero
value, that key shouldn't be included in the output JSON.

## Ensure Settings can print as JSON

Now that an instance of `Settings` can correctly serialize to JSON, define the `Print()` method to
simplify emitting the instance as a single line of JSON.

```go
func (s *Settings) Print() error {
	configJson, err := json.Marshal(s)
	if err != nil {
		return err
	}

	fmt.Println(string(configJson))

	return nil
}
```

## Implement validation for Settings

The DSC Resource should be able to report whether an instance of Settings is valid and, if it
isn't, how it's invalid.

Add the `Validate` method to return an error if the instance is invalid.

```go
func (s *Settings) Validate() error {
	if s.Scope == ScopeUndefined {
		return fmt.Errorf(
			"the Scope setting isn't defined. Must define a Scope for Settings",
		)
	}

	if s.Ensure == EnsureAbsent {
		return nil
	}

	if s.UpdateFrequency != 0 {
		return s.UpdateFrequency.Validate()
	}

	return nil
}
```

The method returns an error if the `Scope` field is undefined because the resource requires a
specific scope to manage a `tstoy` configuration file. It short-circuits the validation if `Ensure`
is set to absent because all other keys are ignored. Finally, if the `UpdateFrequency` field is
invalid, it returns an error message indicating the issue.

[01]: https://pkg.go.dev/fmt#Stringer
[02]: https://pkg.go.dev/github.com/spf13/pflag#Value
