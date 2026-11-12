# Shared helpers for the project scripts. Dot-source it: . "$PSScriptRoot\_common.ps1"
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$script:VenvDir = Join-Path $RepoRoot '.venv'
$script:VenvPython = Join-Path $VenvDir 'Scripts\python.exe'
$script:ToolsDir = Join-Path $RepoRoot '.tools'
# Python for the app, installed by uv; kept inside the app folder (uninstall.cmd removes it).
$script:PythonDir = Join-Path $ToolsDir 'python'

function Get-AppDataDir {
    if ($env:VOICETUTOR_DATA_DIR) { return $env:VOICETUTOR_DATA_DIR }
    return (Join-Path $env:LOCALAPPDATA 'VoiceTutor')
}

function Get-AppModelsDir {
    if ($env:VOICETUTOR_MODELS_DIR) { return $env:VOICETUTOR_MODELS_DIR }
    return (Join-Path (Get-AppDataDir) 'models')
}

function Set-AppEnv {
    $env:PYTHONUTF8 = '1'
    $env:PYTHONIOENCODING = 'utf-8'
    $env:HF_HOME = Get-AppModelsDir
    $env:HF_HUB_DISABLE_TELEMETRY = '1'
    $env:UV_PROJECT_ENVIRONMENT = $VenvDir
    $env:UV_PYTHON_DOWNLOADS = 'never'
    $env:UV_PYTHON_INSTALL_DIR = $PythonDir
    $env:UV_NO_PROGRESS = '1'
    # The package cache stays inside the app folder too, unless a developer points it elsewhere.
    if (-not $env:UV_CACHE_DIR) { $env:UV_CACHE_DIR = Join-Path $ToolsDir 'uv-cache' }
}

function Invoke-Checked {
    # Runs a native command and throws if it exits with a non-zero code.
    param(
        [Parameter(Mandatory)][string]$Exe,
        [Parameter(ValueFromRemainingArguments)][string[]]$Arguments
    )
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $Exe $($Arguments -join ' ')"
    }
}

function Assert-Venv {
    if (-not (Test-Path $VenvPython)) {
        throw "Python environment not found at $VenvDir. Run scripts\setup.ps1 first."
    }
}
