# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

$env:PSModulePath     += [System.IO.Path]::PathSeparator + $pwd
$MachinePath,$UserPath = tstoy show path