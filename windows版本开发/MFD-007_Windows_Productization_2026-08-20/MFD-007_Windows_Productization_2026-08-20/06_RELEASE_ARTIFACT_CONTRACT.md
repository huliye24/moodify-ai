# MFD-007 Release Artifact Contract

Recommended output structure:

```text
release/
└── 0.1.0-alpha.N/
    ├── installer/
    │   └── Moodify-Desktop-<version>-win-x64-setup.exe
    ├── SHA256SUMS.txt
    ├── RELEASE_NOTES.md
    ├── BUILD_INFO.json
    └── TEST_EVIDENCE.md
```

Actual Squirrel artifacts may include additional files.

Do not delete maker-required update metadata.

---

## BUILD_INFO.json

Suggested:

```json
{
  "product": "Moodify Desktop",
  "version": "0.1.0-alpha.1",
  "commit": "<sha>",
  "platform": "win32",
  "arch": "x64",
  "electron": "<version>",
  "forge": "<version>",
  "channel": "internal-alpha",
  "signed": false,
  "build_date": "<ISO-8601>"
}
```

---

## SHA256

Generate for externally transferred binary artifacts.

Checksums prove artifact integrity.

They do not prove publisher identity.

---

## RELEASE_NOTES

Must include:

- version
- scope
- verified capabilities
- known limitations
- signing status
- update status
- rollback version if relevant

Do not claim unverified audio quality properties.
