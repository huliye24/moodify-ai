# MHP-878: CLI/API MAP Contract

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-BUILD-046 / Build Plan-6C / V4
**Depends on**: MHP-846 (Interface Contract), MHP-859 (Command Gate)

## Verified CLI Contract

```bash
python3 -m moodify.cli v01-process <input.wav> --preset <name|auto> --output-dir <dir>
```

- Exit 0 on success ✅ (tested: 3 presets × vocal_folk.wav)
- WAV, JSON, PDF, PNG artifacts in output dir ✅
- MAP v0.2 delivery artifacts (manifest, metadata, etc.) ✅
- Exit non-zero on error ✅ (tested: missing file, unknown preset)

## Verified API Contract

```python
from moodify.v01_pipeline import process_audio
result = process_audio("input.wav", preset="auto")
result.success        # bool
result.delivery        # DeliveryBundle with 10 paths
result.quality_gate    # QualityGate with MRS version
result.scan            # ScanResult with acoustic fields
```

API smoke: 5/5 tests pass (test_api_v01.py).

## Backwards Compatibility

- All existing CLI flags unchanged
- All existing API fields unchanged
- New fields (manifest, metadata, etc.) are optional in DeliveryBundle
- `mrs_version` field indicates which engine was used
