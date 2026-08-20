param(
    [Parameter(Mandatory = $true)][string]$HostAlias,
    [string]$RemoteRoot = "~/moodify-ear-remote",
    [string]$Destination = "artifacts\ear_batch\remote-results"
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$destinationPath = [System.IO.Path]::GetFullPath((Join-Path $repoRoot $Destination))
New-Item -ItemType Directory -Force -Path $destinationPath | Out-Null
$stamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssZ")
$archiveName = "ear-batch-results-$stamp.tar.gz"
$localArchive = Join-Path $destinationPath $archiveName

ssh -o BatchMode=yes -o ConnectTimeout=30 -o ConnectionAttempts=3 $HostAlias "set -eu; root=$RemoteRoot; cd \"`$root/repo\"; python3 ops/ear_batch/ear_batch.py validate --run-dir artifacts/ear_batch/v1; python3 ops/ear_batch/ear_batch.py report --run-dir artifacts/ear_batch/v1; tar -czf \"`$root/$archiveName\" artifacts/ear_batch/v1; sha256sum \"`$root/$archiveName\" > \"`$root/$archiveName.sha256\""
if ($LASTEXITCODE -ne 0) { throw "Remote validation or archive failed" }
scp "${HostAlias}:$RemoteRoot/$archiveName" $localArchive
scp "${HostAlias}:$RemoteRoot/$archiveName.sha256" "$localArchive.sha256"
if ($LASTEXITCODE -ne 0) { throw "Result download failed" }

$expected = (Get-Content -LiteralPath "$localArchive.sha256" -Raw).Split(' ', [System.StringSplitOptions]::RemoveEmptyEntries)[0].ToLowerInvariant()
$actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $localArchive).Hash.ToLowerInvariant()
if ($expected -ne $actual) { throw "SHA-256 mismatch: expected=$expected actual=$actual" }
$extractPath = Join-Path $destinationPath $stamp
New-Item -ItemType Directory -Path $extractPath | Out-Null
tar -xzf $localArchive -C $extractPath
if ($LASTEXITCODE -ne 0) { throw "Result extraction failed" }
Write-Output "COLLECTED host=$HostAlias sha256=$actual path=$extractPath"
