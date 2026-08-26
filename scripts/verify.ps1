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

$PublicationRegistryPath = Join-Path $RepositoryRoot 'mrd\documentation\04-publication-family-registry.mrd.json'
$PublicationRegistry = Get-Content -LiteralPath $PublicationRegistryPath -Raw | ConvertFrom-Json
$AllowedGeneratedMarkdownPrefixes = @(
    $PublicationRegistry.content.families |
        ForEach-Object { ($_.output.TrimEnd('/') + '/').Replace('\', '/') }
)
$TrackedMarkdown = @(& git -C $RepositoryRoot ls-files '*.md')
$UnexpectedMarkdown = @(
    $TrackedMarkdown | Where-Object {
        $Path = $_
        $AllowedGenerated = @($AllowedGeneratedMarkdownPrefixes | Where-Object { $Path.StartsWith($_) }).Count -gt 0
        $Path -ne 'AGENTS.md' -and -not $AllowedGenerated
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

    & $PythonCommand -m kis_mcp_doc --root . references-validate
    if ($LASTEXITCODE -ne 0) {
        throw "Documentation Reference Standard validation failed with exit code $LASTEXITCODE"
    }

    & $PythonCommand -m kis_mcp_doc --root . references-check-generated
    if ($LASTEXITCODE -ne 0) {
        throw "Documentation Reference Standard generated-output verification failed with exit code $LASTEXITCODE"
    }

    & $PythonCommand -m kis_mcp_doc --root . work-validate
    if ($LASTEXITCODE -ne 0) {
        throw "Work Management validation failed with exit code $LASTEXITCODE"
    }

    & $PythonCommand -m kis_mcp_doc --root . work-check-generated
    if ($LASTEXITCODE -ne 0) {
        throw "Work Management generated-output verification failed with exit code $LASTEXITCODE"
    }

    & $PythonCommand -m kis_mcp_doc --root . publications-validate
    if ($LASTEXITCODE -ne 0) {
        throw "Publication family registry validation failed with exit code $LASTEXITCODE"
    }

    & $PythonCommand -m kis_mcp_doc --root . publications-check-generated
    if ($LASTEXITCODE -ne 0) {
        throw "Registered publication generated-output verification failed with exit code $LASTEXITCODE"
    }

    & $PythonCommand -m kis_mcp_doc --root . site-validate
    if ($LASTEXITCODE -ne 0) {
        throw "Documentation site validation failed with exit code $LASTEXITCODE"
    }

    & $PythonCommand -m kis_mcp_doc --root . site-check-generated
    if ($LASTEXITCODE -ne 0) {
        throw "Documentation site generated-output verification failed with exit code $LASTEXITCODE"
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
