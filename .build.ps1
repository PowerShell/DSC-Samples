#!/usr/bin/env pwsh
#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#
#requires -Version 7.2
#requires -Module InvokeBuild

[cmdletbinding()]
param(
  [string]$SiteBaseUrl
)

task CheckPrereqs {
  if (-not (Get-Command hugo -ErrorAction Ignore)) {
    throw "Hugo is not installed. Please install Hugo extended edition from https://gohugo.io/getting-started/installing/"
  }
  $HugoVersion = hugo version
  if (-not ($HugoVersion -match 'hugo v(?<version>\d+\.\d+\.\d+)[^+]+\+extended')) {
    throw "Hugo is installed but not the extended edition. Please install Hugo extended edition from https://gohugo.io/getting-started/installing/"
  }
  if ([version]($Matches.version) -lt [version]'0.115.0') {
    throw "Hugo is installed but the version is too old. Please install Hugo extended edition, minimum version 0.115.0, from https://gohugo.io/getting-started/installing/"
  }
  if (-not (Get-Command go)) {
    throw "Go is not installed. Please install Go 1.19 or higher from https://golang.org/dl/"
  }
}

task PrepareSite CheckPrereqs, {
  # Nothing to do yet, included for future use.
}

task BuildSite PrepareSite, {
  Push-Location -Path "$BuildRoot/.site"
  if ([string]::IsNullOrEmpty($SiteBaseUrl)) {
    $SiteBaseUrl = $env:DEPLOY_PRIME_URL
  }
#   if ([string]::IsNullOrEmpty($SiteBaseUrl)) {
#     $SiteBaseUrl = 'https://quiet-snickerdoodle-38a82c.netlify.app/'
#   }
  hugo --gc --minify -b $SiteBaseUrl
  Pop-Location
}

task ServeSite PrepareSite, {
  Push-Location -Path "$BuildRoot/.site"
  hugo server
  Pop-Location
}
