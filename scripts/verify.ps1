param(
    [switch]$SkipDependencySync
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepositoryRoot = Split-Path -Parent $PSScriptRoot
$LockPath = Join-Path $RepositoryRoot 'uv.lock'

if (-not (Test-Path -LiteralPath $LockPath -PathType Leaf)) {
    throw 'DEPENDENCY_LOCK_MISSING: uv.lock is required for canonical verification.'
}

if ($env:KIS_EXACT_SHA) {
    $ActualSha = (& git -C $RepositoryRoot rev-parse HEAD).Trim().ToLowerInvariant()
    $ExpectedSha = $env:KIS_EXACT_SHA.Trim().ToLowerInvariant()
    if ($ActualSha -ne $ExpectedSha) {
        throw "EXACT_HEAD_MISMATCH: expected $ExpectedSha, found $ActualSha"
    }
}

$AllowedGeneratedMarkdownPrefix = 'generated/governance-spec/'
$TrackedMarkdown = @(& git -C $RepositoryRoot ls-files '*.md')
$UnexpectedMarkdown = @(
    $TrackedMarkdown | Where-Object {
        $_ -ne 'AGENTS.md' -and -not $_.StartsWith($AllowedGeneratedMarkdownPrefix)
    }
)
if ($UnexpectedMarkdown.Count -gt 0) {
    throw "HAND_AUTHORED_MARKDOWN_FORBIDDEN: $($UnexpectedMarkdown -join ', ')"
}
$BeforeStatus = @(& git -C $RepositoryRoot status --porcelain --untracked-files=no)
$PythonCommand = 'python'

if (-not $SkipDependencySync) {
    $env:UV_OFFLINE = '1'
    & uv sync --offline --locked --all-groups --project $RepositoryRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Offline locked dependency synchronization failed with exit code $LASTEXITCODE"
    }
    $PythonCommand = Join-Path $RepositoryRoot '.venv\Scripts\python.exe'
}
elseif ($env:GITHUB_ACTIONS -eq 'true') {
    $PythonCommand = Join-Path $RepositoryRoot '.venv\Scripts\python.exe'
}

Push-Location $RepositoryRoot
try {
    & $PythonCommand -m pytest -q
    if ($LASTEXITCODE -ne 0) {
        throw "Test verification failed with exit code $LASTEXITCODE"
    }

    & $PythonCommand -m kis_mcp_doc --root . validate
    if ($LASTEXITCODE -ne 0) {
        throw "Governance validation failed with exit code $LASTEXITCODE"
    }

    & $PythonCommand -m kis_mcp_doc --root . check-generated
    if ($LASTEXITCODE -ne 0) {
        throw "Generated-output verification failed with exit code $LASTEXITCODE"
    }

    & git diff --check
    if ($LASTEXITCODE -ne 0) {
        throw "Whitespace verification failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}

$AfterStatus = @(& git -C $RepositoryRoot status --porcelain --untracked-files=no)
if (($BeforeStatus -join "`n") -ne ($AfterStatus -join "`n")) {
    throw 'VERIFICATION_MUTATED_TRACKED_STATE: canonical verification changed tracked files.'
}

Write-Host 'Verification passed: locked dependencies, tests, governance validation, generated output, and repository policy are consistent.'
