#!/usr/bin/env python3
"""Smoke test for moodify core engine"""
import sys
sys.path.insert(0, 'src')

# Test data types
from moodify.data_types import WaveState, WaveStateDiagnosis, CraftCardV2
print("1. Data types OK")

# Test knowledge base
from moodify.knowledge.craft_chains import list_all_chains, get_recommended_params
emotions = list_all_chains()
print(f"2. Knowledge base OK - {len(emotions)} emotions: {emotions}")

# Test one craft chain
params = get_recommended_params("GA")
print(f"3. GA craft chain OK - {len(params)} params")

# Test pedalboard
import pedalboard
print(f"4. pedalboard {pedalboard.__version__} OK")

# Test pyloudnorm
import pyloudnorm
print("5. pyloudnorm OK")

# Test diagnosis engine (lightweight import check)
from moodify.diagnosis.engine import DiagnosisEngine
print("6. DiagnosisEngine import OK")

# Test workflow
from moodify.orchestration.workflow_engine import WorkflowOrchestrator
print("7. WorkflowOrchestrator import OK")

print("\n=== ALL CHECKS PASSED ===")
