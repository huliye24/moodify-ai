# Preset Runbook — MHP-189

## Available Presets (v0.2.0)

| Preset | Category | Status | Best For |
|--------|----------|--------|----------|
| warm_vocal | warm_reality | candidate | piano, vocal |
| clean_master | dynamic_recovery | candidate | electronic |
| wide_space | soft_space | experimental | rock, ambient |
| safe_air | anti_fatigue | experimental | over-dark mitigation |
| clean_master_safe | anti_fatigue | experimental | — |
| air_preserve_master | soft_space | experimental | — |
| bypass_control | bypass | stable | reference |

## Adopting a Preset

1. Run: `craft-safety-check --preset <name> --over-dark none ...`
2. All 5 gates must pass
3. Batch validate on 10+ samples
4. Set status: `candidate`
5. After 30+ successful deliveries without safety gate failures: `stable`
6. After 100+ deliveries: `adopted`
