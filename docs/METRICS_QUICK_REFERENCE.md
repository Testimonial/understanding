# Metrics Quick Reference

## All 31 Metrics at a Glance

```
UNDERSTANDING QUALITY METRICS (31 Total)
|
+-- STRUCTURE (30% weight) - 5 metrics
|   +-- Atomicity Score (9.00%) HIGHEST
|   +-- Completeness Score (9.00%) HIGHEST
|   +-- Passive Voice Ratio (4.50%)
|   +-- Ambiguous Pronoun Ratio (3.00%)
|   +-- Modal Strength (4.50%)
|
+-- TESTABILITY (20% weight) - 3 metrics
|   +-- Hard Constraint Ratio (9.00%) HIGHEST
|   +-- Constraint Density (7.00%)
|   +-- Negative Space Coverage (4.00%)
|
+-- READABILITY (15% weight) - 6 metrics
|   +-- Flesch Reading Ease (3.75%)
|   +-- Flesch-Kincaid Grade (2.25%)
|   +-- Gunning Fog Index (2.25%)
|   +-- SMOG Index (2.25%)
|   +-- Coleman-Liau Index (2.25%)
|   +-- Automated Readability Index (2.25%)
|
+-- COGNITIVE (15% weight) - 7 metrics
|   +-- Sentence Length (3.00%)
|   +-- Syllable Complexity (2.25%)
|   +-- Concept Density (2.25%)
|   +-- Coordination Complexity (2.25%)
|   +-- Subordination Complexity (2.25%)
|   +-- Negation Load (1.50%)
|   +-- Conditional Load (1.50%)
|
+-- SEMANTIC (10% weight) - 6 metrics
|   +-- Actor Presence (2.00%)
|   +-- Action Presence (2.00%)
|   +-- Object Presence (2.00%)
|   +-- Outcome Presence (2.00%)
|   +-- Trigger Presence (1.00%)
|   +-- SCC Score (1.00%)
|
+-- BEHAVIORAL (10% weight) - 4 metrics
    +-- Scenario Decomposition (2.50%)
    +-- Transition Completeness (3.50%)
    +-- Branch Coverage (2.00%)
    +-- Observability Score (2.00%)
```

## Quality Gates

```
Constitutional Requirements (NON-NEGOTIABLE):
+-- Overall Score:      >=0.70 (Good)
+-- Structure Score:    >=0.70 (Good)
+-- Testability Score:  >=0.70 (Good)
+-- Semantic Score:     >=0.60 (Fair)
+-- Cognitive Score:    >=0.60 (Fair)
+-- Readability Score:  >=0.50 (Poor threshold)
+-- Behavioral:         no gate
```

## Score Interpretation

| Range | Level | Ready? |
|-------|-------|--------|
| 0.90-1.00 | **Excellent** | Production |
| 0.80-0.89 | **Very Good** | Production |
| 0.70-0.79 | **Good** | Planning |
| 0.60-0.69 | **Fair** | Improve first |
| 0.50-0.59 | **Poor** | Revise |
| 0.00-0.49 | **Very Poor** | Rewrite |

## Usage

### Base 18 Metrics (Default)
```bash
understanding metrics-scan --spec specs/001-feature/spec.md
```

### Enhanced 31 Metrics
```bash
understanding metrics-scan --spec specs/001-feature/spec.md --enhanced
```

### Batch Analysis
```bash
understanding metrics-scan --all --enhanced
```

### CI/CD Integration
```bash
understanding metrics-scan --all --threshold 0.70 --fail-below-threshold
```

## Energy Metrics (Experimental)

Activated with `--energy`. Uses a local language model to detect ambiguity.

| Metric | What It Measures |
|--------|-----------------|
| Mean Energy | Overall plausibility |
| Max Energy | Worst ambiguity hotspot |
| Dispersion | Difficulty uniformity |
| Anchor Ratio | % easy tokens |
| Tail Ratio | % hard tokens |

Separate overlay — not part of the 31-metric score.

```bash
understanding scan spec.md --energy
```

## Documentation

- **All 31 metrics**: [`ENHANCED_METRICS_COMPLETE_REFERENCE.md`](./ENHANCED_METRICS_COMPLETE_REFERENCE.md) (714 lines)
- **Base 18 metrics**: [`NORMALIZED_METRICS_COMPLETE_REFERENCE.md`](./NORMALIZED_METRICS_COMPLETE_REFERENCE.md) (370 lines)
- **Scientific validation**: [`SCIENTIFIC_VALIDATION_REPORT.md`](./SCIENTIFIC_VALIDATION_REPORT.md) (1400+ lines)
- **Comparison**: [`METRICS_COMPARISON_REPORT.md`](./METRICS_COMPARISON_REPORT.md)

## Scientific Foundation

**24 peer-reviewed papers**, 5,000+ citations:
- Flesch (1948), Kincaid (1975), Gunning (1952) - Readability
- Lucassen et al. (2017) - Visual Narrator (421 citations)
- Gildea & Jurafsky (2002) - Semantic Role Labeling (2,891 citations)
- Ambriola & Gervasi (2006) - CIRCE (337 citations)
- Harel et al. (2005) - Statecharts (156 citations)
- IEEE 830-1998, ISO 29148:2018 - Standards

## Quick Fixes

### Low Semantic Score (<0.60)
```diff
- Password reset is available to users
+ User can request password reset, system sends reset link via email
  + Actor: User, System
  + Action: request, sends
  + Object: password reset, link
```

### Low Testability Score (<0.60)
```diff
- System must be fast and handle many users
+ System must respond within 200ms for 95% of requests under 1000 concurrent users
  + Hard constraints: 200ms, 95%, 1000 users
```

### Low Behavioral Score (<0.60)
```diff
- System stores user data
+ WHEN user submits valid form, system stores data and returns HTTP 200. IF invalid, returns HTTP 400 with error details
  + Conditionals: WHEN, IF
  + Transitions: guard->action->outcome
  + Error paths: invalid -> 400
```

## Top 5 Metrics by Impact

1. **Atomicity Score** - 9.00% (Split compound requirements)
2. **Completeness Score** - 9.00% (Add actor-action-object)
3. **Hard Constraint Ratio** - 9.00% (Use quantifiable constraints)
4. **Constraint Density** - 7.00% (Add measurable bounds)
5. **Passive Voice Ratio** - 4.50% (Use active voice)

**Focus**: Atomicity + Completeness + Hard Constraints = 27% of total score
