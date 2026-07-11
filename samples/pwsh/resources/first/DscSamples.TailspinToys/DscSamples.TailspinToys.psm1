# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

[DscResource()]
class PSTailspinToys {
    [DscProperty(Key)] [TailspinScope]
    $ConfigurationScope

    [DscProperty()] [TailspinEnsure]
    $Ensure = [TailspinEnsure]::Present

    [DscProperty()] [bool]
    $UpdateAutomatically

    [DscProperty()] [int] [ValidateRange(1, 90)]
    $UpdateFrequency

    hidden [PSTailspinToys]                               $CachedCurrentState
    hidden [PSCustomObject]                               $CachedData
    hidden [System.Management.Automation.ApplicationInfo] $CachedApplicationInfo
    hidden [string]                                       $CachedConfigurationFilePath

    [PSTailspinToys] Get() {
        $CurrentState = [PSTailspinToys]::new()

        $CurrentState.ConfigurationScope = $this.ConfigurationScope

        $FilePath = $this.GetConfigurationFilePath()

        if (!(Test-Path -path $FilePath)) {
            $CurrentState.Ensure     = [TailspinEnsure]::Absent
            $this.CachedCurrentState = $CurrentState

            return $CurrentState
        }

        $Data = $this.GetConfigurationData()

        if ($null -ne $Data.Updates.Automatic) {
            $CurrentState.UpdateAutomatically = $Data.Updates.Automatic
        }

        if ($null -ne $Data.Updates.CheckFrequency) {
            $CurrentState.UpdateFrequency = $Data.Updates.CheckFrequency
        }

        $this.CachedCurrentState = $CurrentState

        return $CurrentState
    }

    [bool] Test() {
        $CurrentState = $this.Get()

        if ($CurrentState.Ensure -ne $this.Ensure) {
            return $false
        }

        if ($CurrentState.Ensure -eq [TailspinEnsure]::Absent) {
            return $true
        }

        if ($CurrentState.UpdateAutomatically -ne $this.UpdateAutomatically) {
            return $false
        }

        if ($this.UpdateFrequency -eq 0) {
            return $true
        }

        if ($CurrentState.UpdateFrequency -ne $this.UpdateFrequency) {
            return $false
        }

        return $true
    }

    [void] Set() {
        if ($this.Test()) {
                return
        }

        Write-Warning "Setting for scope $($this.ConfigurationScope)"
        $CurrentState   = $this.CachedCurrentState
        $IsAbsent       = $CurrentState.Ensure -eq [TailspinEnsure]::Absent
        $ShouldBeAbsent = $this.Ensure         -eq [TailspinEnsure]::Absent

        if ($IsAbsent) {
            Write-Warning "Creating $($this.CachedConfigurationFilePath)"
            $this.Create()
        } elseif ($ShouldBeAbsent) {
            Write-Warning "Removing $($this.CachedConfigurationFilePath)"
            $this.Remove()
        } else {
            Write-Warning "Updating $($this.CachedConfigurationFilePath)"
            $this.Update()
        }
    }

    [void] Create() {
        $ErrorActionPreference = 'Stop'

        $Json = $this.ToConfigurationJson()

        $FilePath   = $this.GetConfigurationFilePath()
        $FolderPath = Split-Path -Path $FilePath

        if (!(Test-Path -Path $FolderPath)) {
            New-Item -Path $FolderPath -ItemType Directory -Force
        }

        Set-Content -Path $FilePath -Value $Json -Encoding utf8 -Force
    }

    [void] Remove() {
        Remove-Item -Path $this.GetConfigurationFilePath() -Force -ErrorAction Stop
    }

    [void] Update() {
        $ErrorActionPreference = 'Stop'

        $Json     = $this.ToConfigurationJson()
        $FilePath = $this.GetConfigurationFilePath()

        Set-Content -Path $FilePath -Value $Json -Encoding utf8 -Force
    }

    [string] ToConfigurationJson() {
        $config = @{
            updates = @{
                automatic = $this.UpdateAutomatically
            }
        }

        if ($this.CachedData) {
            # Copy unmanaged settings without changing the cached values
            $this.CachedData |
                Get-Member -MemberType NoteProperty |
                Where-Object -Property Name -NE -Value 'updates' |
                ForEach-Object -Process {
                    $setting = $_.Name
                    $config.$setting = $this.CachedData.$setting
                }

            # Add the checkFrequency to the hashtable if it is set in the cache
            if ($frequency = $this.CachedData.updates.checkFrequency) {
                $config.updates.checkFrequency = $frequency
            }
        }

        # If the user specified an UpdateFrequency, use that value
        if ($this.UpdateFrequency -ne 0) {
            $config.updates.checkFrequency = $this.UpdateFrequency
        }

        return ($config | ConvertTo-Json -Depth 99)
    }

    [System.Management.Automation.ApplicationInfo] GetApplicationInfo() {
        if ($null -ne $this.CachedApplicationInfo) {
            return $this.CachedApplicationInfo
        }

        try {
            $Parameters = @{
                Name        = 'tstoy'
                CommandType = 'Application'
                ErrorAction = 'Stop'
            }
            $this.CachedApplicationInfo = Get-Command @Parameters
            | Select-Object -First 1
        } catch [System.Management.Automation.CommandNotFoundException] {
            throw [System.Management.Automation.CommandNotFoundException]::new(
                "tstoy application not found, unable to retrieve path to configuration file",
                $_
            )
        }

        return $this.CachedApplicationInfo
    }

    [string] GetConfigurationFilePath() {
        if (-not ([string]::IsNullOrEmpty($this.CachedConfigurationFilePath))) {
            return $this.CachedConfigurationFilePath
        }

        $this.GetApplicationInfo()

        $Arguments = @(
            'show'
            'path'
            $this.ConfigurationScope.ToString().ToLower()
        )

        $this.CachedConfigurationFilePath = & $this.CachedApplicationInfo @Arguments

        return $this.CachedConfigurationFilePath
    }

    [PSCustomObject] GetConfigurationData() {
        if ($null -ne $this.CachedData) {
            return $this.CachedData
        }

        $ConfigurationFilePath = $this.GetConfigurationFilePath()

        if (-not (Test-Path -Path $ConfigurationFilePath)) {
            return $null
        }

        try {
            $GetParameters = @{
                Path        = $ConfigurationFilePath
                Raw         = $true
            }

            $this.CachedData = Get-Content @GetParameters
            | ConvertFrom-Json -ErrorAction Stop
        } catch [Newtonsoft.Json.JsonReaderException] {
            throw [Newtonsoft.Json.JsonReaderException]::new(
                "Unable to load TSToy configuration data from $ConfigurationFilePath",
                $_
            )
        }

        return $this.CachedData
    }
}

enum TailspinScope {
    Machine
    User
}

enum TailspinEnsure {
    Absent
    Present
}
