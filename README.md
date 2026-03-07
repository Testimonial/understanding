# Understanding

**Requirements understanding and cognitive load metrics - pattern-based quality analysis**

Simple, deterministic metrics for requirements quality using established readability formulas and pattern matching.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/Testimonial/understanding/actions/workflows/test.yml/badge.svg)](https://github.com/Testimonial/understanding/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/Testimonial/understanding/branch/main/graph/badge.svg)](https://codecov.io/gh/Testimonial/understanding)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Comprehensive requirements quality validation with 31 metrics across 6 dimensions:
- **Readability** (6 metrics)
- **Structure** (5 metrics)
- **Cognitive Load** (7 metrics)
- **Semantic Completeness** (6 metrics)
- **Testability** (3 metrics)
- **Behavioral Clarity** (4 metrics)

## Features

- **31 Deterministic Metrics** - Pattern-based analysis using established formulas
- **Energy Metrics (NEW)** - Token-level perplexity analysis using a local LM to detect ambiguity hotspots (optional `--energy` flag)
- **Entity Extraction** - Extract actors, actions, objects, and relationships from requirements (optional `--entities` flag)
- **EARS Compliance** - Validate against Easy Approach to Requirements Syntax patterns (optional `--ears` flag)
- **Quality Gates** - Threshold-based validation (Overall >=0.70, Structure >=0.70, Testability >=0.70, Semantic >=0.60, Cognitive >=0.60, Readability >=0.50)
- **Comprehensive Reports** - JSON, CSV, and human-readable formats
- **Fast Analysis** - ~200ms per spec using regex and statistical methods
- **Universal** - Works with any text format (markdown, plain text, etc.)
- **No External Dependencies** - Pure Python pattern matching (spaCy, energy model optional)

## Implementation Approach

**This tool uses pattern-based analysis, not sophisticated NLP.**

### What We Actually Do

- **Readability**: Direct implementation of mathematical formulas (Flesch, Gunning Fog, etc.)
- **Structure**: Regex patterns for modal verbs (must/shall/should), passive voice, pronouns
- **Cognitive**: Statistical analysis of sentence length, word complexity, coordination
- **Semantic**: Keyword matching (basic) OR spaCy NLP (with `--nlp` flag)
  - Basic: Pattern matching for actors/actions/objects
  - NLP: Dependency parsing, POS tagging, semantic role labeling
- **Testability**: Regex for numbers, units, comparisons (e.g., ">= 95%", "< 2 seconds")
- **Behavioral**: Pattern matching for conditionals, state transitions

### NLP Enhancement (Optional)

**Performance Comparison:**

| Mode | Speed | Semantic Accuracy | Dependencies | Best For |
|------|-------|-------------------|--------------|----------|
| Pattern-based | ~200ms | 70-80% | None | CI/CD, quick checks |
| NLP mode (`--nlp`) | 🐌 ~500ms | 85-95% | spaCy (~50MB) | Detailed analysis |

**Example Impact:**

```bash
# Pattern-based: Semantic score 58.17% ❌
understanding scan spec.md

# NLP mode: Semantic score 71.09% ✅ (+12.92%)
understanding scan spec.md --nlp
```

**What NLP Adds:**
- ✅ Dependency parsing (nsubj, dobj, ROOT verbs)
- ✅ POS tagging (VERB, NOUN identification)
- ✅ Lemmatization ("validates", "validated" → "validate")
- ✅ Better actor/action/object detection

**When to Use:**
- Use pattern-based for: Fast CI/CD checks, large batches
- Use NLP mode for: Final validation, detailed analysis, gate-critical specs

### What We Still Don't Do

- ❌ UML/ER diagram generation
- ❌ FSM/statechart generation
- ❌ Machine learning models

### Foundation

Based on established formulas and standards:
- Flesch (1948), Kincaid (1975), Gunning (1952) - Readability formulas
- Sweller (1988) - Cognitive load theory principles
- IEEE 830-1998, ISO 29148:2018 - Requirements standards

## Installation

### Basic Installation (Pattern-Based)

Fast, no dependencies, good for most use cases:

```bash
# Using uv (recommended)
uv tool install understanding

# Using pip
pip install understanding
```

### With NLP Enhancement (Optional)

For ~13% better semantic analysis using spaCy dependency parsing:

#### Method 1: Using uv tool (recommended)

```bash
# Step 1: Install understanding with spaCy and graphviz
uv tool install understanding --with "spacy>=3.0.0" --with "graphviz>=0.20.0"

# Step 2: Download spaCy model using uv pip
uv pip install --python ~/.local/share/uv/tools/understanding/bin/python \
  en-core-web-sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl

# Step 3: Verify NLP is working
understanding scan --nlp
```

**Note**: For local development, use `uv tool install . --with "spacy>=3.0.0" --with "graphviz>=0.20.0"` from the repo directory.

#### Method 2: Using pip

```bash
# Install with NLP dependencies
pip install "understanding[nlp]"

# Download spaCy language model
python -m spacy download en_core_web_sm

# Verify installation
python -c "import spacy; spacy.load('en_core_web_sm'); print('✓ NLP ready')"
```

#### Method 3: Development/Editable Install

```bash
# Clone repository
git clone https://github.com/Testimonial/understanding.git
cd understanding

# Install with NLP support
pip install -e ".[nlp]"
python -m spacy download en_core_web_sm

# Or with uv
uv pip install -e ".[nlp]"
python -m spacy download en_core_web_sm
```

### Verify Installation

```bash
# Check version
understanding --help

# Test scan (pattern-based)
understanding scan

# Test with NLP (if installed)
understanding scan --nlp
```

### Troubleshooting NLP Installation

#### Issue: "No module named 'spacy'"

```bash
# If using uv tool, reinstall with spacy
uv tool uninstall understanding
uv tool install --with spacy understanding

# If using pip
pip install "understanding[nlp]"
```

#### Issue: "Can't find model 'en_core_web_sm'"

```bash
# For uv tool installation - need to install pip first
source ~/.local/share/uv/tools/understanding/bin/activate
curl -sS https://bootstrap.pypa.io/get-pip.py | python
python -m spacy download en_core_web_sm
deactivate

# For pip installation
python -m spacy download en_core_web_sm
```

#### Issue: NLP mode gives same scores as pattern-based

This means spaCy isn't loading. Verify:

```bash
# Check if spaCy is in the right environment
understanding --help  # Note the Python path
python -c "import spacy; spacy.load('en_core_web_sm')"

# If error, reinstall with model
```

#### Check NLP is Working

```bash
# Should show ~13% higher semantic score with --nlp
understanding scan yourspec.md | grep Semantic
understanding scan yourspec.md --nlp | grep Semantic
```

### With Energy Metrics (Optional)

Token-level perplexity analysis using a local language model (SmolLM2-135M, ~270MB):

```bash
# Install energy dependencies
pip install "understanding[energy]"

# Or with uv
uv tool install understanding --with "transformers>=4.30.0" --with "torch>=2.0.0"

# Verify
understanding scan spec.md --energy
```

The model auto-downloads on first use and is cached locally (~/.cache/huggingface/).

## Usage Guide

### Quick Start

```bash
# Simplest usage - auto-discovers spec.md in current directory
understanding scan

# Scan a specific spec file
understanding scan specs/001-feature/spec.md

# Scan all specs in a directory
understanding scan specs/
```

### Analysis Modes

```bash
# Default: 31 enhanced metrics
understanding scan spec.md

# Fast mode: 18 base metrics only
understanding scan spec.md --basic

# Better accuracy: Enable NLP for semantic analysis (~13% improvement)
understanding scan spec.md --nlp

# Energy analysis: token-level ambiguity detection using local LM
understanding scan spec.md --energy

# Combine modes
understanding scan spec.md --energy --nlp
```

### Quality Validation

```bash
# Enforce quality gates (exits with code 1 if any gate fails)
understanding scan spec.md --validate

# CI/CD mode: JSON output + validation
understanding scan spec.md --json --validate

# Per-requirement analysis (detailed breakdown)
understanding scan spec.md --per-req
```

### Output Formats

```bash
# Human-readable (default)
understanding scan spec.md

# JSON for CI/CD integration
understanding scan spec.md --json

# CSV for spreadsheet analysis
understanding scan spec.md --csv

# Save to file
understanding scan spec.md --json --output report.json
understanding scan spec.md --csv --output results.csv
```

### Entity Extraction & Visualization

Extract actors, actions, objects, and their relationships:

```bash
# Extract entities and relationships
understanding scan spec.md --entities

# Better results with NLP
understanding scan spec.md --entities --nlp

# Text-based diagram (auto-enables --entities)
understanding scan spec.md --diagram

# Export diagrams (auto-enables --entities, infers format from extension)
understanding scan spec.md --png diagram.png          # PNG
understanding scan spec.md --png diagram.svg          # SVG (format auto-detected)
understanding scan spec.md --png diagram.pdf          # PDF

# Combined: text diagram + PNG export
understanding scan spec.md --diagram --png output.png

# With NLP for best results
understanding scan spec.md --nlp --diagram --png diagram.svg

# JSON export with entity data
understanding scan spec.md --entities --json
```

**Tip**: `--diagram` and `--png` automatically enable `--entities`, so you don't need to specify it explicitly!

**Cross-Spec Analysis (NEW):**

When scanning multiple specifications, entities are automatically aggregated into a unified view:

```bash
# Scan directory - aggregates entities from all specs
understanding scan specs/ --entities --nlp

# Generate unified system diagram
understanding scan specs/ --entities --nlp --png system-architecture.svg

# Shows:
# - Combined entities from all specs
# - Cross-spec relationships
# - Deduplicated entities
# - Unified system diagram
```

**Single Spec vs Multiple Specs:**
- **Single spec** (`spec.md`): Focused entity analysis for that spec only
- **Multiple specs** (`specs/`): Unified cross-spec analysis showing the big picture

**What Gets Extracted:**
- **Actors**: Users, systems, roles (e.g., "administrator", "payment service")
- **Actions**: Operations, verbs (e.g., "validate", "process", "notify")
- **Objects**: Data, UI elements (e.g., "order", "notification", "dashboard")
- **Systems**: System components (e.g., "database", "API", "server")
- **Conditions**: Triggers, preconditions (e.g., "if user clicks", "when payment succeeds")
- **Relationships**: Actor→Action→Object chains, triggers, conditions

**Enhanced Vocabulary (v3.2.0):**
- 30+ actors (microservices, gateways, external systems)
- 90+ actions (auth, encryption, routing, pub/sub, caching, monitoring)
- 50+ objects (tokens, events, queues, metrics, infrastructure)

**Example Entity Output:**
```
Entity Analysis
========================================
Total Entities:     45
Unique Actors:      8
Unique Actions:     12
Unique Objects:     15

Top Actors:
  • user
  • system
  • administrator

Top Actions:
  • validate
  • create
  • process

Performs Relationships:
  • user → validate
  • system → send
  • administrator → approve

Modifies Relationships:
  • validate → input
  • create → account
  • process → payment
```

**Example Diagram:**
```
[ACTOR] user
  --performs--> [ACTION] validate
  --performs--> [ACTION] create
[ACTION] validate
  --modifies--> [OBJECT] input
[ACTION] create
  --modifies--> [OBJECT] account
```

**Example Cross-Spec Output:**
```
Cross-Spec Entity Analysis
Unified view across 2 specifications
========================================
Specifications Analyzed: 2
Total Entities:         30
Unique Actors:          14
Unique Actions:         11
Unique Objects:          5

Top Actors:
  • api gateway
  • authentication service
  • message broker
  • notification service
  • load balancer
  • monitoring service
  ... and 8 more

Top Actions:
  • authenticate
  • consume
  • publish
  • encrypt
  • route
  • monitor
  ... and 5 more

Cross-Spec Relationships:
  • authentication service → publish → message
  • notification service → consume → message
  • api gateway → route → backend
  • load balancer → distribute → request
```

**Performance:**
- Pattern-based: ~50ms overhead per spec
- NLP mode: ~200ms overhead per spec (better accuracy)
- Cross-spec aggregation: ~10ms additional overhead

**PNG/SVG Diagram Export (Optional):**

Generate professional diagrams with styled nodes and edges:

```bash
# Install diagram support
pip install understanding[diagram]

# Or install all extras
pip install understanding[all]  # Includes nlp + diagram

# System requirement (one-time)
brew install graphviz          # macOS
apt-get install graphviz       # Ubuntu/Debian
dnf install graphviz           # Fedora/RHEL

# Generate PNG diagram
understanding scan spec.md --entities --nlp --png output.png

# Generate SVG (scalable, better for docs)
understanding scan spec.md --entities --nlp --png output.svg --png-format svg

# Generate PDF
understanding scan spec.md --entities --nlp --png output.pdf --png-format pdf
```

**Diagram Features:**
- Color-coded nodes by entity type (actors=blue, actions=green, objects=orange)
- Styled edges by relationship (performs=solid, triggers=dashed)
- Professional layout using Graphviz DOT engine
- Scalable vector graphics (SVG) or raster (PNG/PDF)

**When to Use:**
- Understanding complex specifications
- Identifying missing actors or actions
- Visualizing requirement relationships
- Detecting inconsistencies in terminology
- Creating documentation diagrams
- Presenting requirements to stakeholders

## Command Reference

### All Available Flags

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `[SPEC]` | - | Path to spec.md file or directory | Auto-discover |
| `--enhanced` | - | Use all 31 metrics | ✓ Enabled |
| `--basic` | - | Use only 18 base metrics | Disabled |
| `--nlp` | - | Enable spaCy NLP for better accuracy | Disabled |
| `--energy` | - | Token-level energy/perplexity analysis | Disabled |
| `--ears` | - | EARS pattern compliance checking | Disabled |
| `--entities` | - | Extract entities and relationships | Auto¹ |
| `--diagram` | - | Generate text-based diagram | Disabled |
| `--png PATH` | - | Export diagram (PNG/SVG/PDF) | - |
| `--png-format` | - | Override format (png/svg/pdf) | Auto² |
| `--validate` | `-v` | Enforce quality gates | Disabled |
| `--test` | `-t` | Alias for --validate | Disabled |
| `--per-req` | - | Per-requirement analysis | Disabled |
| `--json` | - | JSON output format | Disabled |
| `--csv` | - | CSV output format³ | Disabled |
| `--output PATH` | `-o` | Write output to file | stdout |

**Notes:**
1. Auto-enabled when `--diagram` or `--png` is used
2. Auto-detected from file extension (.png, .svg, .pdf)
3. Cannot be used with `--json` (choose one)

### Common Workflows

#### Development Workflow
```bash
# Quick check during development
understanding scan

# Detailed analysis with NLP
understanding scan --nlp

# Visual review
understanding scan --diagram --png review.svg
```

#### CI/CD Pipeline
```bash
# Validate and fail if quality gates not met
understanding scan --validate --json > report.json

# Exit codes:
#   0 = All quality gates passed
#   1 = One or more quality gates failed
```

#### Documentation Generation
```bash
# Generate all artifacts
understanding scan spec.md --nlp \
  --diagram \
  --png entity-diagram.svg \
  --json --output metrics.json \
  --csv --output metrics.csv
```

#### Batch Analysis
```bash
# Analyze multiple specs
understanding scan specs/ --csv --output batch-results.csv

# With validation
understanding scan specs/ --validate --json
```

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
  ✓ Overall ≥0.70 (0.78)
  ✓ Structure ≥0.70 (0.80)
  ✓ Testability ≥0.70 (0.67) - FAILED ❌
  ✓ Semantic ≥0.60 (0.89)
  ✓ Cognitive ≥0.60 (0.71)
  ✓ Readability ≥0.50 (0.87)

Status: FAILED (1/6 gates failed) ❌
```

## Usage with Spec Kit

This tool is designed to complement [Spec Kit](https://github.com/github/spec-kit):

```bash
# Install both
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
uv tool install understanding

# Use together
specify init my-project --ai claude
cd my-project
# ... create specification using Spec Kit workflow ...

# Check quality
understanding scan specs/001-feature/spec.md --test

# Continue with Spec Kit if quality gates pass
specify plan
specify tasks
specify implement
```

## All 31 Metrics

### Structure (5 metrics, 30% weight)
- **Atomicity Score** (highest weight)
- **Completeness Score** (highest weight)
- Passive Voice Ratio
- Ambiguous Pronoun Ratio
- Modal Strength (MUST/SHALL/SHOULD)

### Testability (3 metrics, 20% weight)
- Hard Constraint Ratio (quantifiable vs subjective)
- Constraint Density
- Negative Space Coverage (explicit boundaries)

### Semantic (6 metrics, 10% weight)
- Actor Presence (who)
- Action Presence (what)
- Object Presence (to what)
- Outcome Presence (result)
- Trigger Presence (when)
- SCC Composite Score

### Cognitive (7 metrics, 15% weight)
- Sentence Length
- Syllable Complexity
- Concept Density
- Coordination Complexity
- Subordination Complexity
- Negation Load
- Conditional Load

### Readability (6 metrics, 15% weight)
- Flesch Reading Ease
- Flesch-Kincaid Grade Level
- Gunning Fog Index
- SMOG Index
- Coleman-Liau Index
- Automated Readability Index

### Behavioral (4 metrics, 10% weight)
- Scenario Decomposition (conditionals)
- Transition Completeness (guard→action→outcome)
- Branch Coverage Proxy
- Observability Score

## Python API

```python
from understanding import analyze_with_enhanced_metrics

# Analyze requirements text
result = analyze_with_enhanced_metrics(requirements_text)
metrics = result["enhanced_metrics"]

# Get summary scores
overall = metrics["overall_weighted_average"]  # 0-1 range
categories = metrics["category_averages"]

print(f"Overall: {overall:.2%}")
print(f"Semantic: {categories['semantic']:.2%}")
print(f"Testability: {categories['testability']:.2%}")

# Check quality gates
if overall >= 0.70 and categories["semantic"] >= 0.60 and categories["testability"] >= 0.60:
    print("Quality gates passed")
else:
    print("Quality gates failed")

# Access individual metrics
for score in metrics["scores"]:
    print(f"{score['name']}: {score['score']:.2%}")
```

### Energy API (optional)

```python
from understanding import analyze_energy

# Requires: pip install understanding[energy]
result = analyze_energy("The system must validate user email format before saving.")

print(f"Composite: {result.composite_score:.2%}")
print(f"Mean energy: {result.raw_mean_energy:.2f}")

# Hotspot tokens (most ambiguous/surprising)
for token, energy in result.hotspot_tokens:
    print(f"  {token}: {energy:.2f}")
```

## Documentation

- **[Complete Metrics Reference](docs/ENHANCED_METRICS_COMPLETE_REFERENCE.md)** - All formulas, weights, examples
- **[Output Reference](docs/METRICS_OUTPUT_REFERENCE.md)** - Understanding validation output
- **[Quick Reference](docs/METRICS_QUICK_REFERENCE.md)** - Visual cheat sheet
- **[Scientific Validation](docs/SCIENTIFIC_VALIDATION_REPORT.md)** - Research citations

## Quality Gates

Research-backed thresholds (based on ISO 29148:2018, IEEE 830-1998, ISO 25010:2023):

| Gate | Threshold | Standard/Research | Description |
|------|-----------|-------------------|-------------|
| Overall | ≥0.70 | ISO 29148:2018 | Minimum acceptable quality |
| Structure | ≥0.70 | ISO 29148 §5.2.5 | Atomicity & Completeness |
| Testability | ≥0.70 | ISO 29148 (mandatory) | Verifiability |
| Semantic | ≥0.60 | Lucassen 2017 | Actor-Action-Object completeness |
| Cognitive | ≥0.60 | Sweller 1988 | Cognitive load management |
| Readability | ≥0.50 | Flesch 1948 | Understanding (lower for technical) |

Note: Behavioral metrics have no gate (context-dependent)

## Contributing

Contributions welcome! Areas of interest:
- Additional metrics from requirements engineering research
- Improved NLP semantic extraction
- Language support beyond English
- Integration with other tools

## License

MIT License - see [LICENSE](LICENSE) for details

## Related Projects

- [Spec Kit](https://github.com/github/spec-kit) - Spec-Driven Development framework
- [Visual Narrator](https://github.com/MarcelRobeer/VisualNarrator) - User story quality analysis

## Support

- **Issues**: [GitHub Issues](https://github.com/Testimonial/understanding-enhanced/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Testimonial/understanding-enhanced/discussions)
- **Documentation**: [Full Docs](docs/)

## Acknowledgments

Built on:
- Established readability formulas (Flesch, Kincaid, Gunning)
- Cognitive load theory (Sweller)
- Requirements engineering standards (IEEE 830, ISO 29148)
- Simple pattern-based analysis (regex for constraints, keywords for patterns)

---

**Made for better requirements engineering**
