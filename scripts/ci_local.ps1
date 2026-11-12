# The CI steps (.github/workflows/ci.yml), locally: lint and the fast suite.
# The fast suite includes i18n completeness, JSON schemas and data files, doc links, the GitHub
# templates and the repository hygiene scan (no keys, no personal data).
. "$PSScriptRoot\_common.ps1"
Assert-Venv
Set-AppEnv

$failed = @()
Push-Location $RepoRoot
try {
    Write-Host '=== ruff check ===' -ForegroundColor Cyan
    & $VenvPython -m ruff check voicetutor tests scripts
    if ($LASTEXITCODE -ne 0) { $failed += 'ruff check' }

    Write-Host '=== ruff format --check ===' -ForegroundColor Cyan
    & $VenvPython -m ruff format --check voicetutor tests scripts
    if ($LASTEXITCODE -ne 0) { $failed += 'ruff format' }

    Write-Host '=== fast suite ===' -ForegroundColor Cyan
    & $VenvPython -m pytest -m 'not gpu and not e2e and not live' -q
    if ($LASTEXITCODE -ne 0) { $failed += 'fast suite' }
} finally {
    Pop-Location
}

if ($failed.Count -gt 0) {
    Write-Host "ci_local: FAILED ($($failed -join ', '))" -ForegroundColor Red
    exit 1
}
Write-Host 'ci_local: OK' -ForegroundColor Green
exit 0
