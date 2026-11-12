# Starts the application.
. "$PSScriptRoot\_common.ps1"

$launcher = Join-Path $RepoRoot 'voicetutor\launcher.py'
if (-not (Test-Path $launcher)) {
    Write-Host 'The application is not built yet: stage 0 only verifies the hardware and pins versions.'
    exit 1
}

Assert-Venv
Set-TrainerEnv
& $VenvPython -m voicetutor.launcher @args
exit $LASTEXITCODE
