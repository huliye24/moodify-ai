# Moodify Desktop 0.1 Alpha — Release Artifact Template

Recommended:

```text
release/
└── <version>/
    ├── installer/
    │   └── <installer>
    ├── SHA256SUMS.txt
    ├── BUILD_INFO.json
    ├── RELEASE_NOTES.md
    ├── TEST_EVIDENCE.md
    ├── KNOWN_ISSUES.md
    ├── SECURITY_NOTES.md
    └── ROLLBACK.md
```

---

## RELEASE_NOTES skeleton

```markdown
# Moodify Desktop <version>

## Verified
- Windows install
- Moodify Player
- Cloud playback
- Play / Pause / Seek
- Next / Previous
- state recovery

## Known limitations
- ...

## Not included
- WASAPI Exclusive
- offline library
- EQ / DSP UI
- skins/community
- macOS/Linux
```

---

## KNOWN_ISSUES

Every issue:

```text
ID
Severity
Description
Reproduction
Impact
Workaround
Target package/version
```

---

## SECURITY_NOTES

Record:

```text
signed/unsigned
auth model
secure storage
update status
known security limitations
```

Do not publish secrets.
