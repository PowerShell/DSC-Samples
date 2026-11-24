$global:executable = Join-Path (Split-Path -Parent $PSScriptRoot) 'src' 'main.py'

Write-Verbose -Message "Executable path: $global:executable" -Verbose

Describe "TuxCtl acceptance tests - Help command" -Skip:(!$IsLinux) {
    It "Should display help information when --help is passed" {
        $result = & $global:executable --help
        $LASTEXITCODE | Should -Be 0
        $result | Should -Not -BeNullOrEmpty
    }
}

Describe "TuxCtl acceptance tests - Get command" -Skip:(!$IsLinux) {
    It "Should get a username using the --username option" {
        $result = & sudo $global:executable get --username root | ConvertFrom-Json
        $LASTEXITCODE | Should -Be 0
        $result | Should -Not -BeNullOrEmpty
        $result.username | Should -Be "root"
        $result.uid | Should -Be 0
        $result.gid | Should -Be 0
        $result.home | Should -Be "/root"
        $result.shell | Should -Be "/bin/bash"
        $result.groups | Should -Contain "root"
        $result._exist | Should -Be $true
    }

    It "Should work with all options" -Skip:(!($IsLinux)) {
        $result = & sudo $global:executable get --username root --uid 0 --gid 0 --home /root --shell /bin/bash | ConvertFrom-Json
        $LASTEXITCODE | Should -Be 0
        $result | Should -Not -BeNullOrEmpty
        $result.username | Should -Be "root"
        $result.uid | Should -Be 0
        $result.gid | Should -Be 0
        $result.home | Should -Be "/root"
        $result.shell | Should -Be "/bin/bash"
        $result.groups | Should -Contain "root"
        $result._exist | Should -Be $true
    }

    It "Should work with JSON input" {
        $in = @{username = "root"; uid = 0; gid = 0; shell = "/bin/bash"; home = "/root"} | ConvertTo-Json
        $result = & sudo $global:executable get --input $in | ConvertFrom-Json
        $LASTEXITCODE | Should -Be 0
        $result | Should -Not -BeNullOrEmpty
        $result.username | Should -Be "root"
        $result.uid | Should -Be 0
        $result.gid | Should -Be 0
        $result.home | Should -Be "/root"
        $result.shell | Should -Be "/bin/bash"
        $result.groups | Should -Contain "root"
        $result._exist | Should -Be $true
    }
}

Describe "TuxCtl acceptance tests - Set command" -Skip:(!$IsLinux) {
    It "Should set a username using the --username option" {
        & sudo $global:executable set --username testuser --password randompassword
        $LASTEXITCODE | Should -Be 0
        
        # Check if the user was created
        $result = & sudo $global:executable get --username testuser | ConvertFrom-Json
        $LASTEXITCODE | Should -Be 0
        $result.username | Should -Be "testuser"
    }
}

Describe "TuxCtl acceptance tests - Delete command" -Skip:(!$IsLinux) {
    It "Should delete a user using the --username option" {
        & sudo $global:executable delete --username testuser
        $LASTEXITCODE | Should -Be 0
        
        # Check if the user was deleted
        $result = & sudo $global:executable get --username testuser | ConvertFrom-Json
        $LASTEXITCODE | Should -Be 0
        $result._exist | Should -Be $false
    }
}

Describe "TuxCtl acceptance tests - Export command" -Skip:(!$IsLinux) {
    It "Should list all users" {
        $result = & sudo $global:executable export | ConvertFrom-Json
        $LASTEXITCODE | Should -Be 0
        $result.Count | Should -BeGreaterThan 1
    }
}