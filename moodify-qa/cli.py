"""Moodify QA CLI - Command line interface for audio quality analysis.

Usage:
    moodify-qa analyze <audio_file> [options]
    moodify-qa batch <audio_files>... [options]

Examples:
    moodify-qa analyze song.wav
    moodify-qa analyze song.wav --output report.json
    moodify-qa batch *.wav --output-dir ./reports
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from core.analyzer import AudioAnalyzer
from core.scoring import QAScorer
from core.report import QAReport

# Initialize CLI
app = typer.Typer(
    name="moodify-qa",
    help="Moodify QA - AI Audio Quality Assurance System",
    add_completion=False,
)
console = Console()

# Version
__version__ = "0.1.0"


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"Moodify QA v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit."
    ),
):
    """Moodify QA - AI Audio Quality Assurance Infrastructure."""
    pass


@app.command()
def analyze(
    audio_file: str = typer.Argument(..., help="Path to audio file to analyze"),
    output: Optional[str] = typer.Option(
        None, "--output", "-o",
        help="Output file path for JSON report"
    ),
    markdown: Optional[str] = typer.Option(
        None, "--markdown", "-m",
        help="Output file path for Markdown report"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Show detailed progress"
    ),
    raw: bool = typer.Option(
        False, "--raw",
        help="Output raw JSON to stdout instead of formatted report"
    ),
):
    """Analyze a single audio file and generate QA report."""
    filepath = Path(audio_file)

    if not filepath.exists():
        console.print(f"[red]Error: File not found: {filepath}[/red]")
        raise typer.Exit(1)

    if not filepath.suffix.lower() in ['.wav', '.mp3', '.flac', '.aiff', '.ogg', '.m4a']:
        console.print(f"[yellow]Warning: Unrecognized audio format: {filepath.suffix}[/yellow]")

    # Analyze
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        disable=not verbose,
    ) as progress:
        task = progress.add_task("Analyzing audio...", total=None)

        try:
            analyzer = AudioAnalyzer()
            analysis = analyzer.analyze(filepath)

            progress.update(task, description="Calculating QA score...")
            scorer = QAScorer()
            scoring = scorer.score(analysis)

            progress.update(task, description="Generating report...")
            report = QAReport.from_scoring_result(scoring, analysis)

        except Exception as e:
            console.print(f"[red]Analysis failed: {e}[/red]")
            raise typer.Exit(1)

    # Output
    if raw:
        # Raw JSON output
        console.print(report.to_json())
    else:
        # Formatted report
        report.display(console)

    # Save reports if requested
    if output:
        report.save_json(output)
        console.print(f"[green]✓ JSON report saved: {output}[/green]")

    if markdown:
        report.save_markdown(markdown)
        console.print(f"[green]✓ Markdown report saved: {markdown}[/green]")

    # Exit code based on QA score
    if report.qa_score < 60:
        raise typer.Exit(2)  # Poor quality
    elif report.qa_score < 80:
        raise typer.Exit(1)  # Fair quality
    else:
        raise typer.Exit(0)  # Good quality


@app.command()
def batch(
    audio_files: list[str] = typer.Argument(..., help="Audio files to analyze"),
    output_dir: str = typer.Option(
        "./reports", "--output-dir", "-d",
        help="Directory for output reports"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Show detailed progress"
    ),
):
    """Analyze multiple audio files in batch."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    analyzer = AudioAnalyzer(verbose=verbose)
    scorer = QAScorer()

    results = []
    errors = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing files...", total=len(audio_files))

        for fp in audio_files:
            filepath = Path(fp)
            progress.update(task, description=f"Analyzing {filepath.name}...")

            try:
                analysis = analyzer.analyze(filepath)
                scoring = scorer.score(analysis)
                report = QAReport.from_scoring_result(scoring, analysis)
                results.append(report)

                # Save individual report
                json_path = output_path / f"{filepath.stem}_qa_report.json"
                report.save_json(json_path)

            except Exception as e:
                errors.append((fp, str(e)))

            progress.advance(task)

    # Summary
    console.print()
    console.print("[bold]Batch Analysis Complete[/bold]")
    console.print(f"  Success: {len(results)}")
    console.print(f"  Failed: {len(errors)}")

    if results:
        avg_score = sum(r.qa_score for r in results) / len(results)
        console.print(f"  Average QA Score: {avg_score:.1f}")

        # Score distribution
        excellent = sum(1 for r in results if r.qa_score >= 90)
        good = sum(1 for r in results if 80 <= r.qa_score < 90)
        acceptable = sum(1 for r in results if 70 <= r.qa_score < 80)
        poor = sum(1 for r in results if r.qa_score < 70)

        console.print()
        console.print("[dim]Score Distribution:[/dim]")
        console.print(f"  [green]Excellent (90-100): {excellent}[/green]")
        console.print(f"  [green]Good (80-89): {good}[/green]")
        console.print(f"  [yellow]Acceptable (70-79): {acceptable}[/yellow]")
        console.print(f"  [red]Poor (<70): {poor}[/red]")

    if errors:
        console.print()
        console.print("[red]Errors:[/red]")
        for fp, err in errors:
            console.print(f"  {fp}: {err}")

    # Save summary
    summary = {
        "total_files": len(audio_files),
        "successful": len(results),
        "failed": len(errors),
        "average_qa_score": sum(r.qa_score for r in results) / len(results) if results else 0,
        "reports_directory": str(output_path.absolute()),
    }
    summary_path = output_path / "batch_summary.json"
    import json
    summary_path.write_text(json.dumps(summary, indent=2))
    console.print()
    console.print(f"[green]✓ Summary saved: {summary_path}[/green]")


@app.command()
def api(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="API server host"),
    port: int = typer.Option(8000, "--port", "-p", help="API server port"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload (dev mode)"),
):
    """Start the Moodify QA API server (FastAPI).

    This is a placeholder for future FastAPI implementation.
    """
    console.print("[yellow]API server not yet implemented in v0.1[/yellow]")
    console.print()
    console.print("Planned endpoints:")
    console.print("  POST /qa/analyze - Upload and analyze audio file")
    console.print("  GET  /qa/report/{id} - Get analysis report by ID")
    console.print("  POST /qa/batch - Batch analyze multiple files")
    console.print()
    console.print("For now, use the CLI commands:")
    console.print("  moodify-qa analyze <file>")
    console.print("  moodify-qa batch <files...>")


# Entry point for direct execution
def cli_entry():
    """Entry point for console script."""
    app()


if __name__ == "__main__":
    cli_entry()
