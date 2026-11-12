# Creates the application shortcut. It starts the app without a console window (pythonw).
#   scripts\make_shortcut.ps1                 -> shortcut in the project folder
#   scripts\make_shortcut.ps1 -Desktop        -> also on the Desktop
#   scripts\make_shortcut.ps1 -StartMenu      -> also in the Start menu
#   scripts\make_shortcut.ps1 -OutDir <dir>   -> only in the given folder
param(
    [switch]$Desktop,
    [switch]$StartMenu,
    [string]$OutDir = ''
)
. "$PSScriptRoot\_common.ps1"
Assert-Venv

$name = 'Voice Tutor'
$pythonw = Join-Path $VenvDir 'Scripts\pythonw.exe'
if (-not (Test-Path $pythonw)) { throw "pythonw.exe not found in $VenvDir" }
$icon = Join-Path $RepoRoot 'assets\voicetutor.ico'

$targets = @()
if ($OutDir) {
    $targets += $OutDir
} else {
    $targets += $RepoRoot
    if ($Desktop) { $targets += [Environment]::GetFolderPath('Desktop') }
    if ($StartMenu) { $targets += [Environment]::GetFolderPath('Programs') }
}

$shell = New-Object -ComObject WScript.Shell
foreach ($dir in $targets) {
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
    $path = Join-Path $dir "$name.lnk"
    $link = $shell.CreateShortcut($path)
    $link.TargetPath = $pythonw
    $link.Arguments = '-m voicetutor.launcher'
    $link.WorkingDirectory = $RepoRoot
    $link.Description = 'Voice Tutor'
    if (Test-Path $icon) { $link.IconLocation = "$icon,0" }
    $link.WindowStyle = 1
    $link.Save()
    Write-Host "shortcut: $path"
}
exit 0
