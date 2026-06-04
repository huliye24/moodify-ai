"""MHP-719-730: Craft Selector and Intelligence.

Rule-based craft selection from CT/MRS/tidal evidence, risk-aware operation
limits, feedback hooks, and memory writeback.

Part of ECHAIN-MOODIFY-CRAFT-22-012 / NEM-CRAFT-INTELLIGENCE-SYSTEM-038.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .craft_chain import ChainStep, preset_to_chain
from .craft_processes import CRAFT_REGISTRY, RiskLevel, get_operation


# ═══════════════════════════════════════════════════════════════════════════
# MHP-719: Craft Selection Input
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class CraftSelectionInput:
    """Input evidence for craft selection.

    MHP-719: CT, MRS, preset, operator notes accepted.
    """
    # Acoustic CT findings
    ct_findings: List[Dict[str, Any]] = field(default_factory=list)

    # MRS scores
    mrs_score: Optional[float] = None
    mrs_target: Optional[float] = None

    # Preset hint
    preset_hint: str = ""

    # Tidal cycle context
    tidal_cycle_active: bool = False
    tidal_priority: str = "quality"  # quality | speed | experiment

    # Operator notes
    operator_notes: str = ""

    # Genre context
    genre: str = ""

    # Risk tolerance
    max_risk: str = "medium"  # low | medium | high


# ═══════════════════════════════════════════════════════════════════════════
# MHP-720: Rule-Based Selector v1
# ═══════════════════════════════════════════════════════════════════════════

# Genre-to-recommended-operations mapping
GENRE_RECOMMENDATIONS: Dict[str, List[str]] = {
    "electronic": [
        "sub_bass_discipline", "harshness_guard", "transient_soften",
        "stereo_width_control", "clarity_polish", "loudness_landing",
    ],
    "rock": [
        "macro_dynamics_guard", "harshness_guard", "bass_body_shaping",
        "mid_presence_lift", "loudness_landing",
    ],
    "vocal": [
        "sibilance_guard", "mid_presence_lift", "warmth_injection",
        "center_focus", "micro_dynamics_lift",
    ],
    "folk": [
        "warmth_injection", "air_recovery", "noise_floor_polish",
        "mid_presence_lift",
    ],
    "classical": [
        "macro_dynamics_guard", "air_recovery", "room_reverb_cleanup",
    ],
    "hiphop": [
        "sub_bass_discipline", "bass_body_shaping", "transient_restore",
        "loudness_landing",
    ],
    "jazz": [
        "warmth_injection", "air_recovery", "center_focus",
        "micro_dynamics_lift",
    ],
}

# CT finding → recommended operation
CT_RESPONSE_MAP: Dict[str, Dict[str, Any]] = {
    "sub_bass_excessive": {
        "op_id": "sub_bass_discipline",
        "params": {"cutoff_hz": 35, "reduction_db": -8.0},
        "reasoning": "CT detected excessive sub-bass energy",
    },
    "low_mid_muddy": {
        "op_id": "low_mid_de_mud",
        "params": {"gain_db": -3.0, "center_hz": 250},
        "reasoning": "CT detected low-mid muddiness",
    },
    "harsh_upper_mid": {
        "op_id": "harshness_guard",
        "params": {"max_reduction_db": -5.0},
        "reasoning": "CT detected harshness in upper mids",
    },
    "sibilant": {
        "op_id": "sibilance_guard",
        "params": {"max_reduction_db": -6.0},
        "reasoning": "CT detected excessive sibilance",
    },
    "dull_air": {
        "op_id": "air_recovery",
        "params": {"gain_db": 2.5},
        "reasoning": "CT detected lack of air/brilliance",
    },
    "thin_bass": {
        "op_id": "bass_body_shaping",
        "params": {"gain_db": 3.0},
        "reasoning": "CT detected thin bass body",
    },
    "over_compressed": {
        "op_id": "transient_restore",
        "params": {"amount_db": 3.0},
        "reasoning": "CT detected over-compression; restoring transients",
    },
    "spiky_transients": {
        "op_id": "transient_soften",
        "params": {"threshold_db": -8.0, "ratio": 2.5},
        "reasoning": "CT detected spiky transients",
    },
    "narrow_stereo": {
        "op_id": "stereo_width_control",
        "params": {"width_factor": 1.3, "mono_safety": True},
        "reasoning": "CT detected narrow stereo image",
    },
    "noisy_floor": {
        "op_id": "noise_floor_polish",
        "params": {"reduction_db": -5.0},
        "reasoning": "CT detected elevated noise floor",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# MHP-721: Risk-Aware Operation Limits
# ═══════════════════════════════════════════════════════════════════════════

DANGEROUS_COMBINATIONS = [
    (["transient_soften", "transient_restore"],
     "warning", "Transient soften and restore applied together may cancel out"),
    (["sub_bass_discipline", "bass_body_shaping"],
     "warning", "Sub-bass discipline + bass shaping combined may produce uneven low end"),
    (["macro_dynamics_guard", "transient_soften"],
     "warning", "Macro dynamics guard + transient soften may over-compress"),
    (["warmth_injection", "clarity_polish"],
     "info", "Warmth + clarity together: verify no muddiness"),
    (["harshness_guard", "sibilance_guard"],
     "info", "Multiple high-frequency reductions: verify no dullness"),
]


def check_dangerous_combinations(op_ids: List[str]) -> List[Dict[str, str]]:
    """MHP-721: Check for dangerous operation combinations."""
    warnings = []
    op_set = set(op_ids)
    for combo, severity, message in DANGEROUS_COMBINATIONS:
        if all(op in op_set for op in combo):
            warnings.append({"severity": severity, "message": message, "operations": combo})
    return warnings


def filter_by_risk(
    op_ids: List[str],
    max_risk: str = "medium",
) -> List[str]:
    """Filter operations by maximum allowed risk level."""
    risk_vals = {"none": 0, "low": 1, "medium": 2, "high": 3}
    max_val = risk_vals.get(max_risk, 2)
    return [
        oid for oid in op_ids
        if risk_vals.get(get_operation(oid).risk.value if get_operation(oid) else "low", 0) <= max_val
    ]


# ═══════════════════════════════════════════════════════════════════════════
# Selector v1
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SelectionResult:
    """Result of craft selection."""
    steps: List[ChainStep]
    reasoning: List[str] = field(default_factory=list)
    warnings: List[Dict[str, str]] = field(default_factory=list)
    risk_level: str = "low"
    source: str = ""  # "preset" | "ct_diagnosis" | "genre" | "hybrid"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "steps": [
                {
                    "op_id": s.op_id,
                    "params": s.params,
                    "name": get_operation(s.op_id).name if get_operation(s.op_id) else "unknown",
                }
                for s in self.steps
            ],
            "reasoning": self.reasoning,
            "warnings": self.warnings,
            "risk_level": self.risk_level,
            "source": self.source,
        }


def select_craft(input_data: CraftSelectionInput) -> SelectionResult:
    """MHP-720: Rule-based craft selector v1.

    Selection priority:
    1. CT findings → specific operations
    2. Genre → recommended operations
    3. Preset hint → preset-to-chain
    4. Always include safety operations (loudness_landing, final_safety_limiter)
    """
    reasoning: List[str] = []
    selected_ops: Dict[str, Dict[str, Any]] = {}

    # ── Layer 1: CT diagnosis-driven selection ──
    if input_data.ct_findings:
        for finding in input_data.ct_findings:
            finding_type = finding.get("type", finding.get("finding", ""))
            if finding_type in CT_RESPONSE_MAP:
                response = CT_RESPONSE_MAP[finding_type]
                selected_ops[response["op_id"]] = response["params"]
                reasoning.append(f"CT finding '{finding_type}': {response['reasoning']}")

    # ── Layer 2: Genre-based recommendations ──
    if input_data.genre:
        genre_lower = input_data.genre.lower()
        for genre_key, ops in GENRE_RECOMMENDATIONS.items():
            if genre_key in genre_lower:
                for op_id in ops:
                    if op_id not in selected_ops:
                        selected_ops[op_id] = {}
                reasoning.append(f"Genre '{input_data.genre}' matched '{genre_key}': added {len(ops)} operations")
                break

    # ── Layer 3: Preset hint ──
    if input_data.preset_hint and not input_data.ct_findings:
        preset_steps = preset_to_chain(input_data.preset_hint)
        for step in preset_steps:
            if step.op_id not in selected_ops:
                selected_ops[step.op_id] = step.params
        reasoning.append(f"Preset '{input_data.preset_hint}' added {len(preset_steps)} operations")
        source = "preset"
    else:
        source = "ct_diagnosis" if input_data.ct_findings else "hybrid"

    # ── Layer 4: Tidal cycle adjustments ──
    if input_data.tidal_cycle_active:
        if input_data.tidal_priority == "speed":
            # Remove non-essential operations for speed
            for non_essential in ["room_reverb_cleanup", "warmth_injection", "clarity_polish"]:
                selected_ops.pop(non_essential, None)
            reasoning.append("Tidal speed mode: removed non-essential polish operations")
        elif input_data.tidal_priority == "experiment":
            reasoning.append("Tidal experiment mode: keeping all selected operations for comparison")

    # ── Layer 5: Always include safety ──
    for safety_op in ["loudness_landing", "final_safety_limiter"]:
        if safety_op not in selected_ops:
            selected_ops[safety_op] = {}
    reasoning.append("Added safety operations: loudness_landing, final_safety_limiter")

    # ── Build ordered chain ──
    # Order: PREPARE -> CORRECTIVE -> ENHANCE -> DYNAMICS -> SPATIAL -> POLISH -> SAFETY
    category_order = {cat: i for i, cat in enumerate([
        "prepare", "corrective", "enhance", "dynamics", "spatial", "polish", "safety",
    ])}

    ordered = sorted(
        selected_ops.items(),
        key=lambda item: category_order.get(
            get_operation(item[0]).category.value if get_operation(item[0]) else "enhance",
            3,
        ),
    )

    steps = [ChainStep(op_id=oid, params=params) for oid, params in ordered]

    # ── Risk filtering ──
    steps = [
        s for s in steps
        if get_operation(s.op_id) and
        {"none": 0, "low": 1, "medium": 2, "high": 3}.get(
            get_operation(s.op_id).risk.value, 0
        ) <= {"none": 0, "low": 1, "medium": 2, "high": 3}.get(input_data.max_risk, 2)
    ]

    # ── Check dangerous combinations ──
    warnings = check_dangerous_combinations([s.op_id for s in steps])

    # Determine overall risk
    risk_vals = [{"none": 0, "low": 1, "medium": 2, "high": 3}.get(
        get_operation(s.op_id).risk.value if get_operation(s.op_id) else "low", 0
    ) for s in steps]
    max_risk_val = max(risk_vals) if risk_vals else 0
    risk_level = {0: "none", 1: "low", 2: "medium", 3: "high"}.get(max_risk_val, "low")

    return SelectionResult(
        steps=steps,
        reasoning=reasoning,
        warnings=warnings,
        risk_level=risk_level,
        source=source,
    )


# ═══════════════════════════════════════════════════════════════════════════
# MHP-728: 22-Process Coverage Report
# ═══════════════════════════════════════════════════════════════════════════

def generate_coverage_report(
    operation_usage: Dict[str, int],
) -> Dict[str, Any]:
    """Generate a coverage report showing which operations are used.

    MHP-728: Reports which operations are used across runs.
    """
    all_ops = list(CRAFT_REGISTRY.keys())
    coverage = {}
    for op_id in all_ops:
        count = operation_usage.get(op_id, 0)
        op = get_operation(op_id)
        coverage[op_id] = {
            "name": op.name if op else op_id,
            "category": op.category.value if op else "unknown",
            "usage_count": count,
            "covered": count > 0,
        }

    total = len(all_ops)
    covered = sum(1 for v in coverage.values() if v["covered"])
    return {
        "total_operations": total,
        "covered_operations": covered,
        "coverage_pct": round(100.0 * covered / max(total, 1), 1),
        "operations": coverage,
        "uncovered": [op_id for op_id, v in coverage.items() if not v["covered"]],
    }
