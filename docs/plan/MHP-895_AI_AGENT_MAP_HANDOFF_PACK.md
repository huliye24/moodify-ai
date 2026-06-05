# MHP-895: AI Agent MAP Handoff Pack
**Status**: done

## Handoff Pack Contents
1. E-Chain doc: docs/echain/ECHAIN-MOODIFY-MAP-CHAIN-015.md
2. Interface contract: docs/spec/map_chain_interface_contract.md
3. JSON schema: schemas/map_chain_report.schema.json
4. AWJ policy: docs/policy/map_chain_awj_scope.md
5. Judge checker: scripts/map_judge_check.py
6. Worker protocol: docs/protocol/AEP_WORKER_PROTOCOL.md
7. All 18 Probe + 18 Build + 18 System plan files
8. 19+ probe reports + build reports
9. MAP_CHAIN_VERSION: map_chain_v0.2.0

## Agent Entry Point
```bash
# Clone, install, and smoke test
pip install -e moodify-core-package/
python3 -m pytest -q moodify-core-package/tests/
python3 -m moodify.cli v01-process <audio.wav> --preset auto --output-dir outputs/
python3 scripts/map_judge_check.py schema outputs/*_report.json
```
