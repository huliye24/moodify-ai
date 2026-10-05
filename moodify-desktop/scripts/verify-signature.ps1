#!/usr/bin/env pwsh
<#
.SYNOPSIS
    验证 Windows 可执行文件的 Authenticode 签名，并可写出机器可读的签名事实。

.DESCRIPTION
    这个脚本存在的理由：我们即将引入代码签名，而「签名了」是一个**可验证的事实**，
    不是一个可以靠 CI 步骤名字断言的状态。

    它做的检查，以及每一项为什么必须做：

      1. 有签名吗？
         没有签名的产物不该被标成已签名——RELEASE_MANIFEST.json 里那句
         `code_signed` 必须是实测出来的，不是手写的。

      2. 签名**有效**吗（Status = Valid）？
         Valid 才是"证书链可信且未被篡改"。UnknownError / NotSigned /
         HashMismatch 都必须在发布前变成失败，而不是一个绿色的 CI。

      3. 签名者是谁？和期望的发布者一致吗？
         这一条最容易被忽略，也最要命：用**别人的**证书签出来的包同样是
         "Valid" 的。Moodify 的发布者身份目前尚未确定（见
         docs/releases/CODE_SIGNING_PLAN.md §2 的 `HUMAN_DECISION_REQUIRED`），
         所以 -ExpectedPublisher 是可选的；省略时脚本只**报告**实际发布者，
         不假装它是对的。

      4. 有时间戳吗？
         没有时间戳的签名会在证书到期后失效——用户手里的安装包会在某一天
         突然变成"签名无效"。这不是可选项。

.PARAMETER Path
    一个或多个待检查文件。

.PARAMETER ExpectedPublisher
    期望的证书主体名（子串匹配，大小写不敏感）。省略时只报告、不判定。

.PARAMETER ManifestOut
    可选：把签名事实写成 JSON（供 RELEASE_MANIFEST.json 合并）。

.PARAMETER AllowUnsigned
    允许未签名通过（用于"签名尚未接线"的过渡期）。默认**不允许**——
    默认必须是严格的，宽松必须是显式的。

.EXAMPLE
    ./verify-signature.ps1 -Path dist-electron/*.exe
    ./verify-signature.ps1 -Path dist-electron/*.exe -ExpectedPublisher "Moodify"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string[]]$Path,

    [string]$ExpectedPublisher,

    [string]$ManifestOut,

    [switch]$AllowUnsigned
)

$ErrorActionPreference = 'Stop'

function Get-SignatureFact {
    param([string]$File)

    $item = Get-Item -LiteralPath $File
    $sig = Get-AuthenticodeSignature -LiteralPath $File

    # 注意：纯哈希表字面量里**不能**给值加类型转换（`k = [string]$x` 不是合法语法），
    # 那会让解析器在结尾的 `}` 上报 "Unexpected token" —— 报错位置与真因相隔很远。
    # 所以先算好标量，再一次性建表。
    $status = [string]$sig.Status
    # 「有没有签名」的判据是**签名者证书是否存在**，不是 Status 字符串。
    # 实测：一个非 PE 文件（纯文本）的 Status 是 'UnknownError' 而不是 'NotSigned'，
    # 用 `-ne 'NotSigned'` 判断会把它算成「已签名」并因此跳过未签名分支。
    # SignerCertificate 才是可靠信号。
    $isSigned = ($null -ne $sig.SignerCertificate)
    $isValid = ($status -eq 'Valid')
    $subject = $null
    $thumbprint = $null
    $issuer = $null
    $stamper = $null
    $timestamped = $false

    if ($isSigned) {
        $subject = $sig.SignerCertificate.Subject
        $thumbprint = $sig.SignerCertificate.Thumbprint
        $issuer = $sig.SignerCertificate.Issuer
    }

    # Get-AuthenticodeSignature 不直接暴露时间戳细节；
    # TimeStamperCertificate 在已打时间戳时非空。
    if ($sig.TimeStamperCertificate) {
        $timestamped = $true
        $stamper = $sig.TimeStamperCertificate.Subject
    }

    $fact = [ordered]@{
        name              = $item.Name
        bytes             = $item.Length
        sha256            = (Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash.ToLowerInvariant()
        signature_status  = $status
        is_signed         = $isSigned
        is_valid          = $isValid
        signer_subject    = $subject
        signer_thumbprint = $thumbprint
        signer_issuer     = $issuer
        time_stamper      = $stamper
        timestamped       = $timestamped
    }

    if ($sig.StatusMessage) { $fact.status_message = $sig.StatusMessage }
    return $fact
}

function Write-Fact {
    param($Fact, [string]$Label)
    Write-Host ""
    Write-Host "── $Label" -ForegroundColor Cyan
    Write-Host "   file         : $($Fact.name)  ($([math]::Round($Fact.bytes / 1MB, 2)) MB)"
    Write-Host "   sha256       : $($Fact.sha256)"
    Write-Host "   status       : $($Fact.signature_status)"
    if ($Fact.is_signed) {
        Write-Host "   signer       : $($Fact.signer_subject)"
        Write-Host "   issuer       : $($Fact.signer_issuer)"
        Write-Host "   thumbprint   : $($Fact.signer_thumbprint)"
        if ($Fact.timestamped) {
            Write-Host "   timestamped  : yes ($($Fact.time_stamper))"
        } else {
            Write-Host "   timestamped  : NO" -ForegroundColor Yellow
        }
    }
}

$facts = @()
$failures = @()

foreach ($p in $Path) {
    # 允许通配符：CI 里的文件名含版本号，写死会脆弱
    $resolved = @(Get-ChildItem -Path $p -ErrorAction SilentlyContinue)
    if ($resolved.Count -eq 0) {
        $failures += "no file matched: $p"
        continue
    }
    foreach ($file in $resolved) {
        $fact = Get-SignatureFact -File $file.FullName
        Write-Fact -Fact $fact -Label 'signature'
        $facts += $fact

        if (-not $fact.is_signed) {
            if (-not $AllowUnsigned) {
                $failures += "$($fact.name): NOT SIGNED"
            } else {
                Write-Host "   note         : unsigned accepted (-AllowUnsigned)" -ForegroundColor Yellow
            }
            continue
        }

        if (-not $fact.is_valid) {
            $failures += "$($fact.name): signature status is '$($fact.signature_status)' (not Valid)"
        }

        if (-not $fact.timestamped) {
            # 时间戳不是"好看"，是"证书过期后签名仍然有效"的唯一保障
            $failures += "$($fact.name): signed WITHOUT a timestamp"
        }

        if ($ExpectedPublisher) {
            if ($fact.signer_subject -and
                $fact.signer_subject.ToLowerInvariant().Contains($ExpectedPublisher.ToLowerInvariant())) {
                Write-Host "   publisher    : matches '$ExpectedPublisher'" -ForegroundColor Green
            } else {
                $failures += "$($fact.name): signer '$($fact.signer_subject)' does not contain '$ExpectedPublisher'"
            }
        } elseif ($fact.is_signed) {
            Write-Host "   publisher    : NOT CHECKED (-ExpectedPublisher omitted)" -ForegroundColor Yellow
            Write-Host "                  A valid signature from ANY certificate passes this check."
        }
    }
}

$summary = [ordered]@{
    schema        = 'moodify.release.signature-facts/0.1'
    generated_at  = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    expected_publisher = if ($ExpectedPublisher) { $ExpectedPublisher } else { $null }
    publisher_checked  = [bool]$ExpectedPublisher
    allow_unsigned     = [bool]$AllowUnsigned
    artifacts     = $facts
    all_signed    = (($facts | Where-Object { -not $_.is_signed }).Count -eq 0)
    all_valid     = (($facts | Where-Object { -not $_.is_valid }).Count -eq 0)
    all_timestamped = (($facts | Where-Object { -not $_.timestamped }).Count -eq 0)
    failures      = $failures
}

if ($ManifestOut) {
    $dir = Split-Path -Parent $ManifestOut
    if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    $summary | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ManifestOut -Encoding utf8
    Write-Host ""
    Write-Host "signature facts -> $ManifestOut"
}

Write-Host ""
Write-Host ("summary: signed={0} valid={1} timestamped={2} publisher_checked={3}" -f `
    $summary.all_signed, $summary.all_valid, $summary.all_timestamped, $summary.publisher_checked)

if ($failures.Count -gt 0) {
    Write-Host ""
    Write-Host "FAILED:" -ForegroundColor Red
    foreach ($f in $failures) { Write-Host "  - $f" -ForegroundColor Red }
    exit 1
}

Write-Host "signature verification passed." -ForegroundColor Green
exit 0
