# Understanding

**31 requirements quality metrics based on readability formulas, IEEE/ISO standards, and RE research**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/Testimonial/understanding/actions/workflows/test.yml/badge.svg)](https://github.com/Testimonial/understanding/actions/workflows/test.yml)

## What It Does

Scans requirement specifications and scores them across 6 categories:

### 31 Deterministic Metrics

| Category | Metrics | Weight | Basis | What It Measures |
|----------|---------|--------|-------|-----------------|
| Structure | 5 | 30% | IEEE 830, ISO 29148 | Atomicity, completeness, passive voice, pronouns, modal verbs |
| Testability | 3 | 20% | IEEE 830 §4.3.7 | Quantifiable constraints, density, boundary coverage |
| Readability | 6 | 15% | Flesch 1948, Kincaid 1975, Gunning 1952 | Flesch, Kincaid, Gunning Fog, SMOG, Coleman-Liau, ARI |
| Cognitive | 7 | 15% | Sweller 1988 (Cognitive Load Theory) | Sentence length, complexity, density, negations, conditionals |
| Semantic | 6 | 10% | Lucassen 2017 (Visual Narrator) | Actor/action/object presence, outcomes, triggers |
| Behavioral | 4 | 10% | Harel 2003/2005 (Statecharts) | Scenarios, transitions, branches, observability |

Quality gates enforce minimum thresholds based on ISO 29148:2018 and IEEE 830-1998.

### Energy Metrics (Experimental)

5 additional metrics using token-level perplexity from a local language model (SmolLM2-135M). Based on Hinton's energy framework and the Free Energy Principle — high-energy tokens are "surprising" to the model, which correlates with ambiguity or unusual phrasing.

| Metric | What It Measures |
|--------|-----------------|
| Mean Energy | Overall plausibility — how well the text fits standard language patterns |
| Max Energy | Localized ambiguity — the single most surprising token |
| Dispersion | Uniformity — whether difficulty is spread evenly or concentrated |
| Anchor Ratio | Clarity — percentage of well-predicted, easy tokens |
| Tail Ratio | Ambiguity — percentage of highly surprising tokens |

### How They Work Together

The 31 metrics are a **rule-based inspector** — they check structure, readability, and testability against established formulas and standards. Energy metrics are a **second pair of eyes** — a language model that reads your requirements and flags parts that feel ambiguous, even when all the rules pass.

A requirement can score 0.90 on the 31 metrics (good structure, readable, testable) but the energy model spots a phrase that's oddly worded or domain-novel — something pattern matching can't catch. The 31 metrics tell you *what* is wrong. Energy metrics tell you *where* the ambiguity hides.

Energy is a separate overlay (`--energy` flag), not part of the 31-metric score or quality gates.

## Installation

```bash
# Using uv (recommended) — install with NLP + diagram support
uv tool install git+https://github.com/Testimonial/understanding.git \
  --with "spacy>=3.0.0" \
  --with "graphviz>=0.20.0"

# Download spaCy language model
uv pip install --python ~/.local/share/uv/tools/understanding/bin/python \
  en-core-web-sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl

# Using pip (alternative)
pip install "understanding[all]"
python -m spacy download en_core_web_sm
```

### With Energy Metrics (Experimental)

Adds token-level perplexity analysis using a local language model (SmolLM2-135M, ~270MB auto-download on first use). No API keys needed.

```bash
# Using uv — add energy to the install command
uv tool install git+https://github.com/Testimonial/understanding.git \
  --with "spacy>=3.0.0" \
  --with "graphviz>=0.20.0" \
  --with "transformers>=4.30.0" \
  --with "torch>=2.0.0"

# Using pip
pip install "understanding[all,energy]"
```

Then use with `--energy` flag:
```bash
understanding spec.md --energy
```

## Usage

```bash
# Scan a spec (NLP + entity extraction enabled by default)
understanding spec.md

# Scan all specs in a directory
understanding specs/

# Auto-discover spec.md in current directory
understanding
```

### Diagrams

```bash
# Text diagram in terminal
understanding spec.md --diagram

# Export to file (format inferred from extension)
understanding spec.md --diagram diagram.png
understanding spec.md --diagram diagram.svg
understanding spec.md --diagram diagram.pdf
```

Requires graphviz for PNG/SVG/PDF: `brew install graphviz` (macOS) or `apt install graphviz` (Linux).

### Validation

```bash
# Enforce quality gates (exit code 1 on failure)
understanding spec.md --validate

# JSON for CI/CD
understanding spec.md --json --validate

# CSV for spreadsheets
understanding spec.md --csv --output results.csv
```

### Energy Analysis (Experimental)

```bash
# Detect ambiguity hotspots using token perplexity
understanding spec.md --energy
```

### Per-Requirement Breakdown

```bash
understanding spec.md --per-req
```

## Command Reference

| Flag | Description | Default |
|------|-------------|---------|
| `[SPEC]` | Path to spec file or directory | Auto-discover |
| `--basic` | Use 18 base metrics only (faster, no NLP) | Off |
| `--energy` | [Experimental] Token-level ambiguity analysis | Off |
| `--ears` | EARS pattern compliance | Off |
| `--diagram [PATH]` | Diagram output (text, or PNG/SVG/PDF to file) | Off |
| `--validate` / `-v` | Enforce quality gates | Off |
| `--per-req` | Per-requirement breakdown | Off |
| `--json` | JSON output (includes entities) | Off |
| `--csv` | CSV output | Off |
| `--output PATH` / `-o` | Write to file | stdout |

`--basic` skips NLP and entity extraction for fast CI checks (~200ms vs ~500ms).

## Example Output

```
Requirements Quality Metrics
============================

Overall Score: 0.78 (Good)

Category Scores:
  Readability:   0.87 (Very Good)
  Structure:     0.80 (Very Good)
  Cognitive:     0.71 (Good)
  Semantic:      0.89 (Very Good)
  Testability:   0.67 (Fair)
  Behavioral:    0.60 (Fair)

Quality Gates:
  Overall    >=0.70  0.78  PASS
  Structure  >=0.70  0.80  PASS
  Testability >=0.70  0.67  FAIL
  Semantic   >=0.60  0.89  PASS
  Cognitive  >=0.60  0.71  PASS
  Readability >=0.50  0.87  PASS

Status: FAILED (1/6 gates failed)
```

## Quality Gates

| Gate | Threshold | Based On |
|------|-----------|----------|
| Overall | >= 0.70 | ISO 29148:2018 |
| Structure | >= 0.70 | ISO 29148 §5.2.5 |
| Testability | >= 0.70 | ISO 29148 (mandatory) |
| Semantic | >= 0.60 | Lucassen 2017 |
| Cognitive | >= 0.60 | Sweller 1988 |
| Readability | >= 0.50 | Flesch 1948 |

## Python API

```python
from understanding import analyze_with_enhanced_metrics

result = analyze_with_enhanced_metrics(text)
metrics = result["enhanced_metrics"]

overall = metrics["overall_weighted_average"]
categories = metrics["category_averages"]

print(f"Overall: {overall:.2%}")
print(f"Structure: {categories['structure']:.2%}")
print(f"Testability: {categories['testability']:.2%}")
```

### Energy API (Experimental)

```python
from understanding import analyze_energy

# Requires: pip install understanding[energy]
result = analyze_energy("The system must validate user email format before saving.")
print(f"Composite: {result.composite_score:.2%}")

for token, energy in result.hotspot_tokens:
    print(f"  {token}: {energy:.2f}")
```

## Usage with Spec Kit

### As Extension (AI agent commands)

```bash
# Install extension into your spec-kit project
specify extension add --dev /path/to/understanding/extension

# Then use in your AI agent:
# /speckit.understanding.scan
# /speckit.understanding.validate
# /speckit.understanding.energy
```

See [extension/README.md](extension/README.md) for details.

### As Standalone Tool

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
uv tool install understanding

specify init my-project --ai claude
cd my-project

# Write spec, then validate
understanding specs/001-feature/spec.md --validate

# Continue if gates pass
specify plan
specify tasks
specify implement
```

## All 31 Metrics

**Structure (30%)** — standards-based (IEEE 830, ISO 29148): Atomicity, Completeness, Passive Voice Ratio, Ambiguous Pronoun Ratio, Modal Strength

**Testability (20%)** — standards-based (IEEE 830 §4.3.7): Hard Constraint Ratio, Constraint Density, Negative Space Coverage

**Readability (15%)** — proven formulas (Flesch 1948, Kincaid 1975, Gunning 1952): Flesch Reading Ease, Flesch-Kincaid Grade, Gunning Fog, SMOG, Coleman-Liau, ARI

**Cognitive (15%)** — theory-informed (Sweller 1988): Sentence Length, Syllable Complexity, Concept Density, Coordination, Subordination, Negation Load, Conditional Load

**Semantic (10%)** — research-inspired (Lucassen 2017): Actor Presence, Action Presence, Object Presence, Outcome Presence, Trigger Presence, SCC Composite

**Behavioral (10%)** — research-inspired (Harel 2003/2005): Scenario Decomposition, Transition Completeness, Branch Coverage Proxy, Observability Score

## Documentation

- [Complete Metrics Reference](docs/ENHANCED_METRICS_COMPLETE_REFERENCE.md)
- [Output Reference](docs/METRICS_OUTPUT_REFERENCE.md)
- [Quick Reference](docs/METRICS_QUICK_REFERENCE.md)
- [Scientific Validation](docs/SCIENTIFIC_VALIDATION_REPORT.md)
- [Weights Justification](docs/WEIGHTS_AND_GATES_JUSTIFICATION.md)
- [Energy Research](docs/ENERGY_TRANSFORMERS_RESEARCH.md)

## License

MIT - see [LICENSE](LICENSE)

## Related

- [Spec Kit](https://github.com/github/spec-kit) - Spec-Driven Development framework
- [Visual Narrator](https://github.com/MarcelRobeer/VisualNarrator) - User story quality analysis
