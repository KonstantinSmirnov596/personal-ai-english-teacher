# Stage acceptance: scripts\check_stage.ps1 <N>
# Runs the suites of stage N and all earlier stages, checks required tests, reports and files.
param(
    [Parameter(Mandatory, Position = 0)][int]$Stage
)
. "$PSScriptRoot\_common.ps1"

$setupOk = $true
if ($Stage -ge 0) {
    # Stage 0 criterion: a repeated setup run finishes without errors. Developer flavour: test
    # tools included, no Desktop or Start menu shortcuts, the app is not started.
    Write-Host '=== repeated setup run ===' -ForegroundColor Cyan
    & (Join-Path $PSScriptRoot 'setup.ps1') -Dev -Shortcuts no -NoLaunch
    if ($LASTEXITCODE -ne 0) { $setupOk = $false }
}

Assert-Venv
Set-AppEnv
Push-Location $RepoRoot
try {
    & $VenvPython (Join-Path $PSScriptRoot 'check_stage.py') $Stage
    $code = $LASTEXITCODE
} finally {
    Pop-Location
}

if (-not $setupOk) {
    Write-Host '  FAIL: repeated scripts\setup.ps1 run failed' -ForegroundColor Red
    exit 1
}
exit $code
