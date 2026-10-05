<!--
  这个文件是 GitHub Release 正文的来源（.github/workflows/desktop-release.yml 的
  `body_path`）。它只放**可验证的工程事实**，不放营销文案。

  为什么版本号与文件名不写死在这里：正文会随 tag 发布，写死就会与产物不一致。
  产物清单与指纹由 Release 附件里的 RELEASE_MANIFEST.json / SHA256SUMS.txt 承载——
  那才是权威，正文只是指路。
-->

## Verification

```text
Source:
https://github.com/huliye24/moodify-ai

License:
GNU GPL v3

Build:
GitHub Actions

Windows code signing:
SignPath Foundation

Integrity:
SHA256SUMS.txt

Provenance:
GitHub Artifact Attestation
```

### Verify the download before running it

```bash
# 1. Integrity — the checksum must match the file you downloaded
sha256sum -c SHA256SUMS.txt

# 2. Provenance — this binary was built by this repository's CI, from a specific commit
gh attestation verify Moodify_Studio_*_Setup_x64.exe --repo huliye24/moodify-ai

# 3. Publisher — Windows Authenticode signature
#    PowerShell:
Get-AuthenticodeSignature .\Moodify_Studio_*_Setup_x64.exe | Format-List Status, SignerCertificate, TimeStamperCertificate
```

### Honest boundaries

- **Windows code signing is performed by [SignPath Foundation](https://signpath.org/), not by
  Moodify.** The publisher shown in the Windows properties dialog is `SignPath Foundation`.
  This is the accepted trade-off while the project is zero-cost. See
  [WINDOWS_CODE_SIGNING.md](https://github.com/huliye24/moodify-ai/blob/main/docs/releases/WINDOWS_CODE_SIGNING.md).
- **Signing and provenance are different guarantees.** Signing says who published the bytes;
  attestation says which commit and workflow produced them. Neither one says the software is
  free of defects, and neither is a claim that the app is "safe" or "certified".
- **A valid signature does not by itself remove the SmartScreen warning.** Reputation
  accumulates over downloads; a newly signed binary may still prompt for a while.
- Before signing is enabled, `RELEASE_MANIFEST.json` reports `code_signed: false`. That value is
  **measured** from the artifact, not hardcoded. Do not read an unsigned release as a signed one.

### What is in the artifact set

| File | What it is |
|---|---|
| `Moodify_Studio_<version>_Setup_x64.exe` | NSIS installer |
| `Moodify_Studio_<version>_Portable_x64.exe` | portable executable |
| `SHA256SUMS.txt` | SHA-256 of the executable(s) above, computed **after** signing |
| `RELEASE_MANIFEST.json` | version, commit, measured signature facts, artifact digests |
| `SIGNATURE_FACTS.json` | raw output of the signature verification step |
