# Creates a diagnostics archive for a bug report (plan item 4.7): versions, GPU, hardware
# profile, settings and logs. API keys, the Windows user name and conversation text are removed
# (voicetutor/diagnostics.py). Nothing is sent anywhere; attach the archive to an issue yourself.
#   right-click -> Run with PowerShell, or: scripts\collect_diagnostics.ps1 [-OutDir <folder>]
param([string]$OutDir = '')
. "$PSScriptRoot\_common.ps1"
Assert-Venv
Set-AppEnv
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

if (-not $OutDir) { $OutDir = [Environment]::GetFolderPath('Desktop') }
Push-Location $RepoRoot
try {
    $archive = & $VenvPython -m voicetutor.diagnostics --out $OutDir
    if ($LASTEXITCODE -ne 0) { throw 'diagnostics failed' }
} finally {
    Pop-Location
}
Write-Host $archive -ForegroundColor Green
exit 0
