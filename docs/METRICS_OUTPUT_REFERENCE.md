# Metrics Output Reference

## What You Get from Validation

When you run `understanding metrics-scan`, you receive a comprehensive JSON/dictionary output with **summary metrics** and **detailed per-metric scores**.

---

## Summary Metrics (Top-Level)

These are the **key values** you use for quality gates and overall assessment.

### 1. `overall_weighted_average` (float, 0-1)
**The main score** - weighted average of all metrics.

```python
overall_weighted_average: 0.7836  # 78.36% quality
```

**Interpretation**:
- `>=0.90`: Excellent (production-ready)
- `>=0.80`: Very Good
- `>=0.70`: Good (meets quality gates)
- `>=0.60`: Fair (improvements needed)
- `<0.60`: Poor (revision required)

**Use this for**: Primary quality gate enforcement

---

### 2. `category_averages` (dict)
Weighted average score for each of the 6 categories.

```python
category_averages: {
  "readability": 0.8718,    # 87.18%
  "structure": 0.8000,      # 80.00%
  "cognitive": 0.7111,      # 71.11%
  "semantic": 0.8879,       # 88.79%
  "testability": 0.6712,    # 67.12%
  "behavioral": 0.5978      # 59.78%
}
```

**Use this for**:
- Identifying weak areas (lowest scores)
- Enforcing category-specific gates
- Prioritizing improvements

**Constitutional Quality Gates**:
- `overall_weighted_average >= 0.70`
- `category_averages["structure"] >= 0.70`
- `category_averages["testability"] >= 0.70`
- `category_averages["semantic"] >= 0.60`
- `category_averages["cognitive"] >= 0.60`
- `category_averages["readability"] >= 0.50`

---

### 3. `metric_count` (dict) - Enhanced metrics only
Number of metrics per category (diagnostic info).

```python
metric_count: {
  "readability": 6,
  "structure": 5,
  "cognitive": 7,
  "semantic": 6,
  "testability": 3,
  "behavioral": 4,
  "total": 31
}
```

---

## Detailed Metrics (Per-Metric Scores)

### `scores` (list of dicts)
Array of all individual metric results.

Each score object contains:

```python
{
  "name": "atomicity_score",           # Metric identifier
  "score": 0.6667,                     # Normalized score (0-1)
  "weight": 0.0900,                    # Weight in overall (9.0%)
  "weighted_score": 0.0600,            # Contribution to overall
  "category": "structure",             # Category name
  "raw_value": 0.6667,                 # Original raw value
  "ideal_value": 1.0,                  # Target/ideal value
  "description": "Single testable statement per requirement"
}
```

### Field Definitions

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `name` | string | - | Unique metric identifier (snake_case) |
| `score` | float | 0-1 | Normalized score (0=worst, 1=best) |
| `weight` | float | 0-1 | Contribution weight to overall score |
| `weighted_score` | float | 0-1 | `score × weight` (actual contribution) |
| `category` | string | - | One of: readability, structure, cognitive, semantic, testability, behavioral |
| `raw_value` | float | varies | Original metric value before normalization |
| `ideal_value` | float | varies | Target value for this metric |
| `description` | string | - | Human-readable explanation |

---

## Complete Output Structure

### Base 18 Metrics Output

```python
{
  "normalized_metrics": {
    "overall_weighted_average": 0.7836,
    "category_averages": {
      "readability": 0.8718,
      "structure": 0.8000,
      "cognitive": 0.7111
    },
    "scores": [
      {
        "name": "flesch_reading_ease",
        "score": 0.9965,
        "weight": 0.0375,
        "weighted_score": 0.0374,
        "category": "readability",
        "raw_value": 65.35,
        "ideal_value": 65.0,
        "description": "Overall readability (higher = easier)"
      },
      # ... 17 more metrics
    ]
  }
}
```

### Enhanced 31 Metrics Output

```python
{
  "base_metrics": {
    # Same structure as base 18 output above
  },
  "enhanced_metrics": {
    "overall_weighted_average": 0.7836,
    "category_averages": {
      "readability": 0.8718,
      "structure": 0.8000,
      "cognitive": 0.7111,
      "semantic": 0.8879,      # NEW
      "testability": 0.6712,   # NEW
      "behavioral": 0.5978     # NEW
    },
    "scores": [
      # All 31 metric objects (18 base + 13 new)
    ]
  },
  "metric_count": {
    "readability": 6,
    "structure": 5,
    "cognitive": 7,
    "semantic": 6,
    "testability": 3,
    "behavioral": 4,
    "total": 31
  }
}
```

---

## Usage Examples

### Python API

#### Access Summary Metrics

```python
from specify_cli.enhanced_metrics import analyze_with_enhanced_metrics

result = analyze_with_enhanced_metrics(requirements_text)
enhanced = result["enhanced_metrics"]

# Get overall score
overall = enhanced["overall_weighted_average"]
print(f"Overall Quality: {overall:.2%}")  # "Overall Quality: 78.36%"

# Get category scores
categories = enhanced["category_averages"]
print(f"Readability: {categories['readability']:.2%}")
print(f"Semantic: {categories['semantic']:.2%}")
print(f"Testability: {categories['testability']:.2%}")

# Check quality gates
if (overall >= 0.70 and categories["structure"] >= 0.70
    and categories["testability"] >= 0.70 and categories["semantic"] >= 0.60
    and categories["cognitive"] >= 0.60 and categories["readability"] >= 0.50):
    print("Quality gates passed")
else:
    print("Quality gates failed")
```

#### Access Individual Metrics

```python
# Get all scores
all_scores = enhanced["scores"]

# Find specific metric
atomicity = next(s for s in all_scores if s["name"] == "atomicity_score")
print(f"Atomicity: {atomicity['score']:.2%} (weight: {atomicity['weight']:.1%})")

# Find lowest scoring metrics
sorted_by_score = sorted(all_scores, key=lambda x: x["score"])
print("Bottom 5 metrics:")
for metric in sorted_by_score[:5]:
    print(f"  {metric['name']}: {metric['score']:.2%}")

# Find highest impact metrics (by weighted_score)
sorted_by_impact = sorted(all_scores, key=lambda x: x["weighted_score"], reverse=True)
print("Top 5 by impact:")
for metric in sorted_by_impact[:5]:
    print(f"  {metric['name']}: {metric['weighted_score']:.4f} (weight: {metric['weight']:.1%})")
```

#### Filter by Category

```python
# Get all semantic metrics
semantic_metrics = [s for s in all_scores if s["category"] == "semantic"]
print(f"Semantic metrics: {len(semantic_metrics)}")
for m in semantic_metrics:
    print(f"  {m['name']}: {m['score']:.2%}")

# Calculate custom category score
def category_score(scores, category_name):
    cat_scores = [s for s in scores if s["category"] == category_name]
    total_weighted = sum(s["weighted_score"] for s in cat_scores)
    total_weight = sum(s["weight"] for s in cat_scores)
    return total_weighted / total_weight if total_weight > 0 else 0.0

readability_score = category_score(all_scores, "readability")
print(f"Readability: {readability_score:.2%}")
```

---

### CLI Output

#### JSON Format

```bash
understanding metrics-scan --spec specs/001-feature/spec.md --enhanced --json > output.json
```

```json
{
  "enhanced_metrics": {
    "overall_weighted_average": 0.7836,
    "category_averages": {
      "readability": 0.8718,
      "structure": 0.8000,
      "cognitive": 0.7111,
      "semantic": 0.8879,
      "testability": 0.6712,
      "behavioral": 0.5978
    },
    "scores": [...]
  }
}
```

#### Human-Readable Format (default)

```bash
understanding metrics-scan --spec specs/001-feature/spec.md --enhanced
```

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
  PASS Overall >=0.70 (0.78)
  PASS Structure >=0.70 (0.80)
  FAIL Testability >=0.70 (0.67)
  PASS Semantic >=0.60 (0.89)
  PASS Cognitive >=0.60 (0.71)
  PASS Readability >=0.50 (0.87)

Top Issues:
  1. Behavioral (0.60) - Add conditional structures
  2. Testability (0.67) - Add hard constraints
  3. Cognitive (0.71) - Simplify sentences
```

---

## Quick Decision Guide

### Which Summary Metric Should I Use?

| Use Case | Metric | Threshold |
|----------|--------|-----------|
| **Primary quality gate** | `overall_weighted_average` | >=0.70 |
| **Structure quality** | `category_averages["structure"]` | >=0.70 |
| **Testability** | `category_averages["testability"]` | >=0.70 |
| **Semantic completeness** | `category_averages["semantic"]` | >=0.60 |
| **Cognitive clarity** | `category_averages["cognitive"]` | >=0.60 |
| **Readability** | `category_averages["readability"]` | >=0.50 |
| **Find weakest area** | `min(category_averages.values())` | - |
| **Production readiness** | `overall_weighted_average` | >=0.80 |
| **Excellence benchmark** | `overall_weighted_average` | >=0.90 |

### What to Check First

1. **Check `overall_weighted_average`**
   - If >=0.70: Proceed
   - If <0.70: Check category_averages to find problem area

2. **Check `category_averages`** for lowest scores
   - Focus on categories <0.60 first
   - Then improve categories <0.70

3. **Check individual `scores`** in weak categories
   - Find metrics with `score <0.60`
   - Prioritize by `weight` (higher weight = more impact)

---

## Example Analysis Workflow

```python
from specify_cli.enhanced_metrics import analyze_with_enhanced_metrics

# Run analysis
result = analyze_with_enhanced_metrics(spec_text)
metrics = result["enhanced_metrics"]

# 1. Check overall
overall = metrics["overall_weighted_average"]
print(f"Overall: {overall:.2%}")

if overall < 0.70:
    print("WARN  Below quality gate (0.70)")

    # 2. Find weak categories
    categories = metrics["category_averages"]
    weak_cats = {k: v for k, v in categories.items() if v < 0.70}

    print(f"\nWeak categories ({len(weak_cats)}):")
    for cat, score in sorted(weak_cats.items(), key=lambda x: x[1]):
        print(f"  {cat}: {score:.2%}")

    # 3. Find problem metrics in weak categories
    all_scores = metrics["scores"]
    for cat_name in weak_cats:
        cat_metrics = [s for s in all_scores if s["category"] == cat_name]
        low_metrics = [m for m in cat_metrics if m["score"] < 0.60]

        if low_metrics:
            print(f"\n{cat_name.capitalize()} issues:")
            for m in sorted(low_metrics, key=lambda x: x["score"]):
                print(f"  - {m['name']}: {m['score']:.2%} (ideal: {m['ideal_value']})")
                print(f"    {m['description']}")
else:
    print("PASS Quality gates passed")
```

---

## Key Metric Names (Reference)

### Summary Metrics
- `overall_weighted_average` - Main quality score (0-1)
- `category_averages` - Dict with 6 category scores
  - `readability` (0-1)
  - `structure` (0-1)
  - `cognitive` (0-1)
  - `semantic` (0-1)
  - `testability` (0-1)
  - `behavioral` (0-1)

### Individual Metric Names (all in `scores` array)

**Readability (6)**:
- `flesch_reading_ease`
- `flesch_kincaid_grade`
- `gunning_fog_index`
- `smog_index`
- `coleman_liau_index`
- `automated_readability_index`

**Structure (5)**:
- `atomicity_score`
- `completeness_score`
- `passive_voice_ratio`
- `ambiguous_pronoun_ratio`
- `modal_strength`

**Cognitive (7)**:
- `sentence_length`
- `syllable_complexity`
- `concept_density`
- `coordination_complexity`
- `subordination_complexity`
- `negation_load`
- `conditional_load`

**Semantic (6)** - Enhanced only:
- `actor_presence`
- `action_presence`
- `object_presence`
- `outcome_presence`
- `trigger_presence`
- `scc_score`

**Testability (3)** - Enhanced only:
- `hard_constraint_ratio`
- `constraint_density`
- `negative_space_coverage`

**Behavioral (4)** - Enhanced only:
- `scenario_decomposition_score`
- `transition_completeness_score`
- `branch_coverage_score`
- `observability_score`

---

## Related Documentation

- **Formulas & Calculations**: [`ENHANCED_METRICS_COMPLETE_REFERENCE.md`](./ENHANCED_METRICS_COMPLETE_REFERENCE.md)
- **Quick Reference**: [`METRICS_QUICK_REFERENCE.md`](./METRICS_QUICK_REFERENCE.md)
- **Scientific Validation**: [`SCIENTIFIC_VALIDATION_REPORT.md`](./SCIENTIFIC_VALIDATION_REPORT.md)
