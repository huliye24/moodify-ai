<#
.SYNOPSIS
    发布守卫：在产生 GitHub Release 之前，拒绝任何无法证明的产物集合。

.DESCRIPTION
    这是供应链上**唯一不可撤回**的动作（发布）前面最后一道闸门，因此它必须能被测试。
    早先这段逻辑内联在 workflow 的 YAML 里，结果是「无法验证」——
    一条只在真实发布时才第一次执行的检查，等于没有检查。

    它断言四件事：

      1. 真的有可执行产物（.exe / .msix / .msi）
      2. SHA256SUMS.txt 存在，条目数与产物数**一致**，且**逐个重算指纹比对**
         为什么必须重算：校验和可能是上一版算的。一份与文件不匹配的校验和
         比没有校验和更糟——用户会以为下载被篡改，或者更坏，以为没问题。
      3. RELEASE_MANIFEST.json 存在且可解析
      4. 当 -SigningEnabled 时：清单必须报告 code_signed=true、签名有效、有时间戳
         这一条在构建阶段已由 verify-signature.ps1 强制；这里再断言一次，
         因为「发布」是本链上唯一不能撤销的动作。

    -SigningEnabled 为假时，它**不**要求签名，但会明确 warn：
    产物没有 Authenticode 签名。如实报告 ≠ 假装通过。

.PARAMETER ReleaseDir
    即将发布的目录。

.PARAMETER SigningEnabled
    SignPath 是否已启用（对应 vars.SIGNPATH_ENABLED == 'true'）。

.EXAMPLE
    ./release-guard.ps1 -ReleaseDir release -SigningEnabled:$false
    ./release-guard.ps1 -ReleaseDir release -SigningEnabled:$true
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ReleaseDir,

    [switch]$SigningEnabled
)

$ErrorActionPreference = 'Stop'
$execExt = @('.exe', '.msix', '.msi')

function Fail([string]$Message) {
    Write-Host ""
    Write-Host "RELEASE GUARD FAILED: $Message" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path -LiteralPath $ReleaseDir)) {
    Fail "release directory not found: $ReleaseDir"
}

$exes = @(Get-ChildItem -LiteralPath $ReleaseDir -File |
    Where-Object { $execExt -contains $_.Extension.ToLowerInvariant() })
if ($exes.Count -eq 0) {
    Fail "no executable artifacts in $ReleaseDir; nothing legitimate to publish"
}

Write-Host "artifacts to publish:"
$exes | Select-Object Name, Length | Format-Table -AutoSize

# ── 2. SHA256SUMS.txt ──────────────────────────────────────────────────────────
$sumsPath = Join-Path $ReleaseDir 'SHA256SUMS.txt'
if (-not (Test-Path -LiteralPath $sumsPath)) {
    Fail "SHA256SUMS.txt is missing. Every published binary must carry a checksum."
}
$lines = @(Get-Content -LiteralPath $sumsPath | Where-Object { $_.Trim() })
if ($lines.Count -ne $exes.Count) {
    Fail ("SHA256SUMS.txt lists $($lines.Count) entr(ies) but $($exes.Count) executable(s) " +
          "are present. The checksum file must cover exactly the published binaries.")
}
foreach ($line in $lines) {
    $parts = $line -split '\s+', 2
    if ($parts.Count -ne 2) { Fail "malformed checksum line: '$line'" }
    $want = $parts[0].Trim().ToLowerInvariant()
    $name = $parts[1].Trim()
    $file = Join-Path $ReleaseDir $name
    if (-not (Test-Path -LiteralPath $file)) {
        Fail "SHA256SUMS.txt references a file that is not present: $name"
    }
    $got = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($got -ne $want) {
        Fail "sha256 mismatch for $name`n  listed: $want`n  actual: $got"
    }
    Write-Host "sha256 ok  $name"
}

# ── 3 + 4. manifest ────────────────────────────────────────────────────────────
$manifestPath = Join-Path $ReleaseDir 'RELEASE_MANIFEST.json'
if (-not (Test-Path -LiteralPath $manifestPath)) {
    Fail "RELEASE_MANIFEST.json is missing; the release provenance record must ship with it."
}
$manifest = $null
try { $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json }
catch { Fail "RELEASE_MANIFEST.json is not valid JSON: $($_.Exception.Message)" }

if ($SigningEnabled) {
    if (-not $manifest.code_signed) {
        Fail ("Signing is enabled but the manifest reports code_signed=false. " +
              "Refusing to publish an unsigned build as the official release.")
    }
    if (-not $manifest.signature_valid) { Fail "manifest reports signature_valid=false" }
    if (-not $manifest.signature_timestamped) {
        Fail "manifest reports an unsigned timestamp; the signature would expire with the certificate"
    }
    Write-Host "signed release confirmed: $($manifest.signer_subject)"
} else {
    Write-Host ("::warning title=Unsigned release::code_signed=$($manifest.code_signed) " +
                "because SignPath is not configured. Artifacts carry GitHub attestations " +
                "but no Authenticode signature. See docs/releases/WINDOWS_CODE_SIGNING.md")
}

Write-Host ""
Write-Host "release guard passed: $($exes.Count) artifact(s)" -ForegroundColor Green
exit 0
