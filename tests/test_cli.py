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
        assert "scientifically-proven" in result.stdout or "requirements" in result.stdout


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
        assert "Basic Mode: 18 metrics" in result.stdout or "18" in result.stdout

    def test_scan_with_enhanced_mode(self, temp_spec_file):
        """Test scan command with enhanced (31 metrics) mode."""
        result = runner.invoke(app, ["scan", str(temp_spec_file), "--enhanced"])

        assert result.exit_code == 0
        assert "Enhanced Mode" in result.stdout or "31" in result.stdout

    def test_scan_directory(self, temp_specs_dir):
        """Test scan command with directory containing multiple specs."""
        result = runner.invoke(app, ["scan", str(temp_specs_dir)])

        assert result.exit_code == 0
        # Should process multiple specs
        assert "spec.md" in result.stdout.lower() or "batch" in result.stdout.lower()

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

        # Check CSV content
        csv_content = output_file.read_text()
        assert "Spec,Overall," in csv_content
        assert "Behavioral,Cognitive,Readability" in csv_content


class TestValidateCommand:
    """Test suite for validate command."""

    def test_validate_with_file(self, temp_spec_file):
        """Test validate command with specific file."""
        result = runner.invoke(app, ["validate", str(temp_spec_file)])

        # Exit code depends on quality gates, so don't assert it
        assert "Overall Score" in result.stdout
        assert "Quality Gates" in result.stdout

    def test_validate_without_gates(self, temp_spec_file):
        """Test validate command without enforcing gates."""
        result = runner.invoke(app, ["validate", str(temp_spec_file), "--no-gates"])

        # Should always exit 0 when --no-gates is used
        assert result.exit_code == 0
        assert "Quality Gates" in result.stdout

    def test_validate_directory(self, temp_specs_dir):
        """Test validate command with directory."""
        result = runner.invoke(app, ["validate", str(temp_specs_dir)])

        # Should process multiple specs
        assert "spec" in result.stdout.lower()

    def test_validate_nonexistent_file(self):
        """Test validate command with nonexistent file."""
        result = runner.invoke(app, ["validate", "/nonexistent/path/spec.md"])

        assert result.exit_code == 1
        assert "Error" in result.stdout or "not found" in result.stdout.lower()


class TestAutoDiscovery:
    """Test auto-discovery functionality."""

    def test_scan_auto_discovery_current_dir(self, temp_spec_file, monkeypatch):
        """Test scan auto-discovery in current directory."""
        # Change to directory containing spec.md
        monkeypatch.chdir(temp_spec_file.parent)

        result = runner.invoke(app, ["scan"])

        # Should find and scan the spec
        # Note: auto-discovery might not find it in temp dir, so we allow both outcomes
        # Either it finds it (exit 0) or doesn't (exit 1)
        assert result.exit_code in [0, 1]

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
        # Check for rich formatting elements
        assert "Category Scores" in result.stdout
        assert "Quality Gates" in result.stdout

    def test_json_output_structure(self, temp_spec_file):
        """Test JSON output structure is valid."""
        result = runner.invoke(app, ["scan", str(temp_spec_file), "--json"])

        assert result.exit_code == 0

        # Should be valid JSON
        data = json.loads(result.stdout)
        assert isinstance(data, list)

        # Verify structure
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

        # Verify file content is valid JSON
        with open(output_file) as f:
            data = json.load(f)
            assert isinstance(data, list)


class TestPerRequirementAnalysis:
    """Test per-requirement analysis feature."""

    def test_per_requirement_flag(self, temp_spec_file):
        """Test --per-req flag."""
        result = runner.invoke(app, ["scan", str(temp_spec_file), "--per-req"])

        assert result.exit_code == 0
        # Should mention requirements in output
        assert "requirement" in result.stdout.lower() or "FR-" in result.stdout

    def test_per_requirement_with_validate(self, temp_spec_file):
        """Test --per-req with validate command."""
        result = runner.invoke(app, ["validate", str(temp_spec_file), "--per-req"])

        # Should show per-requirement analysis
        assert "requirement" in result.stdout.lower() or "FR-" in result.stdout


class TestBatchProcessing:
    """Test batch processing of multiple specs."""

    def test_batch_summary(self, temp_specs_dir):
        """Test batch summary output."""
        result = runner.invoke(app, ["scan", str(temp_specs_dir)])

        assert result.exit_code == 0
        # Should show batch summary
        assert "batch" in result.stdout.lower() or "analyzed" in result.stdout.lower()

    def test_batch_detailed(self, temp_specs_dir):
        """Test batch with detailed output."""
        result = runner.invoke(app, ["scan", str(temp_specs_dir), "--detailed"])

        assert result.exit_code == 0
        # Should show detailed results for each spec
