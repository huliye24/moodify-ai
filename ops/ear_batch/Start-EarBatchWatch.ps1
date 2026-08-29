param(
    [string]$RunDirectory = "artifacts\ear_batch\v1",
    [int]$PollSeconds = 60
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$runPath = [System.IO.Path]::GetFullPath((Join-Path $repoRoot $RunDirectory))
$controller = Join-Path $PSScriptRoot "ear_batch.py"
$heartbeat = Join-Path $runPath "HEARTBEAT.json"

Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class MoodifyPowerState {
    [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    public static extern uint SetThreadExecutionState(uint flags);
}
"@

$continuous = 0x80000000
$systemRequired = 0x00000001
[void][MoodifyPowerState]::SetThreadExecutionState($continuous -bor $systemRequired)

try {
    Set-Location $repoRoot
    python $controller validate --run-dir $runPath
    if ($LASTEXITCODE -ne 0) { throw "Ear batch preflight failed." }

    while ($true) {
        $ledgerPath = Join-Path $runPath "TASK_LEDGER.json"
        $ledger = Get-Content -Raw -LiteralPath $ledgerPath | ConvertFrom-Json
        $active = @($ledger.tasks | Where-Object { $_.state -in @("READY", "RUNNING", "VERIFYING", "FAILED_RETRYABLE") })
        $pending = @($ledger.tasks | Where-Object { $_.state -eq "PENDING" })
        $heartbeatValue = [ordered]@{
            checked_at = [DateTime]::UtcNow.ToString("o")
            watcher_pid = $PID
            active_count = $active.Count
            pending_count = $pending.Count
            ledger_updated_at = $ledger.updated_at
        } | ConvertTo-Json
        [System.IO.File]::WriteAllText($heartbeat, $heartbeatValue + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))

        if ($active.Count -eq 0 -and $pending.Count -eq 0) {
            python $controller report --run-dir $runPath
            break
        }
        Start-Sleep -Seconds $PollSeconds
    }
}
finally {
    [void][MoodifyPowerState]::SetThreadExecutionState($continuous)
}
