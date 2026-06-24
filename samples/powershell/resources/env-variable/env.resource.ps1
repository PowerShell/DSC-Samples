[CmdletBinding()]
param(
    [ValidateSet('get', 'set', 'delete')]
    [string]$Operation,
    [Parameter(Mandatory, ValueFromPipeline)]
    [string]$InputObject
)

function Write-DSCTrace
{
    param(
        [ValidateSet('info', 'warn', 'error')]
        [string]$Level,
        [ValidateNotNullOrEmpty()]
        [string]$Message
    )

    # We MUST follow a prescriptive format for logs/traces.
    $Host.UI.WriteErrorLine((@{ $Level = $Message } | ConvertTo-Json -Compress))
}

Write-DSCTrace warn "This DSC Resource displays unredacted environment variable values."

Set-Variable -Option ReadOnly -Name Parameters -Value ($Input | ConvertFrom-Json)
Set-Variable -Option Constant -Name ExitCodeParameterError -Value 2

if ($Parameters.scope -notin ('user', 'machine'))
{
    Write-DSCTrace error "Invalid parameter 'scope': $($Parameters.scope)."

    # FIXME: Ignored? DSC always returns 1.
    exit $ExitCodeParameterError
}

Set-Variable -Option ReadOnly -Name EnvironmentVariableTarget -Value ([System.EnvironmentVariableTarget]$Parameters.scope)

$result = @{ name = $null ; value = $null ; scope = $null }

switch ($Operation)
{
    'get'
    {
        if ([string]::IsNullOrWhiteSpace($Parameters.name))
        {
            Write-DSCTrace error "Invalid parameter 'name': $($Parameters.name)."

            exit $ExitCodeParameterError
        }

        $value = [System.Environment]::GetEnvironmentVariable($Parameters.name, $EnvironmentVariableTarget)
    
        # Assume env var set to null doesn't exist.
        $result['name'] = if ($null -ne $value) { $Parameters.name } else { $null }
        $result['value'] = $value
        $result['scope'] = $EnvironmentVariableTarget.ToString().ToLower()
    }
    'set'
    {
        if ([string]::IsNullOrWhiteSpace($Parameters.name) -or [string]::IsNullOrEmpty($Parameters.value))
        {
            Write-DSCTrace error "Invalid value for parameter 'name' ($($Parameters.name)) or parameter 'value' ($($Parameters.value))."

            exit $ExitCodeParameterError
        }

        if ($EnvironmentVariableTarget -eq [System.EnvironmentVariableTarget]::Machine)
        {
            Write-DSCTrace error "The 'set' operation for the scope 'machine' is not implemented."

            exit 1
        }

        Write-DSCTrace info "Setting environment variable '$($Parameters.name)' to '$($Parameters.value)' ($EnvironmentVariableTarget)."

        [System.Environment]::SetEnvironmentVariable($Parameters.name, $Parameters.value, $EnvironmentVariableTarget)

        $result["name"] = $Parameters.name
        $result["value"] = [System.Environment]::GetEnvironmentVariable($Parameters.name, $EnvironmentVariableTarget)
        $result["scope"] = $EnvironmentVariableTarget.ToString().ToLower()
    }
    'delete'
    {
        if ([string]::IsNullOrWhiteSpace($Parameters.name))
        {
            Write-DSCTrace error "Invalid parameter 'name': $($Parameters.name)"

            exit $ExitCodeParameterError
        }

        if ($EnvironmentVariableTarget -eq [System.EnvironmentVariableTarget]::Machine)
        {
            Write-DSCTrace error "The 'delete' operation for the scope 'machine' is not implemented."

            exit 1
        }

        Write-DSCTrace info "Deleting environment variable '$($Parameters.name)' ($EnvironmentVariableTarget)."

        [System.Environment]::SetEnvironmentVariable($Parameters.name, $null, $EnvironmentVariableTarget)

        $result["name"] = $Parameters.name
        $result["value"] = [System.Environment]::GetEnvironmentVariable($Parameters.name, $EnvironmentVariableTarget)
        $result["scope"] = $EnvironmentVariableTarget.ToString().ToLower()
    }
    default
    {
        Write-DSCTrace error "Operation not implemented: $Operation."

        exit 1
    }
}

return $result | ConvertTo-Json -Compress

