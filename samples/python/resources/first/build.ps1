[CmdletBinding()]
param (
    [ValidateSet('build', 'test')]
    [string]$mode = 'build',
    [string]$name = 'pythontstoy'
)

function Build-PythonProject {
    [CmdletBinding()]
    param (
        [Parameter()]
        [string]$Name 
    )
    begin {
        Write-Verbose -Message "Starting Python project build process"

        $sourceDir = Join-Path -Path $PSScriptRoot -ChildPath 'src'
        $outputDir = Join-Path -Path $PSScriptRoot -ChildPath 'dist'
    }

    process {
        Install-Uv

        Push-Location -Path $sourceDir -ErrorAction Stop

        try {
            # Create virtual environment
            & uv venv

            # Activate it
            & .\.venv\Scripts\activate.ps1

            # Sync all the dependencies
            & uv sync

            # Create executable
            $pyInstallerArgs = @(
                'main.py',
                '-F',
                '--clean',
                '--distpath', $outputDir,
                '--name', $Name
            )
            & pyinstaller.exe @pyInstallerArgs
        }
        finally {
            deactivate
            Pop-Location -ErrorAction Ignore
        }
    }

    end {
        Write-Verbose -Message "Python project build process completed"
    }
}

function Install-Uv() {
    begin {
        Write-Verbose -Message "Installing Uv dependencies"
    }

    process {
        if ($IsWindows) {
            if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
                Write-Verbose -Message "Installing uv package manager on Windows"
                Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression

            }
            $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
        }
        elseif ($IsLinux) {
            curl -LsSf https://astral.sh/uv/install.sh | sh
        }
    }

    end {
        Write-Verbose -Message "Uv installation process completed"
    }
}

switch ($mode) {
    'build' {
        Build-PythonProject -Name $name
    }
    'test' {
        Build-PythonProject -Name $name

        $testContainer = New-PesterContainer -Path (Join-Path 'tests' 'acceptance.tests.ps1') -Data @{ 
            Name = $name
        }

        Invoke-Pester -Container $testContainer -Output Detailed
    }

}