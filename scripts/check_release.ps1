# Release gate on a machine with an NVIDIA GPU: what CI cannot run.
# The gpu and e2e suites under both model profiles (SPEC 7), after the CI steps.
#   scripts\check_release.ps1
. "$PSScriptRoot\_common.ps1"
Assert-Venv
Set-AppEnv

$steps = @(
    @{ name = 'ci_local'; cmd = { & (Join-Path $PSScriptRoot 'ci_local.ps1') } },
    @{ name = 'gpu'; cmd = { & (Join-Path $PSScriptRoot 'test.ps1') gpu } },
    @{ name = 'e2e'; cmd = { & (Join-Path $PSScriptRoot 'test.ps1') e2e } },
    @{ name = 'gpu (compacto)'; cmd = { & (Join-Path $PSScriptRoot 'test.ps1') gpu --vt-profile compacto } },
    @{ name = 'e2e (compacto)'; cmd = { & (Join-Path $PSScriptRoot 'test.ps1') e2e --vt-profile compacto } }
)
$failed = @()
foreach ($s in $steps) {
    Write-Host "=== $($s.name) ===" -ForegroundColor Cyan
    & $s.cmd | Out-Host
    if ($LASTEXITCODE -ne 0) { $failed += $s.name }
}
if ($failed.Count -gt 0) {
    Write-Host "check_release: FAILED ($($failed -join ', '))" -ForegroundColor Red
    exit 1
}
Write-Host 'check_release: OK' -ForegroundColor Green
exit 0
