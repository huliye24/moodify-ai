"""Machine-Human agreement analysis (MFY-CR-P07).

Never a single percentage that hides disagreement. Reports the specific
patterns that matter for learning.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgreementAnalysis:
    n: int
    technical_top_matches_human_top: int
    technical_top_matches_identity_top: int
    source_technical_rank: str | None
    source_human_rank: str | None
    patterns: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "n": self.n,
            "technical_top_matches_human_top": self.technical_top_matches_human_top,
            "technical_top_matches_identity_top": self.technical_top_matches_identity_top,
            "source_technical_rank": self.source_technical_rank,
            "source_human_rank": self.source_human_rank,
            "patterns": list(self.patterns),
        }


def analyze_agreement(records: list[dict[str, object]]) -> AgreementAnalysis:
    """Analyse agreement across learning records.

    Each record dict: technical_rank, human_rank, identity_preservation_rank,
    identity_guard_results, source_vs_winner_result.
    """
    n = len(records)
    tech_human = 0
    tech_identity = 0
    patterns: list[str] = []
    source_tech: list[str] = []
    source_human: list[str] = []

    for r in records:
        tech = r.get("technical_rank")
        human = r.get("human_rank")
        identity = r.get("identity_preservation_rank")
        if tech and human and tech == human:
            tech_human += 1
        if tech and identity and tech == identity:
            tech_identity += 1

        ig = r.get("identity_guard_results") or {}
        if tech and human and tech != human:
            patterns.append("TECH_RANKING_OK_BUT_HUMAN_DISAGREES")
        if human and ig.get("verdict") == "CAUTION" and human in ("A", "B", "C"):
            patterns.append("HUMAN_LIKES_BUT_IDENTITY_CAUTION")
        if r.get("source_vs_winner_result") == "SOURCE_WINS":
            patterns.append("SOURCE_WINS")
        if tech and not human:
            patterns.append("MACHINE_CONFIDENT_HUMAN_MISSING")
        if human and not tech:
            patterns.append("HUMAN_CLEAR_MACHINE_MISSING")

        if r.get("source_technical_rank"):
            source_tech.append(str(r["source_technical_rank"]))
        if r.get("source_human_rank"):
            source_human.append(str(r["source_human_rank"]))

    return AgreementAnalysis(
        n=n,
        technical_top_matches_human_top=tech_human,
        technical_top_matches_identity_top=tech_identity,
        source_technical_rank=sorted(set(source_tech))[0] if source_tech else None,
        source_human_rank=sorted(set(source_human))[0] if source_human else None,
        patterns=tuple(sorted(set(patterns))),
    )
