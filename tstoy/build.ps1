# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[CmdletBinding()]
param (
  [Parameter()]
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
        [string[]]$Arguments = @(
            '--clean'
            '--snapshot'
        )
        $DistFolder   = "$PSScriptRoot/dist"
        $LatestFolder = "$PSScriptRoot/latest"
    }
    process {
        if ($All) {
            $Arguments += @(
                '--skip-publish'
                '--skip-announce'
                '--skip-validate'
            )
            goreleaser release @Arguments
            
            if (Test-Path $LatestFolder) {
                Remove-Item -Path $LatestFolder/* -Force -Recurse
            } else {
                mkdir $LatestFolder
            }

            Get-ChildItem -Path $DistFolder -File
            | Where-Object -FilterScript { $_.Name -match '\.(txt|tar\.gz|zip)'}
            | Move-Item -Destination $LatestFolder
        } else {
            $Arguments += @(
                '--single-target'
            )
            goreleaser build @Arguments
            Get-Command "./dist/tstoy*/tstoy*" -ErrorAction Stop
        }
    }

    end { }
}

switch ($Target) {
    'build' {
        $Application = Build-Project
        if ($AddToPath) {
            $ApplicationFolder = Split-Path -Parent $Application.Path
            $PathSeparator = [System.IO.Path]::PathSeparator
            if ($ApplicationFolder -notin ($env:PATH -split $PathSeparator)) {
                $env:PATH = $ApplicationFolder + $PathSeparator + $env:PATH
            }
        }
        if ($Initialize) {
            $Alias = Set-Alias -Name tstoy -Value $Application.Path -PassThru
            Invoke-Expression $(tstoy completion powershell | Out-String)
            $Alias
        } else {
            $Application
        }
    }
    'package' {
        Build-Project -All
    }
    'test' {
        $Application = Build-Project
        $TestContainer = New-PesterContainer -Path 'acceptance.tests.ps1' -Data @{
            Application = $Application
        }
        Invoke-Pester -Container $TestContainer -Output Detailed
    }
}