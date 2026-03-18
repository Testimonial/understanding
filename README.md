# Understanding

**31 requirements quality metrics based on readability formulas, IEEE/ISO standards, and RE research**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/Testimonial/understanding/actions/workflows/test.yml/badge.svg)](https://github.com/Testimonial/understanding/actions/workflows/test.yml)

<p align="center">
  <img src="demo.gif" alt="understanding CLI demo" width="800">
</p>

## Why This Exists

Spec reviews today lack reproducibility — whether done by humans or LLMs, the same document produces different feedback every time. That's not a quality process.

Requirements engineering has 40+ years of proven research — IEEE 830, ISO 29148, readability formulas, cognitive load theory — but it lived in academic papers, not engineering toolchains. **understanding** makes it operational: deterministic analysis you can run in a terminal and integrate into CI/CD. Same input, same output, every time. No API keys. No cloud. ~500ms.

## How It Compares

| Feature | understanding | LLM-based review | Manual review |
|---------|:---:|:---:|:---:|
| Deterministic (reproducible) | Yes | No | No |
| Works offline | Yes | No | Yes |
| No API keys needed | Yes | No | Yes |
| Standards-based (IEEE/ISO) | Yes | Varies | Varies |
| Speed (<1s) | Yes | No | N/A |
| CI/CD integration | Yes | Possible | No |
| Energy ambiguity detection | Yes | N/A | No |
| JSON/CSV export | Yes | Varies | No |
| Cost | Free | $$$ | Time |

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

All dependencies (NLP, diagrams, energy metrics) are bundled — one command installs everything.

```bash
# Using uv (recommended)
uv tool install git+https://github.com/Testimonial/understanding.git

# Using pip (alternative)
pip install git+https://github.com/Testimonial/understanding.git
```

Energy metrics use a local language model (SmolLM2-135M, ~270MB auto-download on first use). No API keys needed. Use with `--energy` flag:
```bash
understanding spec.md --energy
```

Graphviz is required for PNG/SVG/PDF diagram export: `brew install graphviz` (macOS) or `apt install graphviz` (Linux).

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
| `--diagram [PATH]` | Diagram output (text, or PNG/SVG/PDF to file) | Off |
| `--validate` / `-v` | Enforce quality gates | Off |
| `--per-req` | Per-requirement breakdown | Off |
| `--json` | JSON output (includes entities) | Off |
| `--csv` | CSV output | Off |
| `--output PATH` / `-o` | Write to file | stdout |

`--basic` skips NLP and entity extraction for fast CI checks (~200ms vs ~500ms).

## Example Output

See the [demo GIF above](#understanding) for colored terminal output, or run:

```bash
understanding spec.md          # 31 metrics + quality gates + entity analysis
understanding spec.md --energy  # + token-level ambiguity hotspots
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

# Energy is included in the default install
result = analyze_energy("The system must validate user email format before saving.")
print(f"Composite: {result.composite_score:.2%}")

for token, energy in result.hotspot_tokens:
    print(f"  {token}: {energy:.2f}")
```

## Usage with Spec Kit

Understanding works both as a **standalone CLI** and as a **Spec Kit extension** that adds `/speckit.understanding.*` slash commands to your AI agent.

### Step 1: Install Spec Kit

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

### Step 2: Install Understanding CLI (prerequisite)

Follow the [Installation](#installation) section above. The extension commands call this tool under the hood.

### Step 3: Install the Extension

```bash
# Clone and install extension into your spec-kit project
git clone https://github.com/Testimonial/understanding.git /tmp/understanding
cd your-project
specify extension add --dev /tmp/understanding/extension

# Verify
specify extension list
# Should show: Understanding (v3.5.0)
```

### Step 4: Use in AI Agent

```
/speckit.understanding.scan                          # 31 metrics + entities
/speckit.understanding.scan specs/001-feature/spec.md  # Specific spec
/speckit.understanding.validate                      # Enforce quality gates
/speckit.understanding.energy                        # Experimental ambiguity detection
```

The extension also hooks into `/speckit.tasks` — after generating tasks, it prompts to validate the spec.

See [extension/README.md](extension/README.md) for full extension documentation.

### Standalone (without extension)

You can also use understanding directly without the extension:

```bash
understanding specs/001-feature/spec.md --validate
understanding specs/ --energy
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
