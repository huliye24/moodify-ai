# MHP-887: Operator MAP Runbook
**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / System 6B / E1

## MAP Operator Runbook

### Daily operations
```bash
# Process a track with auto preset
python3 -m moodify.cli v01-process <track.wav> --preset auto --output-dir outputs/

# Process with specific preset
python3 -m moodify.cli v01-process <track.wav> --preset clean_master --output-dir outputs/

# Check quality: review means check warnings
# Pass: no action. Review: inspect validation_report.json. Failed: investigate damage_loss and risk_flags.
```

### Reading the report
- `validation_result.passed`: true = auto-accept, false = operator review
- `validation_result.mrs_version`: check which engine was used
- `validation_result.damage_loss`: 0 = no damage, >0.25 = flagged
- `validation_result.risk_flags`: peak_risk, over_dark, dynamic_damage, mrs_regression, damage_loss_high

### Delivery package
10 files per run. Key files: manifest.json (inventory), metadata.json (reproducibility), validation_report.json (standalone quality), MAP_CHAIN_VERSION (schema version).
