param(
  [string]$OutputRoot = (Join-Path $PSScriptRoot '..\build\runtime')
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$desktopRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$runtimeRoot = [System.IO.Path]::GetFullPath($OutputRoot)
$pythonRoot = Join-Path $runtimeRoot 'python'
$sitePackages = Join-Path $pythonRoot 'Lib\site-packages'
$cacheRoot = Join-Path $desktopRoot 'build\downloads'

New-Item -ItemType Directory -Force -Path $cacheRoot | Out-Null
if (Test-Path -LiteralPath $runtimeRoot) {
  Remove-Item -LiteralPath $runtimeRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $pythonRoot,$sitePackages | Out-Null

$pythonZip = Join-Path $cacheRoot 'python-3.11.9-embed-amd64.zip'
if (-not (Test-Path -LiteralPath $pythonZip)) {
  Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile $pythonZip
}
Expand-Archive -LiteralPath $pythonZip -DestinationPath $pythonRoot -Force

$sourceSitePackages = Join-Path $repoRoot '.venv-core\Lib\site-packages'
if (-not (Test-Path -LiteralPath $sourceSitePackages)) {
  throw "Missing prepared Core environment: $sourceSitePackages"
}
Copy-Item -Path (Join-Path $sourceSitePackages '*') -Destination $sitePackages -Recurse -Force
Get-ChildItem -LiteralPath $sitePackages -Filter '*.pth' -File -ErrorAction SilentlyContinue | Remove-Item -Force

$corePackage = Join-Path $repoRoot 'moodify-core-package\src\moodify'
Copy-Item -LiteralPath $corePackage -Destination $sitePackages -Recurse -Force

$pth = Join-Path $pythonRoot 'python311._pth'
@('python311.zip', '.', 'Lib/site-packages', 'import site') | Set-Content -LiteralPath $pth -Encoding ascii

$ffmpegZip = Join-Path $cacheRoot 'ffmpeg-release-essentials.zip'
if (-not (Test-Path -LiteralPath $ffmpegZip)) {
  Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile $ffmpegZip
}
$ffmpegExtract = Join-Path $cacheRoot 'ffmpeg-extracted'
if (Test-Path -LiteralPath $ffmpegExtract) {
  Remove-Item -LiteralPath $ffmpegExtract -Recurse -Force
}
Expand-Archive -LiteralPath $ffmpegZip -DestinationPath $ffmpegExtract -Force
$ffmpegBin = Get-ChildItem -LiteralPath $ffmpegExtract -Directory | Select-Object -First 1 | ForEach-Object { Join-Path $_.FullName 'bin' }
if (-not $ffmpegBin -or -not (Test-Path -LiteralPath (Join-Path $ffmpegBin 'ffmpeg.exe'))) {
  throw 'Downloaded FFmpeg archive did not contain ffmpeg.exe'
}
New-Item -ItemType Directory -Force -Path (Join-Path $runtimeRoot 'ffmpeg') | Out-Null
Copy-Item -LiteralPath (Join-Path $ffmpegBin 'ffmpeg.exe') -Destination (Join-Path $runtimeRoot 'ffmpeg\ffmpeg.exe')
Copy-Item -LiteralPath (Join-Path $ffmpegBin 'ffprobe.exe') -Destination (Join-Path $runtimeRoot 'ffmpeg\ffprobe.exe')

Get-ChildItem -LiteralPath $runtimeRoot -Directory -Recurse -Filter '__pycache__' -ErrorAction SilentlyContinue |
  Remove-Item -Recurse -Force

$smokeCode = "import moodify, numpy, scipy, librosa, soundfile, pedalboard; print('Moodify bundled runtime OK')"
& (Join-Path $pythonRoot 'python.exe') -c $smokeCode
if ($LASTEXITCODE -ne 0) { throw 'Bundled Python/Core smoke test failed' }

Write-Host "Prepared runtime at $runtimeRoot"
