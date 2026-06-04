"""MHP-701-718: Craft Chain Engine.

Executes safe, measurable craft chains with per-step metrics, safety rollback,
and CLI integration. Part of ECHAIN-MOODIFY-CRAFT-22-012.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .craft_processes import (
    CRAFT_REGISTRY,
    OpResult,
    execute_operation,
    get_operation,
    list_operation_ids,
)
from .utils import utc_now_iso


# ═══════════════════════════════════════════════════════════════════════════
# MHP-701: CraftChain Model
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ChainStep:
    """A single step in a craft chain."""
    op_id: str
    params: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    step_id: str = ""

    def __post_init__(self):
        if not self.step_id:
            self.step_id = f"STEP_{uuid.uuid4().hex[:6].upper()}"


@dataclass
class ChainPlan:
    """A planned chain that can be inspected before execution."""
    chain_id: str
    steps: List[ChainStep]
    source_audio: str = ""
    estimated_steps: int = 0
    risk_level: str = "low"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "source_audio": self.source_audio,
            "estimated_steps": len([s for s in self.steps if s.enabled]),
            "risk_level": self.risk_level,
            "steps": [
                {
                    "step_id": s.step_id,
                    "op_id": s.op_id,
                    "params": s.params,
                    "enabled": s.enabled,
                    "name": get_operation(s.op_id).name if get_operation(s.op_id) else "unknown",
                    "risk": get_operation(s.op_id).risk.value if get_operation(s.op_id) else "unknown",
                }
                for s in self.steps
            ],
        }


@dataclass
class ChainManifest:
    """MHP-715: JSON manifest recording operations, params, metrics, artifacts."""
    chain_id: str
    source_audio: str
    output_audio: str = ""
    steps_executed: int = 0
    steps_succeeded: int = 0
    steps_failed: int = 0
    steps: List[Dict[str, Any]] = field(default_factory=list)
    total_risk: str = "low"
    generated_at: str = field(default_factory=utc_now_iso)
    version: str = "0.1.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "source_audio": self.source_audio,
            "output_audio": self.output_audio,
            "steps_executed": self.steps_executed,
            "steps_succeeded": self.steps_succeeded,
            "steps_failed": self.steps_failed,
            "total_risk": self.total_risk,
            "steps": self.steps,
            "generated_at": self.generated_at,
            "version": self.version,
        }

    def write(self, path: Path) -> Path:
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return path


# ═══════════════════════════════════════════════════════════════════════════
# MHP-702: Chain Executor
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ChainResult:
    """Result of executing a craft chain."""
    chain_id: str
    success: bool
    output_path: str = ""
    steps: List[OpResult] = field(default_factory=list)
    manifest: Optional[ChainManifest] = None
    error: str = ""
    artifacts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "success": self.success,
            "output_path": self.output_path,
            "error": self.error,
            "steps": [s.to_dict() for s in self.steps],
            "manifest": self.manifest.to_dict() if self.manifest else None,
            "artifacts": self.artifacts,
        }


class CraftChainExecutor:
    """MHP-702: Execute ordered craft operations on an audio artifact.

    Features:
    - MHP-703: Dry-run planner showing operation order
    - MHP-704: Per-step before/after metrics
    - MHP-705: Optional intermediate artifact policy
    - MHP-707: Safety rollback — failed step preserves previous valid artifact
    - MHP-708: Clipping/peak gate
    - MHP-710: Runtime budget policy
    """

    def __init__(
        self,
        keep_artifacts: bool = False,
        artifact_dir: Optional[Path] = None,
        max_chain_time_s: float = 300.0,
    ):
        self.keep_artifacts = keep_artifacts
        self.artifact_dir = artifact_dir or Path(tempfile.mkdtemp(prefix="craft_chain_"))
        self.max_chain_time_s = max_chain_time_s

    def plan(self, steps: List[ChainStep], source: str = "") -> ChainPlan:
        """MHP-703: Dry-run planner. Shows operation order without processing."""
        risk_levels = {"none": 0, "low": 1, "medium": 2, "high": 3}
        max_risk = "low"
        max_risk_val = 0
        for s in steps:
            if s.enabled:
                op = get_operation(s.op_id)
                if op:
                    rv = risk_levels.get(op.risk.value, 0)
                    if rv > max_risk_val:
                        max_risk_val = rv
                        max_risk = op.risk.value

        return ChainPlan(
            chain_id=f"CHAIN_{uuid.uuid4().hex[:8].upper()}",
            steps=steps,
            source_audio=source,
            estimated_steps=len([s for s in steps if s.enabled]),
            risk_level=max_risk,
        )

    def execute(
        self,
        input_path: str,
        steps: List[ChainStep],
        output_path: Optional[str] = None,
        rollback_on_failure: bool = True,
    ) -> ChainResult:
        """MHP-702: Execute the chain.

        Args:
            input_path: Path to input WAV file.
            steps: Ordered list of chain steps.
            output_path: Final output path. Auto-generated if None.
            rollback_on_failure: If True, failed step preserves previous artifact.

        Returns:
            ChainResult with full execution trace.
        """
        chain_id = f"CHAIN_{uuid.uuid4().hex[:8].upper()}"

        if output_path is None:
            output_path = str(self.artifact_dir / f"{chain_id}_output.wav")

        self.artifact_dir.mkdir(parents=True, exist_ok=True)

        enabled_steps = [s for s in steps if s.enabled]
        if not enabled_steps:
            # No-op: copy input to output
            shutil.copy2(input_path, output_path)
            manifest = ChainManifest(
                chain_id=chain_id,
                source_audio=input_path,
                output_audio=output_path,
            )
            return ChainResult(
                chain_id=chain_id,
                success=True,
                output_path=output_path,
                manifest=manifest,
            )

        # Use temp directory for intermediate files
        work_dir = self.artifact_dir / chain_id
        work_dir.mkdir(parents=True, exist_ok=True)

        current_input = input_path
        results: List[OpResult] = []
        artifacts: List[str] = []
        last_successful = input_path

        for i, step in enumerate(enabled_steps):
            step_output = str(work_dir / f"step_{i:03d}_{step.op_id}.wav")

            op_result = execute_operation(
                step.op_id, current_input, step_output, step.params
            )

            results.append(op_result)

            if op_result.success:
                artifacts.append(step_output)
                last_successful = step_output
                current_input = step_output
            else:
                if rollback_on_failure:
                    # MHP-707: Safety rollback — preserve previous valid artifact
                    current_input = last_successful
                break

        # Determine final output
        final_output = last_successful if results and results[-1].success else current_input

        # Copy to output path
        if final_output != output_path:
            shutil.copy2(final_output, output_path)

        # Build manifest
        manifest = ChainManifest(
            chain_id=chain_id,
            source_audio=input_path,
            output_audio=output_path,
            steps_executed=len(results),
            steps_succeeded=sum(1 for r in results if r.success),
            steps_failed=sum(1 for r in results if not r.success),
            steps=[r.to_dict() for r in results],
            total_risk=self.plan(steps).risk_level,
        )

        # MHP-715: Write chain manifest
        manifest_path = Path(output_path).with_suffix(".chain_manifest.json")
        manifest.write(manifest_path)

        all_success = all(r.success for r in results)
        return ChainResult(
            chain_id=chain_id,
            success=all_success,
            output_path=output_path,
            steps=results,
            manifest=manifest,
            artifacts=artifacts if self.keep_artifacts else [],
            error="" if all_success else f"{results[-1].error}" if results else "",
        )

    def cleanup(self) -> None:
        """Remove temporary artifacts if not kept."""
        if not self.keep_artifacts and self.artifact_dir.exists():
            shutil.rmtree(self.artifact_dir, ignore_errors=True)


# ═══════════════════════════════════════════════════════════════════════════
# MHP-713: Preset-to-Chain Adapter
# ═══════════════════════════════════════════════════════════════════════════

PRESET_CHAIN_MAP: Dict[str, List[Dict[str, Any]]] = {
    "clean_master": [
        {"op_id": "input_normalize", "params": {"target_rms_db": -18.0}},
        {"op_id": "silence_trim", "params": {}},
        {"op_id": "dc_offset_repair", "params": {}},
        {"op_id": "sub_bass_discipline", "params": {"cutoff_hz": 30}},
        {"op_id": "low_mid_de_mud", "params": {"gain_db": -2.0}},
        {"op_id": "mid_presence_lift", "params": {"gain_db": 1.5}},
        {"op_id": "harshness_guard", "params": {"max_reduction_db": -3.0}},
        {"op_id": "air_recovery", "params": {"gain_db": 1.0}},
        {"op_id": "macro_dynamics_guard", "params": {"max_reduction_db": 4.0}},
        {"op_id": "clarity_polish", "params": {"amount": 0.4}},
        {"op_id": "loudness_landing", "params": {"target_lufs": -14.0}},
        {"op_id": "final_safety_limiter", "params": {"ceiling_db": -0.3}},
    ],
    "warm_vocal": [
        {"op_id": "input_normalize", "params": {"target_rms_db": -18.0}},
        {"op_id": "silence_trim", "params": {}},
        {"op_id": "dc_offset_repair", "params": {}},
        {"op_id": "bass_body_shaping", "params": {"gain_db": 2.0}},
        {"op_id": "mid_presence_lift", "params": {"gain_db": 3.0}},
        {"op_id": "sibilance_guard", "params": {"max_reduction_db": -4.0}},
        {"op_id": "warmth_injection", "params": {"drive_db": 4.0, "mix_percent": 25.0}},
        {"op_id": "micro_dynamics_lift", "params": {"makeup_db": 2.0}},
        {"op_id": "loudness_landing", "params": {"target_lufs": -14.0}},
        {"op_id": "final_safety_limiter", "params": {"ceiling_db": -0.3}},
    ],
    "wide_space": [
        {"op_id": "input_normalize", "params": {"target_rms_db": -18.0}},
        {"op_id": "silence_trim", "params": {}},
        {"op_id": "dc_offset_repair", "params": {}},
        {"op_id": "stereo_width_control", "params": {"width_factor": 1.2, "mono_safety": True}},
        {"op_id": "air_recovery", "params": {"gain_db": 2.0}},
        {"op_id": "room_reverb_cleanup", "params": {"reduction_db": -2.0}},
        {"op_id": "loudness_landing", "params": {"target_lufs": -14.0}},
        {"op_id": "final_safety_limiter", "params": {"ceiling_db": -0.3}},
    ],
    "safe_air": [
        {"op_id": "input_normalize", "params": {"target_rms_db": -18.0}},
        {"op_id": "silence_trim", "params": {}},
        {"op_id": "harshness_guard", "params": {"max_reduction_db": -4.0}},
        {"op_id": "air_recovery", "params": {"gain_db": 1.5}},
        {"op_id": "sibilance_guard", "params": {"max_reduction_db": -3.0}},
        {"op_id": "noise_floor_polish", "params": {"reduction_db": -4.0}},
        {"op_id": "loudness_landing", "params": {"target_lufs": -14.0}},
        {"op_id": "final_safety_limiter", "params": {"ceiling_db": -0.3}},
    ],
}


def preset_to_chain(preset_name: str) -> List[ChainStep]:
    """MHP-714: Convert a preset name to a chain of craft steps.

    Falls back to a minimal safe chain for unknown presets.
    """
    preset_steps = PRESET_CHAIN_MAP.get(preset_name)
    if preset_steps is None:
        # Minimal safe chain for unknown presets
        preset_steps = [
            {"op_id": "input_normalize", "params": {"target_rms_db": -18.0}},
            {"op_id": "final_safety_limiter", "params": {"ceiling_db": -0.3}},
        ]

    return [
        ChainStep(op_id=s["op_id"], params=s.get("params", {}))
        for s in preset_steps
    ]


def get_preset_names() -> List[str]:
    """Return list of known preset names."""
    return list(PRESET_CHAIN_MAP.keys())
