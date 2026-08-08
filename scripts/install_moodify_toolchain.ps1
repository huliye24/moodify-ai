# Moodify Open-Source Audio Toolchain Installer
# Run: powershell -ExecutionPolicy Bypass -File scripts/install_moodify_toolchain.ps1

$ErrorActionPreference = "Stop"

function Refresh-ProcessPath {
    $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machine;$user"
}

function Find-Sox {
    $command = Get-Command sox -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    $root = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages"
    $candidate = Get-ChildItem -LiteralPath $root -Recurse -Filter sox.exe -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match "ChrisBagwell\.SoX" } |
        Select-Object -First 1
    if ($candidate) { return $candidate.FullName }
    return $null
}

function Find-RubberBand {
    $command = Get-Command rubberband -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    $root = "E:\moodify\tools\third_party\rubberband-4.0.0"
    $candidate = Get-ChildItem -LiteralPath $root -Recurse -Filter rubberband.exe -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($candidate) { return $candidate.FullName }
    return $null
}

function Add-UserPath([string]$Directory) {
    $current = [Environment]::GetEnvironmentVariable("Path", "User")
    $parts = @($current -split ";" | Where-Object { $_ })
    if ($parts -notcontains $Directory) {
        [Environment]::SetEnvironmentVariable("Path", (($parts + $Directory) -join ";"), "User")
    }
}

Write-Host "=== Moodify Toolchain Installer ===" -ForegroundColor Cyan
Refresh-ProcessPath

Write-Host "`n[1/4] SoX" -ForegroundColor Yellow
$sox = Find-Sox
if (-not $sox) {
    winget install --id ChrisBagwell.SoX --exact --accept-source-agreements --accept-package-agreements
    if ($LASTEXITCODE -ne 0) { throw "SOX_INSTALL_FAILED" }
    Refresh-ProcessPath
    $sox = Find-Sox
}
if (-not $sox) { throw "SOX_NOT_FOUND_AFTER_INSTALL" }
Add-UserPath (Split-Path -Parent $sox)
Write-Host "  [OK] $(& $sox --version 2>&1)"

Write-Host "`n[2/4] Matchering" -ForegroundColor Yellow
py -3.11 -c "import importlib.metadata as m; print(m.version('matchering'))" *> $null
if ($LASTEXITCODE -ne 0) {
    py -3.11 -m pip install matchering
    if ($LASTEXITCODE -ne 0) { throw "MATCHERING_INSTALL_FAILED" }
}
$matcheringVersion = py -3.11 -c "import importlib.metadata as m; print(m.version('matchering'))"
Write-Host "  [OK] $matcheringVersion"

Write-Host "`n[3/4] Rubber Band" -ForegroundColor Yellow
$rubberband = Find-RubberBand
if (-not $rubberband) {
    throw "RUBBERBAND_NOT_FOUND: install the official Windows CLI from https://breakfastquay.com/rubberband/"
}
Add-UserPath (Split-Path -Parent $rubberband)
py -3.11 -c "import pyrubberband" *> $null
if ($LASTEXITCODE -ne 0) {
    py -3.11 -m pip install pyrubberband
    if ($LASTEXITCODE -ne 0) { throw "PYRUBBERBAND_INSTALL_FAILED" }
}
$rubberbandVersion = py -3.11 -c "import subprocess,sys; p=subprocess.run([sys.argv[1],'--version'],capture_output=True,text=True); print((p.stdout or p.stderr).strip()); raise SystemExit(p.returncode)" $rubberband
if ($LASTEXITCODE -ne 0) { throw "RUBBERBAND_PROBE_FAILED" }
Write-Host "  [OK] $rubberbandVersion"

Write-Host "`n[4/4] lameenc" -ForegroundColor Yellow
py -3.11 -c "import lameenc" *> $null
if ($LASTEXITCODE -ne 0) {
    py -3.11 -m pip install lameenc
    if ($LASTEXITCODE -ne 0) { throw "LAMEENC_INSTALL_FAILED" }
}
$lameVersion = py -3.11 -c "import importlib.metadata as m; print(m.version('lameenc'))"
Write-Host "  [OK] $lameVersion"

Refresh-ProcessPath
Write-Host "`n=== Verification PASS ===" -ForegroundColor Green
Write-Host "SoX=$sox"
Write-Host "Matchering=$matcheringVersion"
Write-Host "RubberBand=$rubberbandVersion ($rubberband)"
Write-Host "lameenc=$lameVersion"
