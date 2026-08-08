"""ValidationRule — each rule answers a historical question.

Every rule must carry historical_source: which failure made this rule a
necessary boundary. Rules without a source are marked `unproven` and do not
count toward a PASS verdict. Rule sets are bound per capability from the
registry's quality_policy; providers cannot disable rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from moodify.capability_registry.model import CapabilityRegistry

RuleLevel = str  # "error" | "warning"


@dataclass(frozen=True)
class RuleResult:
    rule_id: str
    passed: bool
    level: RuleLevel
    measured: object = None
    expected: object = None
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "passed": self.passed,
            "level": self.level,
            "measured": self.measured,
            "expected": self.expected,
            "message": self.message,
        }


@dataclass(frozen=True)
class ValidationRule:
    rule_id: str
    description: str
    level: RuleLevel
    historical_source: str  # geological record: which failure made this boundary
    check: Callable[[dict], RuleResult]

    def evaluate(self, context: dict) -> RuleResult:
        return self.check(context)


@dataclass(frozen=True)
class ValidationReport:
    capability_id: str
    results: tuple[RuleResult, ...]

    def errors(self) -> tuple[RuleResult, ...]:
        return tuple(r for r in self.results if r.level == "error" and not r.passed)

    def warnings(self) -> tuple[RuleResult, ...]:
        return tuple(r for r in self.results if r.level == "warning" and not r.passed)

    def passed(self) -> bool:
        return not self.errors()

    def to_dict(self) -> dict:
        return {
            "capability_id": self.capability_id,
            "passed": self.passed(),
            "results": [r.to_dict() for r in self.results],
        }


# ── generic rule implementations (each with a historical source) ─────────

def _rule_output_exists() -> ValidationRule:
    def check(ctx: dict) -> RuleResult:
        artifacts = ctx.get("artifacts", [])
        return RuleResult(
            rule_id="output_exists",
            passed=bool(artifacts),
            level="error",
            measured=len(artifacts),
            expected=">= 1",
            message="provider produced no output files",
        )

    return ValidationRule(
        rule_id="output_exists",
        description="At least one non-empty output file exists",
        level="error",
        historical_source="009 FAILURE_LEDGER #10: MuseScore produced no output files was once "
        "reported as success (artifact collection empty)",
        check=check,
    )


def _rule_nonzero_size() -> ValidationRule:
    def check(ctx: dict) -> RuleResult:
        bad = [
            a for a in ctx.get("artifacts", [])
            if not Path(a).exists() or Path(a).stat().st_size == 0
        ]
        return RuleResult(
            rule_id="nonzero_size",
            passed=not bad,
            level="error",
            measured=[str(Path(a).name) for a in bad],
            expected="all artifacts non-empty",
            message="empty or missing artifacts detected",
        )

    return ValidationRule(
        rule_id="nonzero_size",
        description="All artifacts have non-zero size",
        level="error",
        historical_source="009 FAILURE_LEDGER #4: empty SVG collection was treated as "
        "successful export; empty outputs must be visible",
        check=check,
    )


def _rule_source_hash_linked() -> ValidationRule:
    def check(ctx: dict) -> RuleResult:
        hashes = ctx.get("input_hashes", {})
        return RuleResult(
            rule_id="source_hash_linked",
            passed=bool(hashes) and all(len(h) == 64 for h in hashes.values()),
            level="error",
            measured=list(hashes.keys()),
            expected="all input roles hash-linked",
            message="input hashes missing or malformed",
        )

    return ValidationRule(
        rule_id="source_hash_linked",
        description="Inputs are hash-linked in evidence",
        level="error",
        historical_source="MOODIFY_ENGINEERING_THICKNESS_STANDARD §4.4: derived data must not "
        "become authoritative without source linkage",
        check=check,
    )


def _rule_no_nan() -> ValidationRule:
    def check(ctx: dict) -> RuleResult:
        artifact = ctx.get("primary_artifact")
        if artifact is None or not Path(artifact).exists():
            return RuleResult(rule_id="no_nan", passed=True, level="error")
        data = Path(artifact).read_bytes()[:64]
        nan_marker = b"nan" in data.lower() or b"inf" in data.lower()
        return RuleResult(
            rule_id="no_nan",
            passed=not nan_marker,
            level="error",
            measured=bool(nan_marker),
            expected=False,
            message="NaN/Inf marker detected in output",
        )

    return ValidationRule(
        rule_id="no_nan",
        description="Output contains no NaN/Inf markers",
        level="error",
        historical_source="Audio DSP history: NaN pollution from transformations propagates "
        "silently into loudness/mastering; must be rejected at capability boundary",
        check=check,
    )


def _rule_page_count_nonzero() -> ValidationRule:
    def check(ctx: dict) -> RuleResult:
        pdfs = [a for a in ctx.get("artifacts", []) if str(a).endswith(".pdf")]
        if not pdfs:
            return RuleResult(rule_id="page_count_nonzero", passed=True, level="error")
        ok = all(Path(a).exists() and Path(a).stat().st_size > 1000 for a in pdfs)
        return RuleResult(
            rule_id="page_count_nonzero",
            passed=ok,
            level="error",
            measured=[str(Path(a).name) for a in pdfs],
            expected="PDFs with content",
            message="PDF artifacts too small to contain pages",
        )

    return ValidationRule(
        rule_id="page_count_nonzero",
        description="Rendered PDFs contain pages",
        level="error",
        historical_source="notation.render contract: empty/glyphless PDF would be a "
        "false-success export",
        check=check,
    )


def _rule_roundtrip_visible() -> ValidationRule:
    def check(ctx: dict) -> RuleResult:
        report = ctx.get("roundtrip_report")
        if report is None:
            return RuleResult(rule_id="roundtrip_visible", passed=True, level="error")
        verdict = report.get("verdict", "MISSING")
        return RuleResult(
            rule_id="roundtrip_visible",
            passed=verdict in ("PASS", "WARNINGS"),
            level="error",
            measured=verdict,
            expected="PASS or WARNINGS",
            message="round-trip FAIL: critical fields not preserved",
        )

    return ValidationRule(
        rule_id="roundtrip_visible",
        description="Round-trip report does not hide critical losses",
        level="error",
        historical_source="009 ROUNDTRIP_LOSS_CONTRACT: '成功导出' must never mask semantic "
        "loss; EX-005 in EXPERIENCE_REGISTRY",
        check=check,
    )


# ── registry binding ──────────────────────────────────────────────────────

_COMMON: dict[str, ValidationRule] = {r.rule_id: r for r in (
    _rule_output_exists(),
    _rule_nonzero_size(),
    _rule_source_hash_linked(),
    _rule_no_nan(),
    _rule_page_count_nonzero(),
    _rule_roundtrip_visible(),
)}

# per-capability extra rules (beyond common set), keyed by capability_id
_CAPABILITY_RULES: dict[str, tuple[str, ...]] = {
    "notation.render": ("page_count_nonzero", "roundtrip_visible"),
    "media.transcode": ("nonzero_size", "source_hash_linked"),
    "media.probe": ("output_exists",),
    "audio.measure_loudness": ("output_exists",),
    "audio.time_stretch": ("no_nan", "source_hash_linked"),
    "audio.separate_manifest": ("source_hash_linked",),
    "waveform.region_edit": ("source_hash_linked",),
}


def common_rules() -> dict[str, ValidationRule]:
    return dict(_COMMON)


def rules_for_capability(
    capability_id: str,
    registry: CapabilityRegistry | None = None,
) -> tuple[ValidationRule, ...]:
    """Return rule set for a capability: common rules filtered by declared
    validation list + per-capability extras. Rules cannot be disabled."""
    declared: set[str] = set()
    if registry is not None:
        cap = registry.get_capability(capability_id)
        if cap is not None:
            declared = set(cap.validation)
    extras = set(_CAPABILITY_RULES.get(capability_id, ()))
    selected: list[ValidationRule] = []
    for rule_id in sorted(declared | extras):
        rule = _COMMON.get(rule_id)
        if rule is not None:
            selected.append(rule)
    return tuple(selected)


def validate_capability(
    capability_id: str,
    context: dict,
    registry: CapabilityRegistry | None = None,
) -> ValidationReport:
    rules = rules_for_capability(capability_id, registry)
    if not rules:
        return ValidationReport(capability_id=capability_id, results=())
    results = tuple(rule.evaluate(context) for rule in rules)
    return ValidationReport(capability_id=capability_id, results=results)
