#!/usr/bin/env pwsh
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

<#
    .SYNOPSIS
    Builds the gotstoy DSC Resource.

    .DESCRIPTION
    This build script handles building the `gotstoy` DSC Resource. You can use it to build the DSC
    Resource for your current platform, for every platform, or to run the acceptance tests.

    .PARAMETER Target
    Defines the target to build. Valid values are `build`, `package`, and `test`. The default value
    is `build`.

    When the value is `build`, the script builds the DSC Resource for the current platform. When
    the value is `package`, the script builds the DSC Resource for every platform. When the value
    is `test`, the script builds the DSC Resource for the current platform and runs the acceptance
    tests.

    .PARAMETER Initialize
    When specified, the script adds the DSC Resource to the current PowerShell session as an alias
    and registers the command's completions.

    .PARAMETER AddToPath
    When specified, the script adds the DSC Resource to the current PowerShell session's PATH
    environment variable. DSC won't recognize the built application unless it's in the PATH.
#>

[CmdletBinding()]
param (
    [ValidateSet('build', 'package', 'test')]
    [string]$Target = 'build',
    [switch]$Initialize,
    [switch]$AddToPath
)

function Build-Project {
    [cmdletbinding()]
    [OutputType([System.Management.Automation.ApplicationInfo])]
    param(
        [switch]$All
    )

    begin {
        $Arguments = @()
    }

    process {
        if ($All) {
            $Arguments = @(
                'release'
                '--skip-publish'
                '--skip-announce'
                '--skip-validate'
                '--clean'
                '--release-notes', './RELEASE_NOTES.md'
            )
        } else {
            $Arguments = @(
                'build'
                '--snapshot'
                '--clean'
                '--single-target'
            )
        }

        & goreleaser @Arguments

        Get-Command './dist/gotstoy*/gotstoy*' -ErrorAction Stop
    }
}

switch ($Target) {
    'build' {
        $Application = Build-Project -ErrorAction Stop
        $ApplicationFolder = Split-Path -Parent $Application.Path
        Copy-Item -Path "$PSScriptRoot/gotstoy.dsc.resource.json" -Destination $ApplicationFolder
        if ($AddToPath) {
            $PathSeparator = [System.IO.Path]::PathSeparator
            if ($ApplicationFolder -notin ($env:PATH -split $PathSeparator)) {
                $env:PATH = $ApplicationFolder + $PathSeparator + $env:PATH
            }
        }
        if ($Initialize) {
            $Alias = Set-Alias -Name gotstoy -Value $Application.Path -PassThru
            Invoke-Expression $(gotstoy completion powershell | Out-String)
            $Alias
        } else {
            $Application
        }
    }
    'package' {
        Build-Project -All -ErrorAction Stop
    }
    'test' {
        $Application = Build-Project -ErrorAction Stop
        $ApplicationFolder = Split-Path -Parent $Application.Path
        Copy-Item -Path "$PSScriptRoot/gotstoy.dsc.resource.json" -Destination $ApplicationFolder
        $TestContainer = New-PesterContainer -Path 'acceptance.tests.ps1' -Data @{
            Application = $Application
        }
        Invoke-Pester -Container $TestContainer -Output Detailed
    }
}