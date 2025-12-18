param (
    [string]$Name = 'pythontstoy'
)

BeforeAll {
    $oldPath = $env:Path
    $env:Path += [System.IO.Path]::PathSeparator + (Join-Path (Split-Path $PSScriptRoot -Parent) 'dist')

    if ($IsWindows) {
        $script:machinePath = Join-Path $env:ProgramData 'tstoy' 'config.json'
        $script:userPath = Join-Path $env:APPDATA 'tstoy' 'config.json'
    }
    else {
        $script:machinePath = Join-Path $env:HOME '.config' 'tstoy' 'config.json'
        $script:userPath = Join-Path $env:HOME '.config' 'tstoy' 'config.json'
    }
}

Describe "TSToy acceptance tests - Schema command" {
    It "Should return schema" {
        $schema = & $Name schema | ConvertFrom-Json
        $schema | Should -Not -BeNullOrEmpty
        $LASTEXITCODE | Should -Be 0
        $schema.required | Should -Contain 'scope'
        $schema.properties.scope | Should -Not -BeNullOrEmpty
        $schema.properties.updateFrequency | Should -Not -BeNullOrEmpty
        $schema.properties.updateAutomatically | Should -Not -BeNullOrEmpty
        $schema.properties._exist | Should -Not -BeNullOrEmpty
    }
}

Describe 'TSToy acceptance tests - Get command' {
    Context "Help command" {
        It 'Should return help' {
            $help = & $Name --help
            $help | Should -Not -BeNullOrEmpty
            $LASTEXITCODE | Should -Be 0
        }
    }
    
    Context "Input validation" {
        It 'Should fail with invalid input' {
            $out = & $Name get --input '{}' 2>&1
            $LASTEXITCODE | Should -Be 1
            $out[1] | Should -BeLike '*"ERROR"*"message":"Input validation failed: Validation error: ''scope'' is a required property"*'
        }
    }

    Context "Scope validation" -ForEach @( @{ scope = 'user' }, @{ scope = 'machine' } ) {
        BeforeAll {
            if ($IsWindows) {
                Remove-Item -Path $script:userPath -ErrorAction Ignore
                Remove-Item -Path $script:machinePath -ErrorAction Ignore
            }
            elseif ($IsLinux) {
                Remove-Item -Path $script:userPath -ErrorAction Ignore
                Remove-Item -Path $script:machinePath -ErrorAction Ignore
            }
        }

        It "Should not exist scope: <scope>" {
            $out = & $Name get --input ($_ | ConvertTo-Json -Depth 10) | ConvertFrom-Json
            $LASTEXITCODE | Should -Be 0
            $out._exist | Should -BeFalse
        }

        It 'Should exist when file is present' {
            $config = @{
                updates = @{
                    updateAutomatically = $false
                    updateFrequency     = 180
                }
            } | ConvertTo-Json -Depth 10

            if ($_.scope -eq 'user') {
                $scriptPath = $script:userPath
            }
            else {
                $scriptPath = $script:machinePath
            }

            New-Item -Path $scriptPath -ItemType File -Value $config -Force | Out-Null

            $out = & $Name get --input ($_ | ConvertTo-Json -Depth 10) | ConvertFrom-Json
            $LASTEXITCODE | Should -Be 0
            $out._exist | Should -BeTrue
            $out.updateFrequency | Should -Be 180
            $out.updateAutomatically | Should -BeFalse
        }
    }
}

Describe "TSToy acceptance tests - Set command" {
    It "Should set user scope" {
        $config = @{
            scope = 'user'
            updateAutomatically = $false
            updateFrequency = 180
        } | ConvertTo-Json -Depth 10

        & $Name set --input $config
        $LASTEXITCODE | Should -Be 0

        $out = & $Name get --input $config | ConvertFrom-Json
        $out | Should -Not -BeNullOrEmpty
        $out._exist | Should -BeTrue 
        $out.updateFrequency | Should -Be 180
        $out.updateAutomatically | Should -BeFalse
    }

    It "Should set machine scope" {
        $config = @{
            scope = 'machine'
            updateAutomatically = $true
            updateFrequency = 10
        } | ConvertTo-Json -Depth 10

        & $Name set --input $config
        $LASTEXITCODE | Should -Be 0

        $out = & $Name get --input $config | ConvertFrom-Json
        $out | Should -Not -BeNullOrEmpty
        $out._exist | Should -BeTrue
        $out.updateFrequency | Should -Be 10
        $out.updateAutomatically | Should -BeTrue
    }

    It "Should delete user scope" {
        $config = @{
            scope = 'user'
            _exist = $false
        } | ConvertTo-Json -Depth 10

        & $Name set --input $config
        $LASTEXITCODE | Should -Be 0

        $out = & $Name get --input $config | ConvertFrom-Json
        $out._exist | Should -BeFalse
    }

    It "Should delete machine scope" {
        $config = @{
            scope = 'machine'
            _exist = $false
        } | ConvertTo-Json -Depth 10

        & $Name set --input $config
        $LASTEXITCODE | Should -Be 0

        $out = & $Name get --input $config | ConvertFrom-Json
        $out._exist | Should -BeFalse
    }
}