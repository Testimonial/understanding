"""Tests for CLI commands."""

import json
import pytest
from pathlib import Path
from typer.testing import CliRunner
from understanding.cli import app


runner = CliRunner()


class TestVersionCommand:
    """Test suite for version command."""

    def test_version_command(self):
        """Test version command output."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "understanding version" in result.stdout or "version" in result.stdout
        assert "3.4.0" in result.stdout


class TestScanCommand:
    """Test suite for scan command."""

    def test_scan_with_file(self, temp_spec_file):
        """Test scan command with specific file."""
        result = runner.invoke(app, ["scan", str(temp_spec_file)])

        assert result.exit_code == 0
        assert "Requirements Quality Metrics" in result.stdout
        assert "Overall Score" in result.stdout
        assert "Category Scores" in result.stdout

    def test_scan_with_json_output(self, temp_spec_file):
        """Test scan command with JSON output."""
        result = runner.invoke(app, ["scan", str(temp_spec_file), "--json"])

        assert result.exit_code == 0

        # Parse JSON output
        output = json.loads(result.stdout)
        assert isinstance(output, list)
        assert len(output) > 0

        # Check first result structure
        first_result = output[0]
        assert "spec_path" in first_result
        assert "metrics" in first_result
        assert "enhanced" in first_result

        metrics = first_result["metrics"]
        assert "overall_weighted_average" in metrics
        assert "category_averages" in metrics

    def test_scan_with_basic_mode(self, temp_spec_file):
        """Test scan command with basic (18 metrics) mode."""
        result = runner.invoke(app, ["scan", str(temp_spec_file), "--basic"])

        assert result.exit_code == 0
        assert "Basic" in result.stdout or "18" in result.stdout

    def test_scan_directory(self, temp_specs_dir):
        """Test scan command with directory containing multiple specs."""
        result = runner.invoke(app, ["scan", str(temp_specs_dir)])

        assert result.exit_code == 0

    def test_scan_nonexistent_file(self):
        """Test scan command with nonexistent file."""
        result = runner.invoke(app, ["scan", "/nonexistent/path/spec.md"])

        assert result.exit_code == 1
        assert "Error" in result.stdout or "not found" in result.stdout.lower()

    def test_scan_with_csv_output(self, temp_spec_file, tmp_path):
        """Test scan command with CSV output."""
        output_file = tmp_path / "output.csv"
        result = runner.invoke(app, [
            "scan",
            str(temp_spec_file),
            "--csv",
            "--output",
            str(output_file)
        ])

        assert result.exit_code == 0
        assert output_file.exists()

    def test_scan_with_validate(self, temp_spec_file):
        """Test scan command with --validate flag."""
        result = runner.invoke(app, ["scan", str(temp_spec_file), "--validate"])

        # Exit code depends on quality gates
        assert result.exit_code in [0, 1]

    def test_scan_with_test_flag(self, temp_spec_file):
        """Test scan command with --test flag (alias for --validate)."""
        result = runner.invoke(app, ["scan", str(temp_spec_file), "--test"])

        # Exit code depends on quality gates
        assert result.exit_code in [0, 1]
        assert "Overall Score" in result.stdout


class TestAutoDiscovery:
    """Test auto-discovery functionality."""

    def test_scan_auto_discovery_no_spec(self, tmp_path, monkeypatch):
        """Test scan auto-discovery when no spec exists."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["scan"])

        assert result.exit_code == 1
        assert "No spec.md file found" in result.stdout


class TestOutputFormats:
    """Test different output formats."""

    def test_human_readable_output(self, temp_spec_file):
        """Test human-readable output format."""
        result = runner.invoke(app, ["scan", str(temp_spec_file)])

        assert result.exit_code == 0
        assert "Category Scores" in result.stdout

    def test_json_output_structure(self, temp_spec_file):
        """Test JSON output structure is valid."""
        result = runner.invoke(app, ["scan", str(temp_spec_file), "--json"])

        assert result.exit_code == 0

        # Should be valid JSON
        data = json.loads(result.stdout)
        assert isinstance(data, list)

        if len(data) > 0:
            item = data[0]
            assert "spec_path" in item
            assert "metrics" in item
            assert "overall_weighted_average" in item["metrics"]

    def test_output_to_file(self, temp_spec_file, tmp_path):
        """Test writing output to file."""
        output_file = tmp_path / "results.json"

        result = runner.invoke(app, [
            "scan",
            str(temp_spec_file),
            "--json",
            "--output",
            str(output_file)
        ])

        assert result.exit_code == 0
        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)
            assert isinstance(data, list)

    def test_json_and_csv_conflict(self, temp_spec_file):
        """Test that --json and --csv cannot be used together."""
        result = runner.invoke(app, ["scan", str(temp_spec_file), "--json", "--csv"])

        assert result.exit_code == 1
        assert "Cannot use --json and --csv together" in result.stdout


class TestPerRequirementAnalysis:
    """Test per-requirement analysis feature."""

    def test_per_requirement_flag(self, temp_spec_file):
        """Test --per-req flag."""
        result = runner.invoke(app, ["scan", str(temp_spec_file), "--per-req"])

        assert result.exit_code == 0
        assert "requirement" in result.stdout.lower() or "FR-" in result.stdout


class TestBatchProcessing:
    """Test batch processing of multiple specs."""

    def test_batch_summary(self, temp_specs_dir):
        """Test batch summary output."""
        result = runner.invoke(app, ["scan", str(temp_specs_dir)])

        assert result.exit_code == 0
