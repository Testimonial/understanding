# Quick Start Guide

Get started with Understanding in 5 minutes.

## 1. Install

```bash
uv tool install understanding
```

## 2. Verify Installation

```bash
understanding version
```

Expected output:
```
understanding version 3.4.0
31 scientifically-proven requirements quality metrics
```

## 3. Scan Your First Spec

```bash
# Auto-discover spec in current directory or specs/ folder
understanding scan

# Or provide explicit path
understanding scan path/to/spec.md
```

## 4. Interpret Results

```
Requirements Quality Metrics
============================

Overall Score: 0.78 (Good)

Category Scores:
  Readability:   0.87 (Very Good)  ← Easy to read
  Structure:     0.80 (Very Good)  ← Well-formed requirements
  Cognitive:     0.71 (Good)       ← Mental effort acceptable
  Semantic:      0.89 (Very Good)  ← Clear who/what/why
  Testability:   0.67 (Fair)       ← Could use more hard constraints
  Behavioral:    0.60 (Fair)       ← Add more conditionals

Quality Gates:
  ✓ Overall ≥0.70 (0.78)
  ✓ Structure ≥0.70 (0.80)
  ✗ Testability ≥0.70 (0.67)
  ✓ Semantic ≥0.60 (0.89)
  ✓ Cognitive ≥0.60 (0.71)
  ✓ Readability ≥0.50 (0.87)

Status: FAILED (1/6 gates failed) ❌
```

## 5. Enforce Quality Gates

```bash
# Auto-discover spec
understanding validate

# Or provide explicit path
understanding validate path/to/spec.md
```

Exits with code 1 if gates fail - perfect for CI/CD!

**Auto-discovery looks in:**
- `./spec.md` (current directory)
- `./specs/*/spec.md` (most recent in Spec Kit structure)

## Next Steps

- **[Full Usage Guide](USAGE_GUIDE.md)** - All commands and options
- **[Python API](README.md#-python-api)** - Use in your code
- **[Metrics Reference](docs/METRICS_QUICK_REFERENCE.md)** - Understand the metrics
- **[CI/CD Integration](USAGE_GUIDE.md#cicd-integration)** - Automate validation

## Common Issues

**Command not found**:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

**Need help**:
```bash
understanding --help
```

---

**That's it!** You're validating requirements quality in minutes.
