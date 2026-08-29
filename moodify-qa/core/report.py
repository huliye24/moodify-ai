"""QA Report generator - formatted output for CLI and API."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


@dataclass
class QAReport:
    """Formatted QA report for display and export."""

    track: str
    duration_seconds: float
    sample_rate: int
    channels: int

    technical_score: float
    musical_score: float
    qa_score: float

    issues: list[dict]
    recommendations: list[dict]
    breakdown: dict

    raw_analysis: dict = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @classmethod
    def from_scoring_result(cls, scoring_result, analysis_result) -> QAReport:
        """Create report from scoring and analysis results."""
        from core.analyzer import AudioAnalysisResult
        from core.scoring import QAScoringResult
        return cls(
            track=scoring_result.track,
            duration_seconds=analysis_result.duration_seconds,
            sample_rate=analysis_result.sample_rate,
            channels=analysis_result.channels,
            technical_score=scoring_result.technical_score,
            musical_score=scoring_result.musical_score,
            qa_score=scoring_result.qa_score,
            issues=[i.to_dict() for i in scoring_result.issues],
            recommendations=[r.to_dict() for r in scoring_result.recommendations],
            breakdown=scoring_result.breakdown.to_dict(),
            raw_analysis=analysis_result.to_dict(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "track": self.track,
            "duration_seconds": round(self.duration_seconds, 3),
            "sample_rate_hz": self.sample_rate,
            "channels": self.channels,
            "qa_score": round(self.qa_score, 1),
            "technical_score": round(self.technical_score, 1),
            "musical_score": round(self.musical_score, 1),
            "issues": self.issues,
            "recommendations": self.recommendations,
            "breakdown": self.breakdown,
            "generated_at": self.generated_at,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save_json(self, filepath: str | Path) -> Path:
        """Save report as JSON file."""
        filepath = Path(filepath)
        filepath.write_text(self.to_json(), encoding="utf-8")
        return filepath

    def display(self, console: Console | None = None) -> None:
        """Display formatted report to console."""
        if console is None:
            console = Console()

        # Header
        console.print()
        console.print(Panel.fit(
            Text("Moodify QA Report", style="bold cyan", justify="center"),
            border_style="cyan",
        ))
        console.print()

        # Track info
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Label", style="dim")
        info_table.add_column("Value", style="white")
        info_table.add_row("Track:", self.track)
        info_table.add_row("Duration:", f"{self.duration_seconds:.2f}s")
        info_table.add_row("Sample Rate:", f"{self.sample_rate:,} Hz")
        info_table.add_row("Channels:", "Stereo" if self.channels >= 2 else "Mono")
        console.print(info_table)
        console.print()

        # Scores
        score_table = Table(title="Quality Scores", show_edge=False)
        score_table.add_column("Category", style="cyan")
        score_table.add_column("Score", justify="right")
        score_table.add_column("Rating", justify="center")

        def get_rating(score: float) -> str:
            if score >= 90:
                return "[green]Excellent[/green]"
            elif score >= 80:
                return "[green]Good[/green]"
            elif score >= 70:
                return "[yellow]Acceptable[/yellow]"
            elif score >= 60:
                return "[yellow]Fair[/yellow]"
            else:
                return "[red]Poor[/red]"

        score_table.add_row(
            "Technical Quality",
            f"{self.technical_score:.1f}/100",
            get_rating(self.technical_score)
        )
        score_table.add_row(
            "Musical Quality",
            f"{self.musical_score:.1f}/100",
            get_rating(self.musical_score)
        )
        score_table.add_row(
            "[bold]Overall QA Score[/bold]",
            f"[bold]{self.qa_score:.1f}/100[/bold]",
            get_rating(self.qa_score)
        )
        console.print(score_table)
        console.print()

        # Breakdown
        if self.breakdown:
            breakdown_table = Table(title="Score Breakdown", show_edge=False)
            breakdown_table.add_column("Dimension", style="cyan")
            breakdown_table.add_column("Sub-score", justify="right")

            tech = self.breakdown.get("technical", {})
            musical = self.breakdown.get("musical", {})

            breakdown_table.add_row("[dim]Technical[/dim]", "")
            breakdown_table.add_row("  Loudness", f"{tech.get('loudness', 0):.1f}")
            breakdown_table.add_row("  Dynamics", f"{tech.get('dynamics', 0):.1f}")
            breakdown_table.add_row("  Clipping", f"{tech.get('clipping', 0):.1f}")
            breakdown_table.add_row("  Noise", f"{tech.get('noise', 0):.1f}")
            breakdown_table.add_row("  Stereo", f"{tech.get('stereo', 0):.1f}")
            breakdown_table.add_row("[dim]Musical[/dim]", "")
            breakdown_table.add_row("  Balance", f"{musical.get('balance', 0):.1f}")
            breakdown_table.add_row("  Frequency", f"{musical.get('frequency', 0):.1f}")
            breakdown_table.add_row("  Energy", f"{musical.get('energy', 0):.1f}")

            console.print(breakdown_table)
            console.print()

        # Issues
        if self.issues:
            console.print(Panel("[bold red]Detected Issues[/bold red]", border_style="red"))
            for issue in self.issues:
                severity = issue.get("severity", "info")
                color = {
                    "critical": "red",
                    "warning": "yellow",
                    "info": "blue",
                }.get(severity, "white")

                console.print(f"  [{color}]●[/[{color}] {issue.get('message', 'Unknown issue')}")
                if issue.get("value") is not None:
                    console.print(f"    [dim]Metric: {issue.get('metric')} = {issue.get('value')}")
            console.print()
        else:
            console.print(Panel("[green]✓ No issues detected[/green]", border_style="green"))
            console.print()

        # Recommendations
        if self.recommendations:
            console.print(Panel("[bold yellow]Recommendations[/bold yellow]", border_style="yellow"))
            for i, rec in enumerate(self.recommendations[:5], 1):  # Top 5
                priority = rec.get("priority", 3)
                p_color = {1: "red", 2: "yellow", 3: "blue"}.get(priority, "white")
                console.print(f"  {i}. [{p_color}]P{priority}[/[{p_color}] {rec.get('action', 'N/A')}")
                console.print(f"     [dim]{rec.get('details', '')}")
            console.print()

        # Footer
        console.print(f"[dim]Report generated at {self.generated_at}[/dim]")
        console.print()

    def generate_markdown(self) -> str:
        """Generate markdown report."""
        lines = [
            "# Moodify QA Report",
            "",
            f"**Track:** {self.track}",
            f"**Duration:** {self.duration_seconds:.2f}s",
            f"**Sample Rate:** {self.sample_rate:,} Hz",
            f"**Channels:** {'Stereo' if self.channels >= 2 else 'Mono'}",
            "",
            "## Quality Scores",
            "",
            f"| Category | Score |",
            f"|----------|-------|",
            f"| Technical Quality | {self.technical_score:.1f}/100 |",
            f"| Musical Quality | {self.musical_score:.1f}/100 |",
            f"| **Overall QA Score** | **{self.qa_score:.1f}/100** |",
            "",
        ]

        if self.issues:
            lines.extend([
                "## Detected Issues",
                "",
            ])
            for issue in self.issues:
                severity = issue.get("severity", "info")
                lines.append(f"- **[{severity.upper()}]** {issue.get('message', 'Unknown issue')}")
            lines.append("")

        if self.recommendations:
            lines.extend([
                "## Recommendations",
                "",
            ])
            for i, rec in enumerate(self.recommendations, 1):
                priority = rec.get("priority", 3)
                lines.append(f"{i}. **[P{priority}]** {rec.get('action', 'N/A')}")
                lines.append(f"   {rec.get('details', '')}")
            lines.append("")

        lines.extend([
            "---",
            f"*Report generated at {self.generated_at}*",
        ])

        return "\n".join(lines)

    def save_markdown(self, filepath: str | Path) -> Path:
        """Save report as markdown file."""
        filepath = Path(filepath)
        filepath.write_text(self.generate_markdown(), encoding="utf-8")
        return filepath
