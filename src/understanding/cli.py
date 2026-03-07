#!/usr/bin/env python3
"""CLI for Understanding - Requirements understanding and cognitive load metrics."""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

_SUBCOMMANDS = {"version", "scan", "--help", "-h"}

app = typer.Typer(
    name="understanding",
    help="Requirements quality metrics — 31 measures based on readability formulas, IEEE/ISO standards, and RE research",
    add_completion=False,
)
console = Console()


# Quality Gates (Research-Backed Thresholds)
# Based on ISO 29148:2018, IEEE 830-1998, ISO 25010:2023
QUALITY_GATES = {
    "overall": 0.70,        # Minimum acceptable quality
    "structure": 0.70,      # ISO 29148 §5.2.5 - Atomicity & Completeness
    "testability": 0.70,    # ISO 29148 - Verifiability (mandatory)
    "semantic": 0.60,       # Lucassen 2017 - Actor-Action-Object
    "cognitive": 0.60,      # Sweller 1988 - Cognitive Load
    "readability": 0.50,    # Flesch 1948 - Understanding (lower for technical)
    # behavioral: No gate (context-dependent)
}


@app.command(hidden=True)
def scan(
    spec: Optional[Path] = typer.Argument(
        None,
        help="Path to spec.md file or directory (auto-discovers if not provided)",
    ),
    enhanced: bool = typer.Option(
        True,
        "--enhanced/--basic",
        help="Use all 31 metrics (enhanced) or base 18 metrics (basic)",
    ),
    validate: bool = typer.Option(
        False,
        "--validate",
        "-v",
        help="Enforce quality gates and exit with code 1 if failed",
    ),
    test: bool = typer.Option(
        False,
        "--test",
        "-t",
        help="Run in test mode: validate and show pass/fail status",
    ),
    per_requirement: bool = typer.Option(
        False,
        "--per-req",
        help="Analyze each requirement separately and show summary",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output JSON format (includes entity data)",
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Write output to file",
    ),
    csv: bool = typer.Option(
        False,
        "--csv",
        help="Export results as CSV (works with --output or prints to stdout)",
    ),
    diagram: Optional[str] = typer.Option(
        None,
        "--diagram",
        help="Generate diagram: 'text' for terminal, or path for export (format from extension: .png/.svg/.pdf)",
    ),
    ears: bool = typer.Option(
        False,
        "--ears",
        help="Analyze EARS (Easy Approach to Requirements Syntax) compliance and suggest improvements",
    ),
    energy: bool = typer.Option(
        False,
        "--energy",
        help="Compute token-level energy metrics using a local LM (requires: pip install understanding[energy])",
    ),
):
    """Scan requirements for quality metrics.

    Analyzes specifications using 31 metrics with NLP
    and entity extraction enabled by default. Use --basic for fast mode
    without NLP (18 metrics only).

    Examples:
        understanding                                        # Auto-discover and scan
        understanding spec.md                                # Scan specific spec
        understanding specs/                                 # Scan directory
        understanding spec.md --basic                        # Fast: 18 metrics, no NLP
        understanding spec.md --diagram text                 # Text diagram in terminal
        understanding spec.md --diagram diagram.png          # Export PNG diagram
        understanding spec.md --energy                       # Token-level ambiguity analysis
        understanding spec.md --validate                     # Quality gates (exit 1 if failed)
        understanding spec.md --json                         # JSON output (includes entities)
        understanding version                                # Show version
    """
    try:
        # Validate flag combinations
        if json_output and csv:
            console.print("[red]Error:[/red] Cannot use --json and --csv together")
            console.print("Choose one output format: --json OR --csv")
            raise typer.Exit(1)

        # NLP and entities are on by default (off in --basic mode)
        use_nlp = enhanced  # True unless --basic
        entities = enhanced  # entities on unless --basic

        # Parse --diagram flag
        show_diagram = False
        diagram_export_path = None
        diagram_export_format = "png"
        if diagram is not None:
            entities = True  # always need entities for diagrams
            if diagram.lower() == "text" or diagram == "":
                show_diagram = True
            else:
                # It's a file path
                diagram_export_path = Path(diagram)
                show_diagram = True  # also show text diagram
                ext = diagram_export_path.suffix.lstrip('.')
                if ext in ['svg', 'pdf', 'png']:
                    diagram_export_format = ext

        # Check energy dependencies early
        if energy:
            from .energy_metrics import is_energy_available
            if not is_energy_available():
                console.print("[red]Error:[/red] Energy metrics require transformers and torch")
                console.print("Install with: [bold]pip install understanding\\[energy][/bold]")
                raise typer.Exit(1)
            if not json_output:
                console.print("[dim]Loading energy model (first run downloads ~270MB)...[/dim]")

        # Make --test an alias for --validate (backward compatibility)
        if test:
            validate = True

        # Auto-discover spec if not provided
        if spec is None:
            spec = _find_spec()
            if spec is None:
                console.print("[red]Error:[/red] No spec.md file found")
                console.print("\nSearched in:")
                console.print("  • ./spec.md")
                console.print("  • ./specs/**/spec.md")
                console.print("\nPlease provide a path explicitly:")
                console.print("  understanding scan path/to/spec.md")
                raise typer.Exit(1)
            if not json_output:
                console.print(f"[dim]Found: {spec}[/dim]\n")
        elif not spec.exists():
            console.print(f"[red]Error:[/red] Path not found: {spec}")
            raise typer.Exit(1)

        # Check if path is directory or file
        if spec.is_dir():
            # Find all spec.md files in directory
            spec_files = list(spec.glob("**/spec.md"))
            if not spec_files:
                console.print(f"[red]Error:[/red] No spec.md files found in {spec}")
                raise typer.Exit(1)
        else:
            spec_files = [spec]

        results = []
        for spec_file in spec_files:
            if per_requirement or ears:
                # Parse and analyze per requirement
                spec_text = spec_file.read_text(encoding="utf-8")
                parsed = _parse_requirements(spec_text)

                if parsed["count"] == 0:
                    console.print(f"[yellow]Warning:[/yellow] No requirements found in {spec_file.name}")
                    console.print("Looking for patterns like: - **FR-001**: Requirement text")
                    # Fall back to full spec analysis
                    result = _analyze_spec(spec_file, enhanced=enhanced, use_nlp=use_nlp, extract_entities=entities, check_ears=ears, use_energy=energy)
                    results.append(result)
                else:
                    # Analyze each requirement
                    req_results = []
                    for req in parsed["requirements"]:
                        req_result = _analyze_text(req["text"], enhanced=enhanced, use_nlp=use_nlp, extract_entities=entities, check_ears=ears, use_energy=energy)
                        req_result["requirement_id"] = req["id"]
                        req_result["requirement_text"] = req["text"]
                        req_results.append(req_result)

                    # Analyze full spec for overall summary
                    overall_result = _analyze_spec(spec_file, enhanced=enhanced, use_nlp=use_nlp, extract_entities=entities, check_ears=ears, use_energy=energy)
                    overall_result["per_requirement"] = req_results
                    overall_result["requirement_count"] = parsed["count"]

                    # Add EARS summary if requested
                    if ears:
                        from .ears_patterns import EARSPatternDetector
                        detector = EARSPatternDetector()
                        req_texts = [req["text"] for req in parsed["requirements"]]
                        ears_score, ears_stats = detector.calculate_ears_score(req_texts)
                        overall_result["ears_analysis"] = {
                            "score": ears_score,
                            "stats": ears_stats
                        }

                    results.append(overall_result)
            else:
                result = _analyze_spec(spec_file, enhanced=enhanced, use_nlp=use_nlp, extract_entities=entities, check_ears=ears, use_energy=energy)
                results.append(result)

        # Output results
        if csv:
            # Export as CSV
            csv_output = _export_csv(results)
            if output_file:
                output_file.write_text(csv_output)
                console.print(f"[green]✓[/green] CSV written to {output_file}")
            else:
                print(csv_output)
        elif json_output:
            output = json.dumps(results, indent=2)
            if output_file:
                output_file.write_text(output)
                console.print(f"[green]✓[/green] Results written to {output_file}")
            else:
                print(output)
        else:
            # Show summary table for multiple specs unless --detailed is used
            if len(results) > 1:
                _print_batch_summary(results)

                # Show aggregated entity analysis for multiple specs
                if entities:
                    console.print("\n[dim]Aggregating entities across all specifications...[/dim]")
                    aggregated = _aggregate_entity_analysis(results)
                    _print_entity_analysis(aggregated, show_diagram=show_diagram, png_path=diagram_export_path, png_format=diagram_export_format)

                # Show energy summary for batch
                if energy:
                    energy_results = [r["energy"] for r in results if "energy" in r]
                    if energy_results:
                        avg_composite = sum(e["composite_score"] for e in energy_results) / len(energy_results)
                        console.print(f"\n[bold]Energy Analysis (batch average):[/bold] {avg_composite:.2%}")
            else:
                for result in results:
                    if per_requirement and "per_requirement" in result:
                        _print_per_requirement_result(result)
                    elif test:
                        _print_test_result(result)
                    else:
                        _print_result(result)

                    # Print entity analysis if requested
                    if entities:
                        _print_entity_analysis(result, show_diagram=show_diagram, png_path=diagram_export_path, png_format=diagram_export_format)

                    # Print EARS analysis if requested
                    if ears:
                        _print_ears_analysis(result)

                    # Print energy analysis if requested
                    if energy and "energy" in result:
                        _print_energy_analysis(result["energy"])

        # Validate against quality gates if requested
        if validate or test:
            any_failed = False
            for result in results:
                if not _check_quality_gates(result["metrics"]):
                    any_failed = True
                    break

            if any_failed:
                if not json_output and not csv:
                    console.print("\n[red]✗ Quality gates FAILED[/red]")
                raise typer.Exit(1)
            elif test and not json_output and not csv:
                console.print("\n[green]✓ Quality gates PASSED[/green]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def _check_quality_gates(metrics: dict) -> bool:
    """Check if all quality gates pass.

    Args:
        metrics: Metrics dictionary with overall_weighted_average and category_averages

    Returns:
        True if all gates pass, False otherwise
    """
    overall = metrics["overall_weighted_average"]
    categories = metrics["category_averages"]

    # Check all gates
    gates_pass = []
    gates_pass.append(overall >= QUALITY_GATES["overall"])
    gates_pass.append(categories.get("structure", 0) >= QUALITY_GATES["structure"])
    gates_pass.append(categories.get("testability", 0) >= QUALITY_GATES["testability"])
    gates_pass.append(categories.get("semantic", 0) >= QUALITY_GATES["semantic"])
    gates_pass.append(categories.get("cognitive", 0) >= QUALITY_GATES["cognitive"])
    gates_pass.append(categories.get("readability", 0) >= QUALITY_GATES["readability"])

    return all(gates_pass)


def _print_test_result(result: dict, per_requirement: bool = False):
    """Print validation result for a single spec."""
    spec_file = Path(result["spec_path"])

    # Handle per-requirement analysis if requested
    if per_requirement:
        spec_text = spec_file.read_text(encoding="utf-8")
        parsed = _parse_requirements(spec_text)

        if parsed["count"] == 0:
            console.print(f"[yellow]Warning:[/yellow] No requirements found in {spec_file.name}")
            console.print("Looking for patterns like: - **FR-001**: Requirement text")
            console.print("Falling back to full spec analysis\n")
        else:
            # Analyze each requirement
            req_results = []
            for req in parsed["requirements"]:
                req_result = _analyze_text(req["text"], enhanced=True, use_nlp=True, extract_entities=True)
                req_result["requirement_id"] = req["id"]
                req_result["requirement_text"] = req["text"]
                req_results.append(req_result)

            result["per_requirement"] = req_results
            result["requirement_count"] = parsed["count"]

            # Print per-requirement results
            _print_per_requirement_result(result)
            return

    # Regular validation output
    metrics = result["metrics"]
    overall = metrics["overall_weighted_average"]
    categories = metrics["category_averages"]
    semantic = categories.get("semantic", 0)
    testability = categories.get("testability", 0)

    # Display overall score with quality level
    if overall >= 0.90:
        level = "Excellent"
        level_color = "green bold"
    elif overall >= 0.80:
        level = "Very Good"
        level_color = "green"
    elif overall >= 0.70:
        level = "Good"
        level_color = "cyan"
    elif overall >= 0.60:
        level = "Fair"
        level_color = "yellow"
    else:
        level = "Poor"
        level_color = "red"

    console.print(
        Panel(
            f"[bold]{overall:.2%}[/bold] ({level})",
            title="Overall Score",
            border_style=level_color,
        )
    )

    # Display all 6 category scores
    console.print("\n[bold]Category Scores:[/bold]\n")

    cat_table = Table(show_header=False, box=None)
    cat_table.add_column("Category", style="cyan", width=20)
    cat_table.add_column("Score", justify="right", width=10)
    cat_table.add_column("Level", width=15)

    for cat_name in sorted(categories.keys()):
        score = categories[cat_name]
        if score >= 0.80:
            level_str = "[green]Very Good[/green]"
        elif score >= 0.70:
            level_str = "[cyan]Good[/cyan]"
        elif score >= 0.60:
            level_str = "[yellow]Fair[/yellow]"
        else:
            level_str = "[red]Needs Work[/red]"

        cat_table.add_row(
            cat_name.capitalize(),
            f"{score:.2%}",
            level_str,
        )

    console.print(cat_table)

    # Display quality gates
    console.print(f"\n[bold]Quality Gates (Research-Backed):[/bold]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Gate", style="dim", width=20)
    table.add_column("Required", justify="right", width=10)
    table.add_column("Actual", justify="right", width=10)
    table.add_column("Status", justify="center", width=8)
    table.add_column("Reference", style="dim", width=30)

    # Get all category scores
    structure = categories.get("structure", 0)
    testability = categories.get("testability", 0)
    cognitive = categories.get("cognitive", 0)
    readability = categories.get("readability", 0)

    # Overall gate
    overall_pass = overall >= QUALITY_GATES["overall"]
    table.add_row(
        "Overall",
        f"≥{QUALITY_GATES['overall']:.0%}",
        f"{overall:.2%}",
        "✓" if overall_pass else "✗",
        "Minimum quality baseline"
    )

    # Structure gate (TIER 1)
    structure_pass = structure >= QUALITY_GATES["structure"]
    table.add_row(
        "Structure",
        f"≥{QUALITY_GATES['structure']:.0%}",
        f"{structure:.2%}",
        "✓" if structure_pass else "✗",
        "ISO 29148 §5.2.5"
    )

    # Testability gate (TIER 1)
    testability_pass = testability >= QUALITY_GATES["testability"]
    table.add_row(
        "Testability",
        f"≥{QUALITY_GATES['testability']:.0%}",
        f"{testability:.2%}",
        "✓" if testability_pass else "✗",
        "ISO 29148 (mandatory)"
    )

    # Semantic gate (TIER 1)
    semantic_pass = semantic >= QUALITY_GATES["semantic"]
    table.add_row(
        "Semantic",
        f"≥{QUALITY_GATES['semantic']:.0%}",
        f"{semantic:.2%}",
        "✓" if semantic_pass else "✗",
        "Lucassen et al. 2017"
    )

    # Cognitive gate (TIER 2)
    cognitive_pass = cognitive >= QUALITY_GATES["cognitive"]
    table.add_row(
        "Cognitive",
        f"≥{QUALITY_GATES['cognitive']:.0%}",
        f"{cognitive:.2%}",
        "✓" if cognitive_pass else "✗",
        "Sweller 1988"
    )

    # Readability gate (TIER 2)
    readability_pass = readability >= QUALITY_GATES["readability"]
    table.add_row(
        "Readability",
        f"≥{QUALITY_GATES['readability']:.0%}",
        f"{readability:.2%}",
        "✓" if readability_pass else "✗",
        "Flesch 1948+"
    )

    console.print(table)

    # Overall result
    all_pass = _check_quality_gates(metrics)
    if all_pass:
        console.print("\n[green bold]✓ All quality gates passed[/green bold]\n")
    else:
        console.print("\n[red bold]✗ Quality gates failed[/red bold]\n")
        failures = []
        if not overall_pass:
            failures.append(f"Overall: {overall:.2%} < {QUALITY_GATES['overall']:.0%}")
        if not structure_pass:
            failures.append(f"Structure: {structure:.2%} < {QUALITY_GATES['structure']:.0%}")
        if not testability_pass:
            failures.append(f"Testability: {testability:.2%} < {QUALITY_GATES['testability']:.0%}")
        if not semantic_pass:
            failures.append(f"Semantic: {semantic:.2%} < {QUALITY_GATES['semantic']:.0%}")
        if not cognitive_pass:
            failures.append(f"Cognitive: {cognitive:.2%} < {QUALITY_GATES['cognitive']:.0%}")
        if not readability_pass:
            failures.append(f"Readability: {readability:.2%} < {QUALITY_GATES['readability']:.0%}")

        for failure in failures:
            console.print(f"  • {failure}")
        console.print()


@app.command()
def version():
    """Show version information."""
    from . import __version__

    console.print(f"understanding version {__version__}")
    console.print("31 requirements quality metrics based on readability formulas, IEEE/ISO standards, and RE research")


def _parse_requirements(spec_text: str) -> dict:
    """Parse individual requirements from spec text.

    Returns:
        dict with keys:
        - "requirements": list of dicts with "id" and "text"
        - "full_spec": original full text
    """
    import re

    requirements = []

    # Pattern to match requirements like:
    # - **FR-001**: Some requirement text
    # - **SC-001**: Some success criteria
    # - **NFR-001**: Non-functional requirement
    req_pattern = r"^- \*\*([A-Z]{1,5}-\d{3,4})\*\*:(.+)$"

    lines = spec_text.split("\n")
    for line in lines:
        match = re.match(req_pattern, line.strip())
        if match:
            req_id = match.group(1)
            req_text = match.group(2).strip()
            requirements.append({"id": req_id, "text": req_text})

    return {
        "requirements": requirements,
        "full_spec": spec_text,
        "count": len(requirements),
    }


def _find_spec() -> Optional[Path]:
    """Auto-discover spec.md file in common locations.

    Search order:
    1. ./spec.md (current directory)
    2. Most recent specs/NNN-*/spec.md (Spec Kit convention)
    3. Environment variable SPECIFY_FEATURE
    """
    import os

    cwd = Path.cwd()

    # 1. Current directory
    spec_file = cwd / "spec.md"
    if spec_file.exists():
        return spec_file

    # 2. Spec Kit specs/ directory - find most recent
    specs_dir = cwd / "specs"
    if specs_dir.exists() and specs_dir.is_dir():
        spec_files = sorted(specs_dir.glob("*/spec.md"), reverse=True)
        if spec_files:
            # Return most recently modified
            return max(spec_files, key=lambda p: p.stat().st_mtime)

    # 3. Environment variable
    env_feature = os.getenv("SPECIFY_FEATURE")
    if env_feature:
        env_spec = cwd / "specs" / env_feature / "spec.md"
        if env_spec.exists():
            return env_spec

    return None


def _analyze_text(text: str, enhanced: bool = True, use_nlp: bool = False, extract_entities: bool = False, check_ears: bool = False, use_energy: bool = False) -> dict:
    """Analyze text and return results."""
    if enhanced:
        from .enhanced_metrics import analyze_with_enhanced_metrics

        result = analyze_with_enhanced_metrics(text, use_spacy=use_nlp)
        metrics = result["enhanced_metrics"]
        metric_count = result.get("metric_count", {})
    else:
        from .normalized_metrics import analyze_with_normalized_metrics

        result = analyze_with_normalized_metrics(text)
        metrics = result["normalized_metrics"]
        metric_count = {"total": len(metrics["scores"])}

    result_dict = {
        "enhanced": enhanced,
        "metrics": metrics,
        "metric_count": metric_count,
    }

    # Energy metrics (optional)
    if use_energy:
        from .energy_metrics import analyze_energy
        energy_result = analyze_energy(text)
        result_dict["energy"] = energy_result.to_dict()

    # Check EARS compliance if requested
    if check_ears:
        from .ears_patterns import EARSPatternDetector
        detector = EARSPatternDetector()
        ears_result = detector.analyze(text)
        result_dict["ears"] = {
            "pattern": ears_result.pattern.value,
            "confidence": ears_result.confidence,
            "compliant": ears_result.compliant,
            "trigger": ears_result.trigger,
            "system": ears_result.system,
            "action": ears_result.action,
            "suggestion": ears_result.suggestion,
            "issues": ears_result.issues
        }

    # Extract entities if requested
    if extract_entities:
        try:
            from .semantic_metrics import SemanticAnalyzer
            import re

            # Split text into requirements (simple sentence splitting)
            sentences = re.split(r'[.!?]+', text)
            requirements = [s.strip() for s in sentences if len(s.strip()) > 10]

            analyzer = SemanticAnalyzer(use_spacy=use_nlp)
            entity_result = analyzer.extract_entities_detailed(requirements, use_nlp=use_nlp)

            # Convert Entity and Relationship objects to dicts for JSON serialization
            result_dict["entity_analysis"] = {
                "entities": [
                    {
                        "text": e.text,
                        "type": e.type.value,
                        "normalized": e.normalized,
                        "requirement_id": e.requirement_id,
                        "confidence": e.confidence,
                    }
                    for e in entity_result.entities
                ],
                "relationships": [
                    {
                        "source": {
                            "text": r.source.text,
                            "type": r.source.type.value,
                            "normalized": r.source.normalized,
                        },
                        "relation": r.relation,
                        "target": {
                            "text": r.target.text,
                            "type": r.target.type.value,
                            "normalized": r.target.normalized,
                        },
                        "requirement_id": r.requirement_id,
                    }
                    for r in entity_result.relationships
                ],
                "summary": {
                    "total_entities": len(entity_result.entities),
                    "unique_actors": len(entity_result.unique_actors),
                    "unique_actions": len(entity_result.unique_actions),
                    "unique_objects": len(entity_result.unique_objects),
                    "entity_counts": {k.value: v for k, v in entity_result.entity_counts.items()},
                },
            }
        except (ImportError, AttributeError):
            pass  # entity_metrics module not available, skip silently

    return result_dict


def _analyze_spec(spec_path: Path, enhanced: bool = True, use_nlp: bool = False, extract_entities: bool = False, check_ears: bool = False, use_energy: bool = False) -> dict:
    """Analyze a spec file and return results."""
    # Read spec
    spec_text = spec_path.read_text(encoding="utf-8")

    # Analyze
    result = _analyze_text(spec_text, enhanced=enhanced, use_nlp=use_nlp, extract_entities=extract_entities, check_ears=check_ears, use_energy=use_energy)
    result["spec_path"] = str(spec_path)
    result["spec_name"] = spec_path.stem

    return result


def _print_result(result: dict):
    """Print analysis result in human-readable format."""
    spec_name = result["spec_name"]
    metrics = result["metrics"]
    enhanced = result["enhanced"]
    metric_count = result.get("metric_count", {})

    overall = metrics["overall_weighted_average"]
    categories = metrics["category_averages"]

    # Quality level
    if overall >= 0.90:
        level = "Excellent"
        level_color = "green bold"
    elif overall >= 0.80:
        level = "Very Good"
        level_color = "green"
    elif overall >= 0.70:
        level = "Good"
        level_color = "cyan"
    elif overall >= 0.60:
        level = "Fair"
        level_color = "yellow"
    else:
        level = "Poor"
        level_color = "red"

    # Header
    console.print(f"\n[bold cyan]Requirements Quality Metrics - {spec_name}[/bold cyan]")
    total = metric_count.get('total', 31 if enhanced else 18)
    if not enhanced:
        console.print(f"[dim]Basic mode: {total} metrics (no NLP)[/dim]\n")
    else:
        console.print(f"[dim]{total} metrics[/dim]\n")

    # Overall score
    console.print(
        Panel(
            f"[bold]{overall:.2%}[/bold] ({level})",
            title="Overall Score",
            border_style=level_color,
        )
    )

    # Category scores
    console.print("\n[bold]Category Scores:[/bold]\n")

    table = Table(show_header=False, box=None)
    table.add_column("Category", style="cyan", width=20)
    table.add_column("Score", justify="right", width=10)
    table.add_column("Level", width=15)

    for cat_name in sorted(categories.keys()):
        score = categories[cat_name]
        if score >= 0.80:
            level_str = "[green]Very Good[/green]"
        elif score >= 0.70:
            level_str = "[cyan]Good[/cyan]"
        elif score >= 0.60:
            level_str = "[yellow]Fair[/yellow]"
        else:
            level_str = "[red]Needs Work[/red]"

        table.add_row(
            cat_name.capitalize(),
            f"{score:.2%}",
            level_str,
        )

    console.print(table)

    # Quality gates status (if enhanced)
    if enhanced:
        structure = categories.get("structure", 0)
        testability = categories.get("testability", 0)
        semantic = categories.get("semantic", 0)
        cognitive = categories.get("cognitive", 0)
        readability = categories.get("readability", 0)

        gates_pass = _check_quality_gates(metrics)

        console.print(f"\n[bold]Quality Gates (6 gates):[/bold]")
        console.print(f"  Overall ≥{QUALITY_GATES['overall']:.0%}:      {overall:.2%} {'✓' if overall >= QUALITY_GATES['overall'] else '✗'}")
        console.print(f"  Structure ≥{QUALITY_GATES['structure']:.0%}:    {structure:.2%} {'✓' if structure >= QUALITY_GATES['structure'] else '✗'}")
        console.print(f"  Testability ≥{QUALITY_GATES['testability']:.0%}:  {testability:.2%} {'✓' if testability >= QUALITY_GATES['testability'] else '✗'}")
        console.print(f"  Semantic ≥{QUALITY_GATES['semantic']:.0%}:     {semantic:.2%} {'✓' if semantic >= QUALITY_GATES['semantic'] else '✗'}")
        console.print(f"  Cognitive ≥{QUALITY_GATES['cognitive']:.0%}:    {cognitive:.2%} {'✓' if cognitive >= QUALITY_GATES['cognitive'] else '✗'}")
        console.print(f"  Readability ≥{QUALITY_GATES['readability']:.0%}:  {readability:.2%} {'✓' if readability >= QUALITY_GATES['readability'] else '✗'}")

        if gates_pass:
            console.print("\n[green bold]✓ Status: ALL GATES PASSED[/green bold]\n")
        else:
            console.print("\n[red bold]✗ Status: SOME GATES FAILED[/red bold]\n")
    else:
        console.print()


def _aggregate_entity_analysis(results: list) -> dict:
    """
    Aggregate entity analysis from multiple specs into unified result.

    Args:
        results: List of analysis results from multiple specs

    Returns:
        Aggregated result dict with combined entity_analysis
    """
    # Collect all entities and relationships
    all_entities = []
    all_relationships = []
    spec_sources = {}  # Track which entities come from which specs

    for result in results:
        if "entity_analysis" not in result:
            continue

        entity_data = result["entity_analysis"]
        spec_name = Path(result["spec_path"]).parent.name

        # Add entities with spec source annotation
        for entity in entity_data["entities"]:
            entity_copy = entity.copy()
            entity_copy["spec_source"] = spec_name
            all_entities.append(entity_copy)

            # Track unique entity by normalized form
            normalized = entity["normalized"]
            if normalized not in spec_sources:
                spec_sources[normalized] = set()
            spec_sources[normalized].add(spec_name)

        # Add relationships
        for rel in entity_data["relationships"]:
            rel_copy = rel.copy()
            rel_copy["spec_source"] = spec_name
            all_relationships.append(rel_copy)

    # Deduplicate entities by normalized form (keep highest confidence)
    entities_by_norm = {}
    for entity in all_entities:
        norm = entity["normalized"]
        if norm not in entities_by_norm:
            entities_by_norm[norm] = entity
        elif entity["confidence"] > entities_by_norm[norm]["confidence"]:
            entities_by_norm[norm] = entity

    unique_entities = list(entities_by_norm.values())

    # Deduplicate relationships by (source, relation, target) tuple
    relationships_by_tuple = {}
    for rel in all_relationships:
        key = (rel["source"]["normalized"], rel["relation"], rel["target"]["normalized"])
        if key not in relationships_by_tuple:
            relationships_by_tuple[key] = rel

    unique_relationships = list(relationships_by_tuple.values())

    # Calculate aggregated summary
    actors = [e for e in unique_entities if e["type"] == "actor"]
    actions = [e for e in unique_entities if e["type"] == "action"]
    objects = [e for e in unique_entities if e["type"] == "object"]

    # Count entities by type
    entity_counts = {}
    for entity in unique_entities:
        etype = entity["type"]
        entity_counts[etype] = entity_counts.get(etype, 0) + 1

    # Create aggregated result
    aggregated = {
        "entity_analysis": {
            "entities": unique_entities,
            "relationships": unique_relationships,
            "summary": {
                "total_entities": len(unique_entities),
                "unique_actors": len(set(e["normalized"] for e in actors)),
                "unique_actions": len(set(e["normalized"] for e in actions)),
                "unique_objects": len(set(e["normalized"] for e in objects)),
                "entity_counts": entity_counts,
                "spec_count": len(results),
                "cross_spec": True,
            },
            "spec_sources": {k: list(v) for k, v in spec_sources.items()},
        },
        "spec_path": "aggregate",
        "spec_name": f"Cross-Spec Analysis ({len(results)} specs)",
    }

    return aggregated


def _print_energy_analysis(energy: dict):
    """Display energy metrics analysis."""
    console.print()
    console.print(Panel("[bold]Energy Analysis[/bold] (token-level perplexity)", style="blue"))

    # Score table
    table = Table(show_header=True, header_style="bold")
    table.add_column("Metric", style="cyan", min_width=25)
    table.add_column("Score", justify="right", min_width=8)
    table.add_column("Raw Value", justify="right", min_width=12)
    table.add_column("Interpretation", min_width=30)

    def _interp(score: float) -> str:
        if score >= 0.80:
            return "[green]Good - clear requirement[/green]"
        elif score >= 0.60:
            return "[yellow]Fair - some ambiguity[/yellow]"
        else:
            return "[red]Poor - high ambiguity[/red]"

    table.add_row(
        "Mean Energy",
        f"{energy['mean_energy_score']:.2%}",
        f"{energy['raw']['mean_energy']:.2f}",
        _interp(energy["mean_energy_score"]),
    )
    table.add_row(
        "Max Energy (hotspot)",
        f"{energy['max_energy_score']:.2%}",
        f"{energy['raw']['max_energy']:.2f}",
        _interp(energy["max_energy_score"]),
    )
    table.add_row(
        "Dispersion",
        f"{energy['dispersion_score']:.2%}",
        f"{energy['raw']['variance']:.2f}",
        _interp(energy["dispersion_score"]),
    )
    table.add_row(
        "Anchor Ratio (easy tokens)",
        f"{energy['anchor_score']:.2%}",
        f"{energy['raw']['anchor_ratio']:.0%}",
        _interp(energy["anchor_score"]),
    )
    table.add_row(
        "Tail Ratio (hard tokens)",
        f"{energy['tail_score']:.2%}",
        f"{energy['raw']['tail_ratio']:.0%}",
        _interp(energy["tail_score"]),
    )

    console.print(table)

    # Composite
    composite = energy["composite_score"]
    if composite >= 0.80:
        color = "green"
    elif composite >= 0.60:
        color = "yellow"
    else:
        color = "red"
    console.print(f"\n  Energy Composite Score: [{color} bold]{composite:.2%}[/{color} bold]")

    # Hotspot tokens
    if energy.get("hotspot_tokens"):
        console.print("\n  [bold]Highest-energy tokens[/bold] (potential ambiguity hotspots):")
        for ht in energy["hotspot_tokens"][:5]:
            token = ht["token"]
            e = ht["energy"]
            bar_len = min(30, int(e * 2))
            bar = "#" * bar_len
            console.print(f"    [yellow]{token:>20}[/yellow]  {e:6.2f}  [dim]{bar}[/dim]")


def _print_ears_analysis(result: dict):
    """Display EARS pattern analysis for requirements."""
    if "ears_analysis" not in result and "per_requirement" not in result:
        return

    console.print("\n[bold cyan]EARS Compliance Analysis[/bold cyan]")
    console.print("=" * 60)

    # Show overall stats if available
    if "ears_analysis" in result:
        stats = result["ears_analysis"]["stats"]
        score = result["ears_analysis"]["score"]

        # Summary table
        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("Metric", style="dim")
        table.add_column("Value", justify="right")

        table.add_row("Overall EARS Score", f"{score:.1%}")
        table.add_row("Total Requirements", str(stats["total_requirements"]))
        table.add_row("Compliant", f"{stats['compliant_count']} ({stats['compliance_rate']:.1%})")
        table.add_row("Non-Compliant", str(stats["non_compliant_count"]))
        table.add_row("Avg Confidence", f"{stats['avg_confidence']:.1%}")

        console.print(table)

        # Pattern distribution
        console.print("\n[bold]Pattern Distribution:[/bold]")
        pattern_table = Table(show_header=False, box=None)
        pattern_table.add_column("Pattern", style="cyan")
        pattern_table.add_column("Count", justify="right")

        pattern_names = {
            'ubiquitous': 'Ubiquitous (The system shall...)',
            'event-driven': 'Event-Driven (WHEN...)',
            'state-driven': 'State-Driven (WHILE...)',
            'unwanted-behavior': 'Unwanted Behavior (IF-THEN...)',
            'optional-feature': 'Optional Feature (WHERE...)',
            'none': 'Non-EARS'
        }

        for pattern_key, count in sorted(stats["pattern_counts"].items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                pattern_name = pattern_names.get(pattern_key, pattern_key)
                pattern_table.add_row(pattern_name, str(count))

        console.print(pattern_table)

    # Show per-requirement details
    if "per_requirement" in result:
        console.print("\n[bold]Per-Requirement EARS Analysis:[/bold]")

        for req_result in result["per_requirement"]:
            if "ears" not in req_result:
                continue

            req_id = req_result["requirement_id"]
            ears_data = req_result["ears"]

            # Status icon
            if ears_data["compliant"]:
                status = "[green]✓[/green]"
            else:
                status = "[red]✗[/red]"

            # Pattern badge
            pattern_name = ears_data["pattern"].replace("-", " ").title()
            confidence = ears_data["confidence"]

            console.print(f"\n{status} [bold]{req_id}[/bold]: {pattern_name} ({confidence:.0%})")

            # Show requirement text (truncated)
            req_text = req_result.get("requirement_text", "")
            if len(req_text) > 80:
                req_text = req_text[:77] + "..."
            console.print(f"  [dim]{req_text}[/dim]")

            # Show issues
            if ears_data["issues"]:
                console.print(f"  [yellow]Issues:[/yellow] {', '.join(ears_data['issues'])}")

            # Show suggestion if non-compliant
            if ears_data["suggestion"]:
                console.print(f"  [blue]💡 Suggestion:[/blue] {ears_data['suggestion']}")

    console.print()


def _print_entity_analysis(result: dict, show_diagram: bool = False, png_path: Optional[Path] = None, png_format: str = "png"):
    """Display extracted entities and relationships."""
    if "entity_analysis" not in result:
        return

    entity_data = result["entity_analysis"]
    summary = entity_data["summary"]
    is_cross_spec = summary.get("cross_spec", False)

    # Summary table
    if is_cross_spec:
        console.print("\n[bold cyan]Cross-Spec Entity Analysis[/bold cyan]")
        console.print(f"[dim]Unified view across {summary.get('spec_count', 0)} specifications[/dim]")
    else:
        console.print("\n[bold cyan]Entity Analysis[/bold cyan]")
    console.print("=" * 60)

    table = Table(show_header=True, header_style="bold magenta", box=None)
    table.add_column("Metric", style="dim")
    table.add_column("Count", justify="right")

    if is_cross_spec:
        table.add_row("Specifications Analyzed", str(summary.get("spec_count", 0)))
    table.add_row("Total Entities", str(summary["total_entities"]))
    table.add_row("Unique Actors", str(summary["unique_actors"]))
    table.add_row("Unique Actions", str(summary["unique_actions"]))
    table.add_row("Unique Objects", str(summary["unique_objects"]))

    console.print(table)

    # Entity counts by type
    if "entity_counts" in summary and summary["entity_counts"]:
        console.print("\n[bold]Entity Types:[/bold]")
        type_table = Table(show_header=False, box=None)
        type_table.add_column("Type", style="cyan")
        type_table.add_column("Count", justify="right")

        for entity_type, count in sorted(summary["entity_counts"].items()):
            type_table.add_row(entity_type.capitalize(), str(count))

        console.print(type_table)

    # Top entities by type
    entities = entity_data["entities"]
    actors = [e for e in entities if e["type"] == "actor"]
    actions = [e for e in entities if e["type"] == "action"]
    objects = [e for e in entities if e["type"] == "object"]

    if actors:
        console.print("\n[bold]Top Actors:[/bold]")
        unique_actors = sorted(set(e["normalized"] for e in actors))
        for actor in unique_actors[:10]:
            console.print(f"  • {actor}")
        if len(unique_actors) > 10:
            console.print(f"  ... and {len(unique_actors) - 10} more")

    if actions:
        console.print("\n[bold]Top Actions:[/bold]")
        unique_actions = sorted(set(e["normalized"] for e in actions))
        for action in unique_actions[:10]:
            console.print(f"  • {action}")
        if len(unique_actions) > 10:
            console.print(f"  ... and {len(unique_actions) - 10} more")

    if objects:
        console.print("\n[bold]Top Objects:[/bold]")
        unique_objects = sorted(set(e["normalized"] for e in objects))
        for obj in unique_objects[:10]:
            console.print(f"  • {obj}")
        if len(unique_objects) > 10:
            console.print(f"  ... and {len(unique_objects) - 10} more")

    # Relationships
    relationships = entity_data["relationships"]
    if relationships:
        # Group relationships by type
        rel_by_type = {}
        for rel in relationships:
            rel_type = rel["relation"]
            if rel_type not in rel_by_type:
                rel_by_type[rel_type] = []
            rel_by_type[rel_type].append(rel)

        # Display each relationship type
        for rel_type, rels in sorted(rel_by_type.items()):
            console.print(f"\n[bold]{rel_type.capitalize()} Relationships:[/bold]")
            for rel in rels[:15]:  # Top 15 per type
                console.print(
                    f"  • [cyan]{rel['source']['normalized']}[/cyan] "
                    f"→ [green]{rel['target']['normalized']}[/green]"
                )
            if len(rels) > 15:
                console.print(f"  ... and {len(rels) - 15} more")

    # Generate and display diagram if requested
    if show_diagram and relationships:
        from .entity_metrics import EntityExtractor, Entity, Relationship, EntityType

        # Reconstruct Entity and Relationship objects from dicts
        entity_objs = [
            Entity(
                text=e["text"],
                type=EntityType(e["type"]),
                normalized=e["normalized"],
                requirement_id=e["requirement_id"],
                confidence=e["confidence"],
            )
            for e in entities
        ]

        relationship_objs = [
            Relationship(
                source=Entity(
                    text=r["source"]["text"],
                    type=EntityType(r["source"]["type"]),
                    normalized=r["source"]["normalized"],
                    requirement_id=r.get("requirement_id", ""),
                    confidence=1.0,
                ),
                relation=r["relation"],
                target=Entity(
                    text=r["target"]["text"],
                    type=EntityType(r["target"]["type"]),
                    normalized=r["target"]["normalized"],
                    requirement_id=r.get("requirement_id", ""),
                    confidence=1.0,
                ),
                requirement_id=r.get("requirement_id", ""),
            )
            for r in relationships
        ]

        extractor = EntityExtractor()
        diagram_text = extractor.generate_text_diagram(entity_objs, relationship_objs)

        console.print("\n[bold cyan]Entity Relationship Diagram[/bold cyan]")
        console.print("=" * 60)
        console.print(diagram_text)

    # Export PNG diagram if requested
    if png_path and relationships:
        from .entity_metrics import EntityExtractor, Entity, Relationship, EntityType, GRAPHVIZ_AVAILABLE

        if not GRAPHVIZ_AVAILABLE:
            console.print("\n[yellow]⚠ Warning:[/yellow] PNG export requires graphviz")
            console.print("Install with: pip install understanding[diagram]")
            console.print("System requirement: brew install graphviz (macOS) or apt-get install graphviz (Linux)")
        else:
            # Reconstruct Entity and Relationship objects if not already done
            if 'entity_objs' not in locals():
                entity_objs = [
                    Entity(
                        text=e["text"],
                        type=EntityType(e["type"]),
                        normalized=e["normalized"],
                        requirement_id=e["requirement_id"],
                        confidence=e["confidence"],
                    )
                    for e in entities
                ]

                relationship_objs = [
                    Relationship(
                        source=Entity(
                            text=r["source"]["text"],
                            type=EntityType(r["source"]["type"]),
                            normalized=r["source"]["normalized"],
                            requirement_id=r.get("requirement_id", ""),
                            confidence=1.0,
                        ),
                        relation=r["relation"],
                        target=Entity(
                            text=r["target"]["text"],
                            type=EntityType(r["target"]["type"]),
                            normalized=r["target"]["normalized"],
                            requirement_id=r.get("requirement_id", ""),
                            confidence=1.0,
                        ),
                        requirement_id=r.get("requirement_id", ""),
                    )
                    for r in relationships
                ]

            extractor = EntityExtractor()

            # Get title from spec name if available
            is_cross_spec = entity_data.get("summary", {}).get("cross_spec", False)
            if is_cross_spec:
                spec_count = entity_data.get("summary", {}).get("spec_count", 0)
                title = f"Cross-Spec Entity Relationships ({spec_count} specs)"
            else:
                title = result.get("spec_name", "Entity Relationship Diagram")
                title = f"Entity Relationships: {title}"

            # Export PNG
            # Remove extension if provided
            output_base = str(png_path).rsplit('.', 1)[0]

            success = extractor.export_png_diagram(
                entity_objs,
                relationship_objs,
                output_base,
                title=title,
                format=png_format
            )

            if success:
                output_file = f"{output_base}.{png_format}"
                console.print(f"\n[green]✓[/green] Diagram exported to: {output_file}")
            else:
                console.print(f"\n[red]✗[/red] Failed to export diagram")

    console.print()


def _export_csv(results: list) -> str:
    """Export results as CSV with all categories."""
    from pathlib import Path
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Spec",
        "Overall",
        "Behavioral",
        "Cognitive",
        "Readability",
        "Semantic",
        "Structure",
        "Testability",
        "Overall_Pass",
        "Semantic_Pass",
        "Testability_Pass",
        "All_Gates_Pass",
    ])

    # Data rows
    for result in results:
        spec_path = Path(result["spec_path"])
        spec_name = spec_path.parent.name

        metrics = result["metrics"]
        overall = metrics["overall_weighted_average"]
        categories = metrics["category_averages"]

        behavioral = categories.get("behavioral", 0)
        cognitive = categories.get("cognitive", 0)
        readability = categories.get("readability", 0)
        semantic = categories.get("semantic", 0)
        structure = categories.get("structure", 0)
        testability = categories.get("testability", 0)

        overall_pass = overall >= 0.70
        semantic_pass = semantic >= 0.60
        testability_pass = testability >= 0.60
        all_pass = overall_pass and semantic_pass and testability_pass

        writer.writerow([
            spec_name,
            f"{overall:.4f}",
            f"{behavioral:.4f}",
            f"{cognitive:.4f}",
            f"{readability:.4f}",
            f"{semantic:.4f}",
            f"{structure:.4f}",
            f"{testability:.4f}",
            "PASS" if overall_pass else "FAIL",
            "PASS" if semantic_pass else "FAIL",
            "PASS" if testability_pass else "FAIL",
            "PASS" if all_pass else "FAIL",
        ])

    return output.getvalue()


def _print_batch_summary(results: list):
    """Print summary table for batch analysis of multiple specs."""
    from pathlib import Path

    console.print(f"\n[bold cyan]Batch Quality Analysis Summary[/bold cyan]")
    console.print(f"[dim]Analyzed {len(results)} specifications[/dim]\n")

    # Calculate statistics
    passed = []
    failed = []

    for result in results:
        metrics = result["metrics"]
        overall = metrics["overall_weighted_average"]
        categories = metrics["category_averages"]
        semantic = categories.get("semantic", 0)
        testability = categories.get("testability", 0)

        passes = overall >= 0.70 and semantic >= 0.60 and testability >= 0.60

        if passes:
            passed.append(result)
        else:
            failed.append(result)

    # Overall statistics
    pass_rate = len(passed) / len(results) if results else 0
    console.print(
        Panel(
            f"[bold]{len(passed)}/{len(results)}[/bold] passed ([green]{pass_rate:.1%}[/green])\n"
            f"[bold]{len(failed)}/{len(results)}[/bold] failed ([red]{1-pass_rate:.1%}[/red])",
            title="Quality Gates Status",
            border_style="cyan",
        )
    )

    # Category averages across all specs
    console.print("\n[bold]Average Scores Across All Specs:[/bold]\n")

    # Calculate averages
    avg_overall = sum(r["metrics"]["overall_weighted_average"] for r in results) / len(results)

    categories = {}
    for result in results:
        for cat_name, score in result["metrics"]["category_averages"].items():
            if cat_name not in categories:
                categories[cat_name] = []
            categories[cat_name].append(score)

    avg_categories = {cat: sum(scores) / len(scores) for cat, scores in categories.items()}

    cat_table = Table(show_header=False, box=None)
    cat_table.add_column("Category", style="cyan", width=20)
    cat_table.add_column("Average", justify="right", width=10)
    cat_table.add_column("Level", width=15)

    cat_table.add_row(
        "[bold]Overall[/bold]",
        f"[bold]{avg_overall:.2%}[/bold]",
        _get_level_string(avg_overall, bold=True),
    )

    for cat_name in sorted(avg_categories.keys()):
        score = avg_categories[cat_name]
        cat_table.add_row(
            cat_name.capitalize(),
            f"{score:.2%}",
            _get_level_string(score),
        )

    console.print(cat_table)

    # Failed specs table (show top 20 worst)
    if failed:
        console.print(f"\n[bold]Failed Specifications ({len(failed)}):[/bold]")

        if len(failed) > 20:
            console.print(f"[dim]Showing worst 20 of {len(failed)} failed specs[/dim]\n")
            # Sort by overall score (worst first)
            failed_sorted = sorted(failed, key=lambda r: r["metrics"]["overall_weighted_average"])[:20]
        else:
            console.print()
            failed_sorted = sorted(failed, key=lambda r: r["metrics"]["overall_weighted_average"])

        fail_table = Table(show_header=True, header_style="bold red")
        fail_table.add_column("Spec", style="dim", width=22)
        fail_table.add_column("Overall", justify="right", width=8)
        fail_table.add_column("Behav", justify="right", width=8)
        fail_table.add_column("Cognit", justify="right", width=8)
        fail_table.add_column("Read", justify="right", width=8)
        fail_table.add_column("Semant", justify="right", width=8)
        fail_table.add_column("Struct", justify="right", width=8)
        fail_table.add_column("Testab", justify="right", width=8)
        fail_table.add_column("Issues", width=18)

        for result in failed_sorted:
            spec_path = Path(result["spec_path"])
            spec_name = spec_path.parent.name  # Get directory name like "001-feature-name"

            metrics = result["metrics"]
            overall = metrics["overall_weighted_average"]
            categories = metrics["category_averages"]

            # Get all 6 category scores
            behavioral = categories.get("behavioral", 0)
            cognitive = categories.get("cognitive", 0)
            readability = categories.get("readability", 0)
            semantic = categories.get("semantic", 0)
            structure = categories.get("structure", 0)
            testability = categories.get("testability", 0)

            # Identify issues (gates only check overall, semantic, testability)
            issues = []
            if overall < 0.70:
                issues.append("Ovr")
            if semantic < 0.60:
                issues.append("Sem")
            if testability < 0.60:
                issues.append("Tst")

            fail_table.add_row(
                spec_name[:25],  # Truncate long names
                f"{overall:.0%}",
                f"{behavioral:.0%}",
                f"{cognitive:.0%}",
                f"{readability:.0%}",
                f"{semantic:.0%}",
                f"{structure:.0%}",
                f"{testability:.0%}",
                ", ".join(issues) if issues else "✓",
            )

        console.print(fail_table)

    # Passed specs summary
    if passed:
        console.print(f"\n[green bold]✓ {len(passed)} specifications passed quality gates[/green bold]")

    console.print()


def _get_level_string(score: float, bold: bool = False) -> str:
    """Get colored level string for a score."""
    if score >= 0.80:
        level = "Very Good"
        color = "green"
    elif score >= 0.70:
        level = "Good"
        color = "cyan"
    elif score >= 0.60:
        level = "Fair"
        color = "yellow"
    else:
        level = "Needs Work"
        color = "red"

    if bold:
        return f"[{color} bold]{level}[/{color} bold]"
    else:
        return f"[{color}]{level}[/{color}]"


def _print_per_requirement_result(result: dict):
    """Print per-requirement analysis results."""
    spec_name = result["spec_name"]
    req_results = result["per_requirement"]
    overall_metrics = result["metrics"]
    requirement_count = result["requirement_count"]

    console.print(f"\n[bold cyan]Per-Requirement Quality Analysis - {spec_name}[/bold cyan]")
    console.print(f"[dim]Found {requirement_count} requirements[/dim]\n")

    # Table for per-requirement scores
    req_table = Table(show_header=True, header_style="bold cyan")
    req_table.add_column("Requirement", style="cyan", width=15)
    req_table.add_column("Overall", justify="right", width=10)
    req_table.add_column("Semantic", justify="right", width=10)
    req_table.add_column("Testability", justify="right", width=12)
    req_table.add_column("Status", justify="center", width=10)

    failed_reqs = []
    for req_result in req_results:
        req_id = req_result["requirement_id"]
        metrics = req_result["metrics"]
        overall = metrics["overall_weighted_average"]
        categories = metrics["category_averages"]
        semantic = categories.get("semantic", 0)
        testability = categories.get("testability", 0)

        # Check if requirement passes gates
        passes = overall >= 0.70 and semantic >= 0.60 and testability >= 0.60
        status = "[green]✓[/green]" if passes else "[red]✗[/red]"

        if not passes:
            failed_reqs.append({
                "id": req_id,
                "overall": overall,
                "semantic": semantic,
                "testability": testability,
            })

        req_table.add_row(
            req_id,
            f"{overall:.1%}",
            f"{semantic:.1%}",
            f"{testability:.1%}",
            status,
        )

    console.print(req_table)

    # Overall summary
    console.print(f"\n[bold]Overall Spec Summary:[/bold]\n")

    overall = overall_metrics["overall_weighted_average"]
    categories = overall_metrics["category_averages"]

    # Quality level
    if overall >= 0.90:
        level = "Excellent"
        level_color = "green bold"
    elif overall >= 0.80:
        level = "Very Good"
        level_color = "green"
    elif overall >= 0.70:
        level = "Good"
        level_color = "cyan"
    elif overall >= 0.60:
        level = "Fair"
        level_color = "yellow"
    else:
        level = "Poor"
        level_color = "red"

    console.print(
        Panel(
            f"[bold]{overall:.2%}[/bold] ({level})",
            title="Overall Score (Full Spec)",
            border_style=level_color,
        )
    )

    # Category breakdown
    console.print("\n[bold]Category Scores:[/bold]\n")

    cat_table = Table(show_header=False, box=None)
    cat_table.add_column("Category", style="cyan", width=20)
    cat_table.add_column("Score", justify="right", width=10)
    cat_table.add_column("Level", width=15)

    for cat_name in sorted(categories.keys()):
        score = categories[cat_name]
        if score >= 0.80:
            level_str = "[green]Very Good[/green]"
        elif score >= 0.70:
            level_str = "[cyan]Good[/cyan]"
        elif score >= 0.60:
            level_str = "[yellow]Fair[/yellow]"
        else:
            level_str = "[red]Needs Work[/red]"

        cat_table.add_row(
            cat_name.capitalize(),
            f"{score:.2%}",
            level_str,
        )

    console.print(cat_table)

    # Quality gates
    semantic = categories.get("semantic", 0)
    testability = categories.get("testability", 0)
    overall_pass = overall >= 0.70
    semantic_pass = semantic >= 0.60
    testability_pass = testability >= 0.60
    gates_pass = overall_pass and semantic_pass and testability_pass

    console.print(f"\n[bold]Quality Gates:[/bold]")
    console.print(f"  Overall ≥0.70:      {overall:.2%} {'✓' if overall_pass else '✗'}")
    console.print(f"  Semantic ≥0.60:     {semantic:.2%} {'✓' if semantic_pass else '✗'}")
    console.print(f"  Testability ≥0.60:  {testability:.2%} {'✓' if testability_pass else '✗'}")

    if gates_pass:
        console.print("\n[green bold]✓ Status: PASSED[/green bold]")
    else:
        console.print("\n[red bold]✗ Status: FAILED[/red bold]")

    # Show failed requirements
    if failed_reqs:
        console.print(f"\n[bold]Failed Requirements ({len(failed_reqs)}):[/bold]")
        for req in failed_reqs:
            reasons = []
            if req["overall"] < 0.70:
                reasons.append(f"Overall {req['overall']:.1%} < 0.70")
            if req["semantic"] < 0.60:
                reasons.append(f"Semantic {req['semantic']:.1%} < 0.60")
            if req["testability"] < 0.60:
                reasons.append(f"Testability {req['testability']:.1%} < 0.60")
            console.print(f"  • {req['id']}: {', '.join(reasons)}")

    console.print()


def main():
    """Main entry point. Auto-injects 'scan' if no subcommand given."""
    args = sys.argv[1:]
    # If first arg is not a known subcommand, inject 'scan'
    if not args or args[0] not in _SUBCOMMANDS:
        sys.argv.insert(1, "scan")
    app()


if __name__ == "__main__":
    main()
