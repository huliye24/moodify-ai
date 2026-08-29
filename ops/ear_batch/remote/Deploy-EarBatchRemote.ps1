param(
    [Parameter(Mandatory = $true)][string]$HostAlias,
    [string]$RemoteRoot = "~/moodify-ear-remote",
    [switch]$ReplaceRun
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$sourceRoot = "E:\Moodify ear"
$runRoot = Join-Path $repoRoot "artifacts\ear_batch\v1"
if (-not (Test-Path -LiteralPath $sourceRoot -PathType Container)) { throw "Source not found: $sourceRoot" }
if (-not (Test-Path -LiteralPath $runRoot -PathType Container)) { throw "Run not found: $runRoot" }

    ssh -o BatchMode=yes -o ConnectTimeout=30 -o ConnectionAttempts=3 $HostAlias "printf REMOTE_OK"
if ($LASTEXITCODE -ne 0) { throw "SSH preflight failed for $HostAlias" }

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("moodify-ear-deploy-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempRoot | Out-Null
try {
    $baseArchive = Join-Path $tempRoot "repo-snapshot.tar.gz"
    $sourceArchive = Join-Path $tempRoot "source-v1.tar.gz"

    $localCommit = (git -C $repoRoot rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) { throw "Cannot resolve local HEAD" }
    tar -czf $baseArchive --exclude=moodify-core-package/tests/baseline/test_audio -C $repoRoot AGENTS.md README.md `
      docs/REPOSITORY_STATUS.md docs/LEGACY_AND_EXPERIMENTAL_POLICY.md docs/failures docs/treatment_records docs/releases `
      moodify-core-package/src moodify-core-package/tests moodify-core-package/benchmarks moodify-core-package/scripts `
      moodify-core-package/configs moodify-core-package/sensitivity moodify-core-package/pyproject.toml `
      moodify-core-package/requirements.txt moodify-core-package/requirements.lock.txt moodify-core-package/README.md `
      ops/ear_batch tests/ear_batch artifacts/ear_batch/v1 schemas configs scripts
    if ($LASTEXITCODE -ne 0) { throw "repository snapshot failed" }
    tar -czf $sourceArchive -C "E:\" --exclude="Moodify ear/moodify ear 2.0" "Moodify ear"
    if ($LASTEXITCODE -ne 0) { throw "source archive failed" }

    $replace = if ($ReplaceRun) { "1" } else { "0" }
    $prepareScript = @"
set -euo pipefail
root=$RemoteRoot
replace=$replace
if [[ -e "`$root/repo/artifacts/ear_batch/v1/TASK_LEDGER.json" && "`$replace" != 1 ]]; then
  echo 'remote run exists; use -ReplaceRun' >&2
  exit 12
fi
mkdir -p "`$root/incoming" "`$root/backups"
if [[ "`$replace" == 1 && -d "`$root/repo" ]]; then
  stamp=`$(date -u +%Y%m%dT%H%M%SZ)
  mv "`$root/repo" "`$root/backups/repo-`$stamp"
  if [[ -d "`$root/source" ]]; then mv "`$root/source" "`$root/backups/source-`$stamp"; fi
fi
mkdir -p "`$root/source"
"@
    $prepareEncoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($prepareScript))
    ssh $HostAlias "echo $prepareEncoded | base64 -d | bash"
    if ($LASTEXITCODE -ne 0) { throw "remote directory preparation failed" }
    scp $baseArchive $sourceArchive "${HostAlias}:$RemoteRoot/incoming/"
    if ($LASTEXITCODE -ne 0) { throw "archive upload failed" }
    $installScript = @"
set -euo pipefail
root=$RemoteRoot
mkdir -p "`$root/repo"
tar -xzf "`$root/incoming/repo-snapshot.tar.gz" -C "`$root/repo"
tar -xzf "`$root/incoming/source-v1.tar.gz" -C "`$root/source"
cd "`$root/repo"
git init -q
git config user.name 'Moodify Remote Worker'
git config user.email 'remote-worker@localhost'
python3 ops/ear_batch/ear_batch.py rebase-source --run-dir artifacts/ear_batch/v1 --new-source "`$root/source/Moodify ear"
git add -A
git commit -q -m 'Remote execution baseline $localCommit'
bash ops/ear_batch/remote/remote_preflight.sh "`$root"
"@
    $installEncoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($installScript))
    ssh $HostAlias "echo $installEncoded | base64 -d | bash"
    if ($LASTEXITCODE -ne 0) { throw "remote extraction or preflight failed" }
    Write-Output "DEPLOYED host=$HostAlias root=$RemoteRoot"
}
finally {
    if (Test-Path -LiteralPath $tempRoot) {
        $resolved = (Resolve-Path -LiteralPath $tempRoot).Path
        $tempBase = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
        if (-not $resolved.StartsWith($tempBase, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to remove non-temporary path: $resolved"
        }
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
}
