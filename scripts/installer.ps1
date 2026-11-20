# Installer helpers for setup.ps1 and uninstall.ps1 (plan item 4.1). Dot-source after
# _common.ps1 and requirements.ps1. Windows PowerShell 5.1 compatible; keep this file ASCII
# (messages live in requirements.messages.json).
#
# Tests call these functions with fake inputs (tests/test_installer_ps1.py).

# uv from its GitHub release, pinned by version and SHA-256 (checked on 2026-11-12 against the
# release's .sha256 file and the GitHub API asset digest).
$script:VtUvVersion = '0.13.7'
$script:VtUvSha256 = '0cdc5b38fe5a8168ed6a25814f5ba43c21d313dd3187314fccb37b7cec46e021'
$script:VtUvUrl = "https://github.com/astral-sh/uv/releases/download/$($script:VtUvVersion)/uv-x86_64-pc-windows-msvc.zip"
# uv installs this Python from python-build-standalone and checks the SHA-256 it ships for it.
$script:VtPythonVersion = '3.12'
# The longest file inside the Python environment is about 145 characters below the app folder;
# with the 260-character limit of Windows the folder path must stay short unless long paths are on.
$script:VtMaxAppDirLength = 80

function Format-VtText([string]$Text, [hashtable]$Values) {
    $out = $Text
    foreach ($k in $Values.Keys) { $out = $out.Replace('{' + $k + '}', [string]$Values[$k]) }
    return $out
}

function Test-VtAscii([string]$Text) {
    return -not ($Text -match '[^\x20-\x7E]')
}

function Get-VtShortPath([string]$Path) {
    # Windows 8.3 short name of a folder ('' when the volume keeps none).
    try {
        $fso = New-Object -ComObject Scripting.FileSystemObject
        return [string]$fso.GetFolder($Path).ShortPath
    } catch {
        return ''
    }
}

function Get-VtLongPathsEnabled {
    $key = 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem'
    $item = Get-ItemProperty -Path $key -Name LongPathsEnabled -ErrorAction SilentlyContinue
    if ($null -eq $item) { return $false }
    return ([int]$item.LongPathsEnabled -eq 1)
}

function Test-VtWritable([string]$Dir) {
    try {
        if (-not (Test-Path $Dir)) { New-Item -ItemType Directory -Force -Path $Dir | Out-Null }
        $probe = Join-Path $Dir ('.write-test-' + [guid]::NewGuid().ToString('N'))
        Set-Content -Path $probe -Value 'ok' -Encoding ASCII
        Remove-Item -Path $probe -Force
        return $true
    } catch {
        return $false
    }
}

function Test-VtInstallPath {
    # Problems with the app and data folders, before anything is downloaded:
    #   path_unwritable  - the folder cannot be written
    #   path_ascii       - the app folder has letters espeak-ng cannot read and no ASCII short name
    #   path_long        - the app folder path is too long for the Python environment
    # Spaces are fine. ShortPath, LongPaths and Writable are injectable for tests.
    param(
        [Parameter(Mandatory)][string]$AppDir,
        [Parameter(Mandatory)][string]$DataDir,
        [scriptblock]$ShortPath = { param($p) Get-VtShortPath $p },
        [Nullable[bool]]$LongPaths = $null,
        [scriptblock]$Writable = { param($p) Test-VtWritable $p }
    )
    if ($null -eq $LongPaths) { $LongPaths = Get-VtLongPathsEnabled }
    $problems = @()
    foreach ($dir in @($AppDir, $DataDir)) {
        if (-not (& $Writable $dir)) {
            $problems += [pscustomobject]@{ Id = 'path_unwritable'; Path = $dir }
        }
    }
    if (-not (Test-VtAscii $AppDir)) {
        $short = [string](& $ShortPath $AppDir)
        if (-not $short -or -not (Test-VtAscii $short)) {
            $problems += [pscustomobject]@{ Id = 'path_ascii'; Path = $AppDir }
        }
    }
    if ($AppDir.Length -gt $script:VtMaxAppDirLength -and -not $LongPaths) {
        $problems += [pscustomobject]@{ Id = 'path_long'; Path = $AppDir }
    }
    return $problems
}

function Get-VtSha256([string]$Path) {
    # .NET directly: works whatever PowerShell modules are available.
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $bytes = $sha.ComputeHash($stream)
    } finally {
        $stream.Dispose()
        $sha.Dispose()
    }
    return (($bytes | ForEach-Object { $_.ToString('x2') }) -join '')
}

function Test-VtSha256([string]$Path, [string]$Expected) {
    if (-not (Test-Path $Path)) { return $false }
    return ((Get-VtSha256 $Path) -eq $Expected.ToLowerInvariant())
}

function Install-VtUv {
    # Returns the path of uv.exe in ToolsDir, downloading and verifying the release if needed.
    param(
        [Parameter(Mandatory)][string]$ToolsDir,
        [string]$Url = $script:VtUvUrl,
        [string]$Sha256 = $script:VtUvSha256,
        [string]$Version = $script:VtUvVersion
    )
    $dir = Join-Path $ToolsDir "uv-$Version"
    $exe = Join-Path $dir 'uv.exe'
    if (Test-Path $exe) {
        $have = ((& $exe --version) -split ' ')[1]
        if ($have -eq $Version) { return $exe }
    }
    $downloads = Join-Path $ToolsDir 'downloads'
    New-Item -ItemType Directory -Force -Path $downloads | Out-Null
    $zip = Join-Path $downloads "uv-$Version.zip"
    if (-not (Test-VtSha256 $zip $Sha256)) {
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        try {
            $client = New-Object System.Net.WebClient
            try { $client.DownloadFile($Url, $zip) } finally { $client.Dispose() }
        } catch {
            Remove-Item -Force $zip -ErrorAction SilentlyContinue
            throw
        }
        if (-not (Test-VtSha256 $zip $Sha256)) {
            Remove-Item -Force $zip -ErrorAction SilentlyContinue
            throw "checksum:uv $Version"
        }
    }
    if (Test-Path $dir) { Remove-Item -Recurse -Force $dir }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($zip, $dir)
    if (-not (Test-Path $exe)) {
        $found = Get-ChildItem -Path $dir -Filter uv.exe -Recurse | Select-Object -First 1
        if ($null -eq $found) { throw "uv.exe not found in the uv archive" }
        Move-Item -Path $found.FullName -Destination $exe
    }
    return $exe
}

function Read-VtYesNo {
    # Asks in the user's language; Enter takes the default. Without a console (CI, tests) the
    # default answer is used.
    param(
        [Parameter(Mandatory)][string]$Question,
        [Parameter(Mandatory)][string]$YesLetters,
        [bool]$Default = $true
    )
    $interactive = [Environment]::UserInteractive -and -not [Console]::IsInputRedirected
    if (-not $interactive) { return $Default }
    $answer = Read-Host -Prompt $Question
    if ([string]::IsNullOrWhiteSpace($answer)) { return $Default }
    $first = $answer.Trim().Substring(0, 1).ToUpperInvariant()
    return ($YesLetters.ToUpperInvariant().Contains($first))
}

function Get-VtShortcutPaths([string]$Name = 'Personal AI English Teacher') {
    return @(
        (Join-Path ([Environment]::GetFolderPath('Desktop')) "$Name.lnk"),
        (Join-Path ([Environment]::GetFolderPath('Programs')) "$Name.lnk")
    )
}
