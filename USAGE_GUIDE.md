# Usage Guide

## Command Reference

### `understanding scan`

Scan specifications for quality metrics.

```bash
understanding scan [spec-file-or-directory] [OPTIONS]
```

**Arguments**:
- `[spec-file-or-directory]` - Optional path to spec.md file or directory (auto-discovers if omitted)

**Auto-discovery** (when no path provided):
- Searches `./spec.md` (current directory)
- Searches `./specs/*/spec.md` (most recent in Spec Kit structure)
- Respects `SPECIFY_FEATURE` environment variable

**Options**:
- `--enhanced` / `--basic` - Use all 31 metrics (default) or base 18 metrics
- `--energy` - Include energy consumption metrics (requires `understanding[energy]` extras)
- `--ears` - Include EARS (Easy Approach to Requirements Syntax) pattern analysis
- `--json` - Output JSON format
- `--output FILE` / `-o FILE` - Write output to file

**Examples**:

```bash
# Auto-discover spec in current directory or specs/ folder
understanding scan

# Scan single spec (enhanced mode - 31 metrics)
understanding scan specs/001-feature/spec.md

# Scan in basic mode (18 metrics)
understanding scan specs/001-feature/spec.md --basic

# Scan all specs in directory
understanding scan specs/

# JSON output
understanding scan specs/001-feature/spec.md --json

# Save to file
understanding scan specs/001-feature/spec.md -o report.json --json
```

---

### `understanding validate`

Validate spec against constitutional quality gates.

```bash
understanding validate [spec-file] [OPTIONS]
```

**Arguments**:
- `[spec-file]` - Optional path to spec.md file (auto-discovers if omitted)

**Auto-discovery** (when no path provided):
- Searches `./spec.md` (current directory)
- Searches `./specs/*/spec.md` (most recent in Spec Kit structure)
- Respects `SPECIFY_FEATURE` environment variable

**Options**:
- `--gates` / `--no-gates` - Enforce quality gates (default: enabled)

**Quality Gates**:
- Overall score ≥0.70
- Structure score ≥0.70
- Testability score ≥0.70
- Semantic score ≥0.60
- Cognitive score ≥0.60
- Readability score ≥0.50

**Examples**:

```bash
# Auto-discover and validate (exits with code 1 if failed)
understanding validate

# Validate specific file with quality gates
understanding validate specs/001-feature/spec.md

# Validate without enforcing gates (always exits 0)
understanding validate specs/001-feature/spec.md --no-gates
```

**Exit Codes**:
- `0` - Validation passed
- `1` - Validation failed (quality gates not met)

---

### `understanding version`

Show version information.

```bash
understanding version
```

---

### Energy Metrics (`--energy`)

Analyze the energy consumption implications of your requirements. Requires the energy extras:

```bash
pip install "understanding[energy]"
```

**Usage**:

```bash
# Scan with energy metrics included
understanding scan specs/001-feature/spec.md --energy

# Combine with JSON output
understanding scan specs/001-feature/spec.md --energy --json

# Validate with energy awareness
understanding validate specs/001-feature/spec.md --energy
```

Energy metrics evaluate requirements for computational cost awareness, resource efficiency language, and sustainability considerations.

---

### EARS Pattern Analysis (`--ears`)

Analyze requirements against EARS (Easy Approach to Requirements Syntax) patterns. EARS defines structured templates for writing unambiguous requirements.

**Usage**:

```bash
# Scan with EARS pattern detection
understanding scan specs/001-feature/spec.md --ears

# Combine with other flags
understanding scan specs/001-feature/spec.md --ears --energy --json
```

EARS patterns detected:
- **Ubiquitous**: "The [system] shall [action]"
- **Event-driven**: "WHEN [trigger], the [system] shall [action]"
- **State-driven**: "WHILE [state], the [system] shall [action]"
- **Optional**: "WHERE [feature], the [system] shall [action]"
- **Unwanted behavior**: "IF [condition], THEN the [system] shall [action]"

---

## Python API

### Basic Usage

```python
from understanding import analyze_with_enhanced_metrics

# Read spec
spec_text = open("specs/001-feature/spec.md").read()

# Analyze (all 31 metrics)
result = analyze_with_enhanced_metrics(spec_text)

# Get summary metrics
metrics = result["enhanced_metrics"]
overall = metrics["overall_weighted_average"]
categories = metrics["category_averages"]

print(f"Overall: {overall:.2%}")
print(f"Readability: {categories['readability']:.2%}")
print(f"Semantic: {categories['semantic']:.2%}")
```

### Checking Quality Gates

```python
from understanding import analyze_with_enhanced_metrics

result = analyze_with_enhanced_metrics(spec_text)
metrics = result["enhanced_metrics"]

overall = metrics["overall_weighted_average"]
semantic = metrics["category_averages"]["semantic"]
testability = metrics["category_averages"]["testability"]

# Check gates
if overall >= 0.70 and semantic >= 0.60 and testability >= 0.60:
    print("✅ Quality gates passed")
else:
    print("❌ Quality gates failed")
    if overall < 0.70:
        print(f"  Overall too low: {overall:.2%}")
    if semantic < 0.60:
        print(f"  Semantic too low: {semantic:.2%}")
    if testability < 0.60:
        print(f"  Testability too low: {testability:.2%}")
```

### Accessing Individual Metrics

```python
# Get all metric scores
all_scores = metrics["scores"]

# Find specific metric
atomicity = next(s for s in all_scores if s["name"] == "atomicity_score")
print(f"Atomicity: {atomicity['score']:.2%}")
print(f"Weight: {atomicity['weight']:.1%}")
print(f"Raw value: {atomicity['raw_value']}")

# Get metrics by category
semantic_metrics = [s for s in all_scores if s["category"] == "semantic"]
for m in semantic_metrics:
    print(f"{m['name']}: {m['score']:.2%}")

# Find lowest scoring metrics
sorted_by_score = sorted(all_scores, key=lambda x: x["score"])
print("Bottom 5 metrics:")
for metric in sorted_by_score[:5]:
    print(f"  {metric['name']}: {metric['score']:.2%}")
```

### Base 18 Metrics (Fast Mode)

```python
from understanding import analyze_with_normalized_metrics

# Use base 18 metrics only (faster, no semantic/behavioral)
result = analyze_with_normalized_metrics(spec_text)
metrics = result["normalized_metrics"]

overall = metrics["overall_weighted_average"]
categories = metrics["category_averages"]  # Only readability, structure, cognitive

print(f"Overall: {overall:.2%}")
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Spec Quality Check

on:
  pull_request:
    paths:
      - 'specs/**/*.md'

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install understanding
        run: pip install understanding

      - name: Validate specs
        run: |
          for spec in specs/*/spec.md; do
            echo "Validating $spec..."
            understanding validate "$spec" || exit 1
          done

      - name: Generate report
        if: always()
        run: |
          understanding scan specs/ --json > metrics-report.json

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: metrics-report
          path: metrics-report.json
```

### GitLab CI

```yaml
spec-quality:
  stage: test
  image: python:3.11
  before_script:
    - pip install understanding
  script:
    - |
      for spec in specs/*/spec.md; do
        echo "Validating $spec..."
        understanding validate "$spec" || exit 1
      done
  artifacts:
    when: always
    paths:
      - metrics-report.json
    reports:
      junit: metrics-report.json
```

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Validate all staged spec files
for file in $(git diff --cached --name-only | grep 'specs/.*/spec.md'); do
  if [ -f "$file" ]; then
    echo "Validating $file..."
    understanding validate "$file" --no-gates || {
      echo "❌ Quality gates failed for $file"
      echo "Run: understanding scan $file"
      exit 1
    }
  fi
done

echo "✅ All specs passed quality validation"
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Common Workflows

### Workflow 1: New Feature Spec

```bash
# 1. Create spec with Spec Kit
specify init my-feature --ai claude
cd my-feature
# ... write spec.md ...

# 2. Validate quality
understanding scan specs/001-feature/spec.md

# 3. If low score, iterate
# ... improve spec based on feedback ...
understanding scan specs/001-feature/spec.md

# 4. Once quality gates pass, continue
understanding validate specs/001-feature/spec.md
specify plan
```

### Workflow 2: Batch Analysis

```bash
# Scan all specs
understanding scan specs/ --json -o all-metrics.json

# Parse results with jq
jq '.[] | select(.metrics.overall_weighted_average < 0.70)' all-metrics.json

# Find specs needing improvement
for spec in specs/*/spec.md; do
  score=$(understanding scan "$spec" --json | jq '.metrics.overall_weighted_average')
  if (( $(echo "$score < 0.70" | bc -l) )); then
    echo "$spec needs improvement: $score"
  fi
done
```

### Workflow 3: Compare Before/After

```bash
# Before changes
understanding scan specs/001-feature/spec.md --json > before.json

# Make improvements to spec
# ... edit spec.md ...

# After changes
understanding scan specs/001-feature/spec.md --json > after.json

# Compare
python -c "
import json
before = json.load(open('before.json'))
after = json.load(open('after.json'))
before_score = before['metrics']['overall_weighted_average']
after_score = after['metrics']['overall_weighted_average']
improvement = (after_score - before_score) * 100
print(f'Improvement: {improvement:+.1f} percentage points')
"
```

---

## Tips & Best Practices

### When to Run Validation

✅ **Always validate**:
- Before creating implementation plan
- Before submitting PR with spec changes
- After major spec revisions

✅ **Consider validating**:
- After each spec writing session
- When adding new requirements

❌ **Don't validate**:
- During initial brainstorming (too early)
- On incomplete drafts (expected to be low)

### Interpreting Low Scores

**Low Semantic (<0.60)**:
- Add clear actors (who)
- Specify actions (what happens)
- Define outcomes (results)
- Example: "User can delete account and receives confirmation"

**Low Testability (<0.60)**:
- Replace "fast" with "< 200ms"
- Replace "many" with "1000+ users"
- Add explicit boundaries ("must not store passwords in plain text")

**Low Behavioral (<0.60)**:
- Add conditionals: "IF user is authenticated, THEN..."
- Define state transitions
- Specify error paths

### Performance Tips

- Use `--basic` for quick checks (18 metrics, ~50ms)
- Use `--enhanced` for thorough validation (31 metrics, ~200ms)
- Install spaCy for better semantic analysis (optional)

---

## Getting Help

```bash
# Command help
understanding --help
understanding scan --help
understanding validate --help

# Documentation
# See docs/ directory for complete reference
```

---

## Related Documentation

- [Complete Metrics Reference](docs/ENHANCED_METRICS_COMPLETE_REFERENCE.md)
- [Output Reference](docs/METRICS_OUTPUT_REFERENCE.md)
- [Quick Reference](docs/METRICS_QUICK_REFERENCE.md)
- [Installation Guide](INSTALLATION.md)
