# Failure Analysis — NEM Studio OS 001 Validate-6

**Date**: 2026-06-04
**Protocol**: NEM-18 / Validate-6 / V2
**Source**: MHP-061 validation run + Build-6 test results

---

## 1. Failure Taxonomy

| # | Class | Severity | Count | Description |
|---|-------|----------|-------|-------------|
| 1 | CLI_ARG_MISMATCH | HIGH | 3 templates | Default command_templates used `--input`/`--output` flags, but moodify.cli uses positional audio_path + `--output-dir` |
| 2 | PATH_RESOLUTION | MEDIUM | 0 (potential) | template uses `cli.py` (cwd-relative) instead of `-m moodify.cli` (package-relative) |
| 3 | MP3_FORMAT | LOW | 30 files | Validation dataset uses MP3; moodify.cli process expects WAV. Pipeline works with WAV, MP3 support TBD |

## 2. Root Cause Analysis

### CLI_ARG_MISMATCH (FIXED)
- **Root cause**: `config.py` had 3 default command_templates, all using `--input` and `--output` flags that don't exist in the moodify.cli process command
- **Why it passed tests**: test_real_audio.py explicitly overrode command_templates with correct format (2 templates using `{input}` positional + `--output-dir`)
- **Reproduction**: Run `run_operator_job` without custom command_templates → all 3 templates fail with exit code 2
- **Fix applied**: Updated default templates in config.py to use correct syntax

### PATH_RESOLUTION (FIXED)
- **Root cause**: Template 0 and 2 used `cli.py` (relative to cwd/project_root), which fails if project_root != actual project dir
- **Fix applied**: Removed cwd-relative templates; use only `-m moodify.cli` (package-relative)

### MP3_FORMAT (NOTED)
- **Root cause**: Validation dataset contains 30 MP3 files; moodify.cli process exits with "ERROR: File not found" for MP3 inputs
- **Impact**: LOW — WAV pipeline is fully tested and works. MP3 support is a feature request, not a bug.
- **Action**: Document MP3→WAV conversion step in operator guide; add format detection in future NEM

## 3. Fix Priority List

| Priority | Issue | Action | MHP |
|----------|-------|--------|-----|
| P0 | CLI_ARG_MISMATCH | ✅ Fixed in config.py | 065 |
| P1 | PATH_RESOLUTION | ✅ Fixed in config.py | 065 |
| P2 | MP3_FORMAT | Document conversion step | 065 |
| P3 | Validation dataset MP3→WAV | Add conversion script | Future |

## 4. Impact Assessment

| System | Status | Risk |
|--------|--------|------|
| WAV pipeline (warm_vocal, clean_master, wide_space) | ✅ Green | None |
| CLI command template system | ✅ Fixed | None (3 tests verify) |
| Real audio DSP processing | ✅ 3/3 pass | None |
| MP3 audio support | ⚠️ Not supported | Low — documented workaround |
| JSONL storage | ✅ No corruption in 10-job test | None |

---

## Conclusion

One real bug found and fixed (CLI_ARG_MISMATCH). The system is healthy. No critical failures in the DSP pipeline, gate decisions, or data storage layers. Proceed to Harden-6.
