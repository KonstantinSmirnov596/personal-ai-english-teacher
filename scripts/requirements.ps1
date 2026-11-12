# Hardware and system requirements, checked by setup.ps1 before anything is downloaded.
#
# Get-VtFacts reads this computer; Test-VtRequirements only looks at the facts it is given, so
# tests feed it fake facts (tests/test_requirements_ps1.py). Thresholds match
# voicetutor/profiles.py; sources are in docs/reports/stage0.md ("Hardware facts").
# Messages (English, Spanish, Brazilian Portuguese) are in requirements.messages.json.
#
# Runs on Windows PowerShell 5.1 (what install.cmd uses) and PowerShell 7. Keep it ASCII.
#
#   . scripts\requirements.ps1
#   if (-not (Invoke-VtRequirements -RepoRoot $RepoRoot)) { exit 1 }

$script:VtMinDriver = [version]'572.61'
$script:VtMinComputeCap = [version]'7.5'
$script:VtMinVramMb = 5800        # a 6 GB card reports about 6140 MiB
$script:VtMinRamMb = 15000        # 16 GB installed shows about 15.7 GB to Windows
$script:VtMinWindowsBuild = 19045 # Windows 10 22H2
# Disk space for a first installation (measured on the development machine, rounded up):
# Python environment 4.9 GB next to the app; models 3.1 GB, package cache 4.9 GB and 2 GB for
# recordings, logs and the database in the user's local application data.
$script:VtNeedAppMb = 5500
$script:VtNeedDataMb = 10000

function Get-VtLanguage {
    param([string]$Culture = (Get-UICulture).Name)
    if ($Culture -like 'es*') { return 'es' }
    if ($Culture -like 'pt*') { return 'pt-BR' }
    return 'en'
}

function Format-VtSize([double]$Mb) {
    return ('{0:N1} GB' -f ($Mb / 1024))
}

function Get-VtNvidiaSmi {
    # First NVIDIA GPU as nvidia-smi reports it (the app uses the same one), or $null.
    $exe = $null
    $cmd = Get-Command 'nvidia-smi.exe' -ErrorAction SilentlyContinue
    if ($cmd) { $exe = $cmd.Source }
    if (-not $exe) {
        $candidate = Join-Path $env:SystemRoot 'System32\nvidia-smi.exe'
        if (Test-Path $candidate) { $exe = $candidate }
    }
    if (-not $exe) { return $null }
    try {
        $out = & $exe '--query-gpu=name,driver_version,compute_cap,memory.total' '--format=csv,noheader,nounits' 2>$null
    } catch {
        return $null
    }
    if ($LASTEXITCODE -ne 0 -or -not $out) { return $null }
    foreach ($line in @($out)) {
        $parts = @($line -split ',' | ForEach-Object { $_.Trim() })
        if ($parts.Count -ne 4) { continue }
        $vram = 0
        if (-not [int]::TryParse(($parts[3] -split '\.')[0], [ref]$vram)) { continue }
        return [pscustomobject]@{
            Name        = $parts[0]
            Driver      = $parts[1]
            ComputeCap  = $parts[2]
            VramTotalMb = $vram
        }
    }
    return $null
}

function Get-VtDriveFreeMb([string]$Path) {
    $root = [System.IO.Path]::GetPathRoot([System.IO.Path]::GetFullPath($Path))
    $drive = New-Object System.IO.DriveInfo($root)
    return [pscustomobject]@{ Drive = $root.TrimEnd('\'); FreeMb = [int64]($drive.AvailableFreeSpace / 1MB) }
}

function Get-VtFacts {
    # Everything Test-VtRequirements needs, read from this computer.
    param(
        [Parameter(Mandatory)][string]$AppDir,
        [Parameter(Mandatory)][string]$DataDir
    )
    $os = Get-CimInstance Win32_OperatingSystem
    $adapters = @(Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name } | Where-Object { $_ })

    # Space already taken by an earlier installation is not needed again.
    $needApp = $script:VtNeedAppMb
    if (Test-Path (Join-Path $AppDir '.venv\Scripts\python.exe')) { $needApp = 500 }
    $needData = $script:VtNeedDataMb
    if (Test-Path (Join-Path $DataDir 'models')) { $needData = 2048 }

    $disks = @()
    $app = Get-VtDriveFreeMb $AppDir
    $data = Get-VtDriveFreeMb (Split-Path $DataDir -Parent)
    if ($app.Drive -eq $data.Drive) {
        $disks += [pscustomobject]@{ Drive = $app.Drive; FreeMb = $app.FreeMb; NeedMb = $needApp + $needData }
    } else {
        $disks += [pscustomobject]@{ Drive = $app.Drive; FreeMb = $app.FreeMb; NeedMb = $needApp }
        $disks += [pscustomobject]@{ Drive = $data.Drive; FreeMb = $data.FreeMb; NeedMb = $needData }
    }

    return [pscustomobject]@{
        WindowsBuild = [int]$os.BuildNumber
        RamTotalMb   = [int64]([int64]$os.TotalVisibleMemorySize / 1024)
        Adapters     = $adapters
        Nvidia       = Get-VtNvidiaSmi
        Disks        = $disks
    }
}

function New-VtCheck([string]$Id, [bool]$Ok, [bool]$Blocking, [string]$Value, [string]$Required, [string]$Name, [string]$Message) {
    if (-not $Message) { $Message = $Id }
    return [pscustomobject]@{
        Id = $Id; Ok = $Ok; Blocking = $Blocking; Value = $Value; Required = $Required
        Name = $Name; Message = $Message
    }
}

function ConvertTo-VtVersion([string]$Text) {
    $v = $null
    if ([version]::TryParse(($Text -replace '[^0-9.]', ''), [ref]$v)) { return $v }
    return $null
}

function Test-VtRequirements {
    # One check per requirement; Blocking checks stop the installation.
    param([Parameter(Mandatory)]$Facts)
    $checks = @()
    $nv = $Facts.Nvidia
    $nvidiaAdapters = @($Facts.Adapters | Where-Object { $_ -match 'NVIDIA' })

    if ($null -eq $nv) {
        if ($nvidiaAdapters.Count -gt 0) {
            # An NVIDIA card is there, but nvidia-smi (installed with the driver) is not.
            $checks += New-VtCheck 'gpu' $true $true $nvidiaAdapters[0] 'NVIDIA GPU' $nvidiaAdapters[0]
            $checks += New-VtCheck 'driver' $false $true 'none' $script:VtMinDriver.ToString() $nvidiaAdapters[0] 'driver_missing'
        } else {
            $found = 'none'
            if (@($Facts.Adapters).Count -gt 0) { $found = (@($Facts.Adapters) -join ', ') }
            $checks += New-VtCheck 'gpu' $false $true $found 'NVIDIA GPU' ''
        }
    } else {
        $checks += New-VtCheck 'gpu' $true $true $nv.Name 'NVIDIA GPU' $nv.Name
        $driver = ConvertTo-VtVersion $nv.Driver
        $driverOk = ($null -ne $driver) -and ($driver -ge $script:VtMinDriver)
        $checks += New-VtCheck 'driver' $driverOk $true $nv.Driver $script:VtMinDriver.ToString() $nv.Name
        $cc = ConvertTo-VtVersion $nv.ComputeCap
        $ccOk = ($null -ne $cc) -and ($cc -ge $script:VtMinComputeCap)
        $checks += New-VtCheck 'architecture' $ccOk $true $nv.ComputeCap $script:VtMinComputeCap.ToString() $nv.Name
        $vramOk = [int64]$nv.VramTotalMb -ge $script:VtMinVramMb
        $checks += New-VtCheck 'vram' $vramOk $true (Format-VtSize $nv.VramTotalMb) '6 GB' $nv.Name
    }

    foreach ($disk in @($Facts.Disks)) {
        $ok = [int64]$disk.FreeMb -ge [int64]$disk.NeedMb
        $checks += New-VtCheck 'disk' $ok $true (Format-VtSize $disk.FreeMb) (Format-VtSize $disk.NeedMb) $disk.Drive
    }
    $ramOk = [int64]$Facts.RamTotalMb -ge $script:VtMinRamMb
    $checks += New-VtCheck 'ram' $ramOk $false (Format-VtSize $Facts.RamTotalMb) '16 GB' ''
    if ([int]$Facts.WindowsBuild -gt 0) {
        $winOk = [int]$Facts.WindowsBuild -ge $script:VtMinWindowsBuild
        $checks += New-VtCheck 'windows' $winOk $false ([string]$Facts.WindowsBuild) "$($script:VtMinWindowsBuild) (Windows 10 22H2)" ''
    }
    return $checks
}

function Get-VtMessages([string]$Root = $PSScriptRoot) {
    $path = Join-Path $Root 'requirements.messages.json'
    return (Get-Content -Raw -Encoding UTF8 -Path $path | ConvertFrom-Json)
}

function Format-VtMessage {
    param([Parameter(Mandatory)]$Check, [Parameter(Mandatory)]$Messages, [string]$Language = 'en')
    $table = $Messages.$Language
    if ($null -eq $table) { $table = $Messages.en }
    $text = [string]$table.($Check.Message)
    $text = $text.Replace('{value}', [string]$Check.Value).Replace('{required}', [string]$Check.Required)
    return $text.Replace('{name}', [string]$Check.Name)
}

function Get-VtDocLink([string]$RepoRoot, [string]$Language, [string]$Id) {
    return ((Join-Path $RepoRoot "docs\$Language\hardware.md") + "#$Id")
}

function Invoke-VtRequirements {
    # Prints the result in the user's language; returns $true when nothing blocks.
    param(
        [Parameter(Mandatory)][string]$RepoRoot,
        [string]$DataDir = (Join-Path $env:LOCALAPPDATA 'VoiceTutor'),
        [string]$Language = (Get-VtLanguage),
        $Facts = $null
    )
    if ($null -eq $Facts) { $Facts = Get-VtFacts -AppDir $RepoRoot -DataDir $DataDir }
    $messages = Get-VtMessages
    $table = $messages.$Language
    $checks = @(Test-VtRequirements -Facts $Facts)
    $blocking = @($checks | Where-Object { -not $_.Ok -and $_.Blocking })
    $warnings = @($checks | Where-Object { -not $_.Ok -and -not $_.Blocking })

    Write-Host "--- $($table.title)" -ForegroundColor Cyan
    foreach ($c in $checks) {
        $mark = 'ok  '
        if (-not $c.Ok) { $mark = 'FAIL'; if (-not $c.Blocking) { $mark = 'warn' } }
        Write-Host ("  [{0}] {1}: {2}" -f $mark, $c.Id, $c.Value)
    }
    if ($warnings.Count -gt 0 -and $blocking.Count -eq 0) {
        Write-Host $table.warned -ForegroundColor Yellow
    }
    foreach ($c in @($blocking + $warnings)) {
        $color = 'Yellow'
        if ($c.Blocking) { $color = 'Red' }
        Write-Host ('  - ' + (Format-VtMessage -Check $c -Messages $messages -Language $Language)) -ForegroundColor $color
        Write-Host ('    ' + $table.doc.Replace('{doc}', (Get-VtDocLink $RepoRoot $Language $c.Id)))
    }
    if ($blocking.Count -gt 0) {
        Write-Host $table.blocked -ForegroundColor Red
        return $false
    }
    if ($warnings.Count -eq 0) { Write-Host $table.ok -ForegroundColor Green }
    return $true
}
