param(
    [string]$PolicyPath = (Join-Path (Split-Path -Parent $PSScriptRoot) 'tooling\windows-runtime.json')
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if (-not (Test-Path -LiteralPath $PolicyPath -PathType Leaf)) {
    throw "WINDOWS_RUNTIME_POLICY_MISSING: $PolicyPath"
}

$Policy = Get-Content -LiteralPath $PolicyPath -Raw | ConvertFrom-Json
if ($Policy.platform -ne 'windows') {
    throw "WINDOWS_RUNTIME_POLICY_INVALID: expected platform=windows"
}

function Test-CompliantPython {
    param([Parameter(Mandatory = $true)][string]$Candidate)

    if (-not (Test-Path -LiteralPath $Candidate -PathType Leaf)) {
        return $false
    }

    $Normalized = [System.IO.Path]::GetFullPath($Candidate)
    foreach ($Fragment in $Policy.python.forbidden_path_fragments) {
        if ($Normalized.IndexOf([string]$Fragment, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
            return $false
        }
    }

    $VersionText = (& $Normalized -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')").Trim()
    if ($LASTEXITCODE -ne 0) {
        return $false
    }
    $ActualVersion = [version]$VersionText
    $MinimumVersion = [version]([string]$Policy.python.minimum_version)
    if ($ActualVersion -lt $MinimumVersion) {
        return $false
    }

    if ([bool]$Policy.python.require_authenticode) {
        $Signature = Get-AuthenticodeSignature -FilePath $Normalized
        if ($Signature.Status -ne [System.Management.Automation.SignatureStatus]::Valid) {
            return $false
        }
        if ($null -eq $Signature.SignerCertificate) {
            return $false
        }
        $ExpectedPublisher = [string]$Policy.python.trusted_publisher_subject_contains
        if ($Signature.SignerCertificate.Subject.IndexOf($ExpectedPublisher, [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
            return $false
        }
    }

    return $true
}

$Candidates = [System.Collections.Generic.List[string]]::new()
$Launcher = Get-Command ([string]$Policy.python.preferred_launcher) -ErrorAction SilentlyContinue
if ($null -ne $Launcher) {
    $Selector = [string]$Policy.python.preferred_selector
    $Resolved = (& $Launcher.Source $Selector -c "import sys; print(sys.executable)").Trim()
    if ($LASTEXITCODE -eq 0 -and $Resolved) {
        $Candidates.Add($Resolved)
    }
}

$PythonCommands = @(Get-Command python.exe -All -ErrorAction SilentlyContinue)
foreach ($Command in $PythonCommands) {
    if ($Command.Source) {
        $Candidates.Add($Command.Source)
    }
}

foreach ($Candidate in @($Candidates | Select-Object -Unique)) {
    if (Test-CompliantPython -Candidate $Candidate) {
        Write-Output ([System.IO.Path]::GetFullPath($Candidate))
        exit 0
    }
}

throw 'COMPLIANT_SYSTEM_PYTHON_NOT_FOUND: install a Python Software Foundation signed CPython meeting tooling/windows-runtime.json; uv-managed Python is intentionally rejected.'
