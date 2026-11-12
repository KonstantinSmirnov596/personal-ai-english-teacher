# Builds the release archive (plan item 4.2): dist\VoiceTutor-<version>.zip, dist\SHA256SUMS.txt
# and the release notes draft. Nothing is uploaded; publishing is the owner's decision.
. "$PSScriptRoot\_common.ps1"
Assert-Venv
Set-AppEnv
Push-Location $RepoRoot
try {
    & $VenvPython (Join-Path $PSScriptRoot 'make_release.py') @args
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
