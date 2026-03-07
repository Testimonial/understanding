---
description: Enforce quality gates on spec — exits with code 1 if any gate fails. Use in CI/CD or before proceeding to implementation.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Validate the current feature's spec.md against quality gates based on ISO 29148:2018 and IEEE 830-1998. This is a gate check — the spec must pass before proceeding to planning or implementation.

## Quality Gates

| Gate | Threshold | Standard |
|------|-----------|----------|
| Overall | >= 0.70 | ISO 29148:2018 |
| Structure | >= 0.70 | ISO 29148 S5.2.5 |
| Testability | >= 0.70 | ISO 29148 (mandatory) |
| Semantic | >= 0.60 | Lucassen 2017 |
| Cognitive | >= 0.60 | Sweller 1988 |
| Readability | >= 0.50 | Flesch 1948 |

## Execution Steps

### 1. Locate Spec

```bash
SPEC_PATH="${ARGUMENTS:-}"

if [ -z "$SPEC_PATH" ]; then
  SPECS_DIR="specs"
  if [ -d "$SPECS_DIR" ]; then
    LATEST=$(ls -d "$SPECS_DIR"/[0-9]*/ 2>/dev/null | sort -r | head -1)
    SPEC_PATH="${LATEST}spec.md"
  fi
fi

if [ ! -f "$SPEC_PATH" ]; then
  echo "No spec.md found. Provide a path: /speckit.understanding.validate path/to/spec.md"
  exit 1
fi
```

### 2. Run Validation

```bash
understanding "$SPEC_PATH" --validate
```

The `--validate` flag enforces quality gates and exits with code 1 if any gate fails.

### 3. Handle Results

**If all gates pass**: Confirm the spec is ready and suggest proceeding to `/speckit.plan` or `/speckit.tasks`.

**If gates fail**:
- List each failed gate with its score vs threshold
- For each failure, provide specific improvement suggestions
- Offer to help rewrite the worst-scoring requirements
- Do NOT suggest skipping validation or lowering thresholds

### 4. For CI/CD Integration

```bash
# JSON output for automated pipelines
understanding "$SPEC_PATH" --validate --json

# CSV for spreadsheet reporting
understanding "$SPEC_PATH" --validate --csv --output results.csv
```

## Operating Principles

- **Non-negotiable gates**: Quality gates are based on ISO/IEEE standards — they exist for a reason
- **Actionable feedback**: Every failure must come with a specific fix suggestion
- **No false comfort**: Don't minimize failures or suggest they're "close enough"
