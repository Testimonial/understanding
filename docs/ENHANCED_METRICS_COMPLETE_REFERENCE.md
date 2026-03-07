# Enhanced Metrics Complete Reference
## All 31 Deterministic Quality Metrics (18 Base + 13 Advanced)

**Version**: 3.4.0
**Last Updated**: March 2026
**Total Metrics**: 31
**All Ranges**: 0-1 (normalized)
**All Weights**: Sum to 1.0 (100%)

---

## Executive Summary

This reference documents all **31 scientifically-proven metrics** for evaluating requirement quality in Spec Kit. The metrics span 6 dimensions:

1. **Structure** (5 metrics, 30% weight) - How well-formed
2. **Testability** (3 metrics, 20% weight) - How verifiable
3. **Readability** (6 metrics, 15% weight) - How easy to read
4. **Cognitive** (7 metrics, 15% weight) - Mental effort required
5. **Semantic** (6 metrics, 10% weight) - Completeness of meaning
6. **Behavioral** (4 metrics, 10% weight) - How simulatable

**Key Enhancement**: Added 13 advanced metrics from the Behavioral Clarity Index (BCI) framework to provide comprehensive requirements assessment beyond text quality.

---

## Summary Table - All 31 Metrics

| # | Metric Name | Category | Weight | Final Weight % |
|---|-------------|----------|--------|----------------|
| **READABILITY METRICS (15% total)** |
| 1 | flesch_reading_ease | Readability | 0.250 x 0.15 | 3.75% |
| 2 | flesch_kincaid_grade | Readability | 0.150 x 0.15 | 2.25% |
| 3 | gunning_fog_index | Readability | 0.150 x 0.15 | 2.25% |
| 4 | smog_index | Readability | 0.150 x 0.15 | 2.25% |
| 5 | coleman_liau_index | Readability | 0.150 x 0.15 | 2.25% |
| 6 | automated_readability_index | Readability | 0.150 x 0.15 | 2.25% |
| **STRUCTURE METRICS (30% total)** |
| 7 | atomicity_score | Structure | 0.300 x 0.30 | 9.00% |
| 8 | completeness_score | Structure | 0.300 x 0.30 | 9.00% |
| 9 | passive_voice_ratio | Structure | 0.150 x 0.30 | 4.50% |
| 10 | ambiguous_pronoun_ratio | Structure | 0.100 x 0.30 | 3.00% |
| 11 | modal_strength | Structure | 0.150 x 0.30 | 4.50% |
| **COGNITIVE METRICS (15% total)** |
| 12 | sentence_length | Cognitive | 0.200 x 0.15 | 3.00% |
| 13 | syllable_complexity | Cognitive | 0.150 x 0.15 | 2.25% |
| 14 | concept_density | Cognitive | 0.150 x 0.15 | 2.25% |
| 15 | coordination_complexity | Cognitive | 0.150 x 0.15 | 2.25% |
| 16 | subordination_complexity | Cognitive | 0.150 x 0.15 | 2.25% |
| 17 | negation_load | Cognitive | 0.100 x 0.15 | 1.50% |
| 18 | conditional_load | Cognitive | 0.100 x 0.15 | 1.50% |
| **SEMANTIC METRICS (10% total)** |
| 19 | actor_presence | Semantic | 0.200 x 0.10 | 2.00% |
| 20 | action_presence | Semantic | 0.200 x 0.10 | 2.00% |
| 21 | object_presence | Semantic | 0.200 x 0.10 | 2.00% |
| 22 | outcome_presence | Semantic | 0.200 x 0.10 | 2.00% |
| 23 | trigger_presence | Semantic | 0.100 x 0.10 | 1.00% |
| 24 | scc_score | Semantic | 0.100 x 0.10 | 1.00% |
| **TESTABILITY METRICS (20% total)** |
| 25 | hard_constraint_ratio | Testability | 0.450 x 0.20 | 9.00% |
| 26 | constraint_density | Testability | 0.350 x 0.20 | 7.00% |
| 27 | negative_space_coverage | Testability | 0.200 x 0.20 | 4.00% |
| **BEHAVIORAL METRICS (10% total)** |
| 28 | scenario_decomposition_score | Behavioral | 0.250 x 0.10 | 2.50% |
| 29 | transition_completeness_score | Behavioral | 0.350 x 0.10 | 3.50% |
| 30 | branch_coverage_score | Behavioral | 0.200 x 0.10 | 2.00% |
| 31 | observability_score | Behavioral | 0.200 x 0.10 | 2.00% |

**Total**: All weights sum to 100.00%

---

## Category 1: READABILITY (15% weight)

### Scientific Foundation
All readability formulas validated against peer-reviewed research from 1948-1975.

### 1. Flesch Reading Ease (FRE)
- **Raw Formula**: `206.835 - 1.015 × (words/sentences) - 84.6 × (syllables/words)`
- **Raw Range**: 0-100 (higher = easier)
- **Ideal Value**: 65.0 (8th-9th grade level)
- **Normalization**: `score = 1.0 - |FRE - 65| / 100`
- **Weight**: 3.75% (highest in readability)
- **Research**: Flesch (1948), *Journal of Applied Psychology*

**Example**:
```
FRE = 70  → score = 1.0 - |70-65|/100 = 0.95
FRE = 45  → score = 1.0 - |45-65|/100 = 0.80
```

### 2-6. Other Readability Metrics
See `NORMALIZED_METRICS_COMPLETE_REFERENCE.md` for detailed formulas for:
- Flesch-Kincaid Grade Level (target: grade 10)
- Gunning Fog Index (target: 12)
- SMOG Index (target: 12)
- Coleman-Liau Index (target: grade 10)
- Automated Readability Index (target: grade 10)

---

## Category 2: STRUCTURE (30% weight)

### 7. Atomicity Score ⭐
- **Definition**: % of requirements expressing single testable behavior
- **Raw Range**: 0-1
- **Ideal Value**: 1.0 (100% atomic)
- **Normalization**: Direct (already 0-1)
- **Weight**: 9.00% (HIGHEST INDIVIDUAL METRIC, tied with completeness and hard_constraint_ratio)
- **Formula**: `atomic_requirements / total_requirements`
- **Research**: IEEE 830-1998 §4.4.5

**Why Critical**: Atomic requirements enable independent testing, effort estimation, and traceability.

**Example**:
```
❌ Compound: "System must validate input and store data"
✅ Atomic: "System must validate input format"
✅ Atomic: "System must store validated input"
```

### 8. Completeness Score ⭐
- **Definition**: % with complete actor-action-object pattern
- **Weight**: 9.00% (HIGHEST INDIVIDUAL METRIC, tied with atomicity and hard_constraint_ratio)
- **Formula**: `complete_patterns / total_requirements`
- **Research**: Lucassen et al. (2017) - Visual Narrator

**Pattern**: `[Actor] [Action Verb] [Object]`

**Example**:
```
✅ Complete: "User can delete their account"
   Actor: User, Action: delete, Object: account
❌ Incomplete: "Account deletion should be available"
   Missing clear actor
```

### 9-11. Other Structure Metrics
See `NORMALIZED_METRICS_COMPLETE_REFERENCE.md` for:
- Passive Voice Ratio (target: <20%)
- Ambiguous Pronoun Ratio (target: <10%)
- Modal Strength (target: strong modals MUST/SHALL)

---

## Category 3: COGNITIVE (15% weight)

### 12-18. Cognitive Complexity Metrics
See `NORMALIZED_METRICS_COMPLETE_REFERENCE.md` for detailed formulas.

**Summary**:
- **Sentence Length**: Target 20 words (weight: 3.00%)
- **Syllable Complexity**: Target 1.5 syllables/word
- **Concept Density**: Target 20% unique concepts
- **Coordination**: Minimize and/or/but
- **Subordination**: Minimize if/when/because
- **Negation**: Minimize not/never
- **Conditionals**: Target <10%

---

## Category 4: SEMANTIC (10% weight)

**Purpose**: Validates semantic completeness of requirements
**Research**: Visual Narrator (Lucassen 2017), Semantic Role Labeling (Gildea 2002)

### 19. Actor Presence
- **Definition**: % requirements with identified actor (who performs action)
- **Ideal Value**: 1.0 (100% have actors)
- **Weight**: 2.00%
- **Detection**: Regex patterns + optional spaCy NLP

**Detected Actors**:
- Explicit: user, admin, system, customer, application
- Subject extraction: "The system shall..."

**Example**:
```
✅ Has actor: "User must provide email address"
❌ Missing: "Email address is required"
```

### 20. Action Presence
- **Definition**: % requirements with identified action verb (what happens)
- **Ideal Value**: 1.0
- **Weight**: 2.00%

**Common Action Verbs**: validate, create, update, delete, display, send, store, retrieve, process

**Example**:
```
✅ Has action: "System validates email format"
❌ Missing: "Email format must be correct"
```

### 21. Object Presence
- **Definition**: % requirements with identified object (what is acted upon)
- **Ideal Value**: 1.0
- **Weight**: 2.00%

**Detected Objects**: data, file, message, user, account, input, output

**Example**:
```
✅ Has object: "System stores user profile"
❌ Missing: "Storage must occur"
```

### 22. Outcome Presence
- **Definition**: % requirements with identified outcome/result
- **Ideal Value**: 1.0
- **Weight**: 2.00%

**Outcome Patterns**:
- "returns status code"
- "displays error message"
- "sends notification"
- "becomes active"

**Example**:
```
✅ Has outcome: "System validates input and returns HTTP 200"
❌ Missing: "System validates input"
```

### 23. Trigger Presence
- **Definition**: % requirements with conditional/event trigger
- **Ideal Value**: 0.7 (not all requirements need triggers)
- **Weight**: 1.00%

**Trigger Keywords**: if, when, unless, given, after, before, on

**Example**:
```
✅ Has trigger: "When user clicks submit, system validates form"
❌ Missing: "System validates form"
```

### 24. SCC Score (Semantic Category Coverage)
- **Definition**: Composite semantic completeness score
- **Formula**: `(pA + pV + pO + pR + 0.7×pT) / 4.7`
  - pA = actor presence
  - pV = action (verb) presence
  - pO = object presence
  - pR = outcome (result) presence
  - pT = trigger presence
- **Weight**: 1.00%
- **Research**: BCI Framework

---

## Category 5: TESTABILITY (20% weight)

**Purpose**: Measures precision and verifiability of constraints
**Research**: IEEE 830-1998 §4.3.7, Ambriola & Gervasi (2006) CIRCE

### 25. Hard Constraint Ratio
- **Definition**: % of constraints that are quantifiable/testable
- **Ideal Value**: 1.0 (all constraints testable)
- **Weight**: 9.00%
- **Formula**: `hard_constraints / (hard_constraints + soft_constraints)`

**Hard Constraints** (testable):
- Numeric with units: "< 200ms", "within 5 seconds"
- Thresholds: "at least 10", "maximum 100"
- Enums: HTTP 200, status: active|inactive|pending

**Soft Constraints** (subjective):
- "fast", "user-friendly", "scalable", "robust"

**Example**:
```
✅ Hard: "System responds within 200ms for 95% of requests"
❌ Soft: "System must be fast and responsive"
```

### 26. Constraint Density
- **Definition**: Constraints per requirement (saturating exponential)
- **Formula**: `1 - e^(-density)` where density = constraints/requirements
- **Ideal Value**: 0.85 (saturation ~2 constraints/req)
- **Weight**: 7.00%

**Interpretation**:
- 0 constraints: score = 0.00 (too vague)
- 1 constraint/req: score = 0.63
- 2 constraints/req: score = 0.86 (ideal)
- 3+ constraints/req: score → 0.95 (saturating)

### 27. Negative Space Coverage
- **Definition**: Explicit boundary/exclusion statements
- **Formula**: `1 - e^(-negative_ratio)` where ratio = negatives/requirements
- **Ideal Value**: 0.63 (saturation)
- **Weight**: 4.00%

**Detected Patterns**:
- "must not", "shall not", "cannot", "prohibited"
- "out of scope", "excludes", "never"

**Example**:
```
✅ Explicit boundary: "System must not store credit card numbers"
❌ Missing: Implicit assumption (security risk)
```

---

## Category 6: BEHAVIORAL (10% weight)

**Purpose**: Assesses whether requirements describe testable state machines
**Research**: Harel (2005) Statecharts, Voas & Miller (1995) PIE Model

### 28. Scenario Decomposition Score
- **Definition**: Presence of conditional structures (IF/WHEN/UNLESS)
- **Formula**: `1 - e^(-conditional_ratio)`
- **Ideal Value**: 0.85 (saturation)
- **Weight**: 2.50%

**Why Important**: Conditional requirements enable scenario-based testing and state modeling.

**Example**:
```
✅ Conditional: "IF email is invalid, THEN display error"
✅ Event-driven: "WHEN user clicks submit, validate form"
❌ Missing: "Email must be validated"
```

### 29. Transition Completeness Score
- **Definition**: % of complete guard→action→outcome transitions
- **Ideal Value**: 1.0 (all transitions complete)
- **Weight**: 3.50%
- **Formula**: `complete_transitions / total_transitions`

**Transition Pattern**:
- **Guard**: Condition/trigger (IF/WHEN)
- **Action**: What happens (verb)
- **Outcome**: Result (observable state change)

**Example**:
```
✅ Complete: "WHEN user submits form, system validates data and returns status code"
   Guard: user submits form
   Action: validates data
   Outcome: returns status code

❌ Incomplete: "WHEN user submits form, system validates"
   Missing observable outcome
```

### 30. Branch Coverage Score
- **Definition**: Decision branches and error paths
- **Formula**: `min((log(1+branches) + 0.5×log(1+errors)) / target, 1.0)`
- **Target**: log(7) + 0.5×log(4) ≈ 2.60
- **Weight**: 2.00%

**Why Important**: Identifies requirements coverage of happy paths and error scenarios.

**Example**:
```
✅ Good coverage:
   - IF valid → success path
   - IF invalid → error path
   - IF timeout → retry path
   (3 branches, 2 error paths)
```

### 31. Observability Score
- **Definition**: % requirements with observable/verifiable outcomes
- **Ideal Value**: 1.0
- **Weight**: 2.00%

**Observable Outcomes**:
- Display/UI: display, show, render
- Output: return, emit, send, notify
- Storage: store, save, persist, log
- State: becomes active, transitions to

**Example**:
```
✅ Observable: "System displays confirmation message"
✅ Observable: "Database stores transaction with timestamp"
❌ Not observable: "System processes request"
```

---

## Weighted Average Formula

```
Overall Score = Σ(metric_score × metric_weight)

where:
  metric_weight = within_category_weight × category_weight

Example (atomicity_score):
  category_weight = 0.30 (structure)
  within_category_weight = 0.30 (30% of structure)
  final_weight = 0.30 x 0.30 = 0.090 (9.0%)
```

### Category Breakdown

```
Readability (15%):
  6 metrics x individual weights = 0.0375 + 0.0225x5 = 0.1500

Structure (30%):
  5 metrics x weights = 0.09 + 0.09 + 0.045 + 0.03 + 0.045 = 0.3000

Cognitive (15%):
  7 metrics x weights = 0.03 + 0.0225x4 + 0.015x2 = 0.1500

Semantic (10%):
  6 metrics x weights = 0.02x4 + 0.01x2 = 0.1000

Testability (20%):
  3 metrics x weights = 0.09 + 0.07 + 0.04 = 0.2000

Behavioral (10%):
  4 metrics x weights = 0.025 + 0.035 + 0.02x2 = 0.1000

Total: 0.15 + 0.30 + 0.15 + 0.10 + 0.20 + 0.10 = 1.0000
```

---

## Quality Score Interpretation

### Overall Score Ranges

| Score | Level | Interpretation |
|-------|-------|----------------|
| 0.90-1.00 | **Excellent** | Production-ready, all dimensions strong |
| 0.80-0.89 | **Very Good** | Minor improvements recommended |
| 0.70-0.79 | **Good** | Meets quality gates, ready for planning |
| 0.60-0.69 | **Fair** | Improvements needed before planning |
| 0.50-0.59 | **Poor** | Significant revision required |
| 0.00-0.49 | **Very Poor** | Major rewrite needed |

### Quality Gates (Constitutional Requirements)

From `memory/constitution.md` Principle I (NON-NEGOTIABLE):

- **Overall Score**: >= 0.70
- **Structure Score**: >= 0.70
- **Testability Score**: >= 0.70
- **Semantic Score**: >= 0.60
- **Cognitive Score**: >= 0.60
- **Readability Score**: >= 0.50
- **Behavioral**: no gate

Specs below these thresholds must be revised before planning.

---

## Complete Example Calculation

### Input Requirements

```
FR-001: System must validate email format before saving to database.
FR-002: When user clicks submit with invalid email, system displays error message "Invalid email format" and returns HTTP 400.
FR-003: System must store validated user data within 200ms.
FR-004: Users must be able to update their profile information.
FR-005: System must not allow access to deleted accounts.
```

### Calculated Scores (Abbreviated)

| Metric | Score | Weight | Contribution |
|--------|-------|--------|--------------|
| flesch_reading_ease | 0.94 | 0.0375 | 0.0353 |
| atomicity_score | 1.00 | 0.0900 | 0.0900 |
| completeness_score | 1.00 | 0.0900 | 0.0900 |
| actor_presence | 1.00 | 0.0200 | 0.0200 |
| action_presence | 1.00 | 0.0200 | 0.0200 |
| hard_constraint_ratio | 0.80 | 0.0900 | 0.0720 |
| transition_completeness | 1.00 | 0.0350 | 0.0350 |
| ... (all 31 metrics) | ... | ... | ... |

### Summary

```
Overall Score: 0.88 (88%) - Very Good
└─ Readability:   0.90 (90%)
└─ Structure:     1.00 (100%)
└─ Cognitive:     0.73 (73%)
└─ Semantic:      0.92 (92%)
└─ Testability:   0.78 (78%)
└─ Behavioral:    0.85 (85%)

Quality Level: Very Good (0.80-0.89)
Quality Gates: All passed (overall >=0.70, structure >=0.70, testability >=0.70, semantic >=0.60, cognitive >=0.60, readability >=0.50)
```

---

## Highest Impact Metrics (Top 10)

Metrics that contribute most to overall score:

1. **atomicity_score** - 9.00%
2. **completeness_score** - 9.00%
3. **hard_constraint_ratio** - 9.00%
4. **constraint_density** - 7.00%
5. **passive_voice_ratio** - 4.50%
6. **modal_strength** - 4.50%
7. **negative_space_coverage** - 4.00%
8. **flesch_reading_ease** - 3.75%
9. **transition_completeness_score** - 3.50%
10. **sentence_length** - 3.00%

**Focus areas**: If improving scores, prioritize atomicity, completeness, and hard constraints (combined 27% of total).

---

## Implementation

### Python API

```python
from understanding.enhanced_metrics import analyze_with_enhanced_metrics

# Analyze with all 31 metrics
result = analyze_with_enhanced_metrics(requirements_text, use_spacy=True)

overall = result["enhanced_metrics"]["overall_weighted_average"]
categories = result["enhanced_metrics"]["category_averages"]

print(f"Overall: {overall:.4f} ({overall*100:.1f}%)")
for cat, score in sorted(categories.items()):
    print(f"  {cat.capitalize()}: {score:.4f}")

# Check quality gates
if (overall >= 0.70 and categories["structure"] >= 0.70
    and categories["testability"] >= 0.70 and categories["semantic"] >= 0.60
    and categories["cognitive"] >= 0.60 and categories["readability"] >= 0.50):
    print("Quality gates passed")
else:
    print("Quality gates failed")
```

### CLI Usage

```bash
# Analyze with enhanced metrics (default uses base 18)
understanding metrics-scan --spec specs/001-feature/spec.md --enhanced

# Batch analysis
understanding metrics-scan --all --enhanced

# JSON output for CI/CD
understanding metrics-scan --spec specs/001-feature/spec.md --enhanced --json
```

---

## Base vs Enhanced Metrics

### When to Use Base 18 Metrics

- **Quick validation**: Fast feedback during spec writing
- **Text quality only**: Focus on readability and structure
- **No dependencies**: Works without spaCy or NLP libraries

### When to Use Enhanced 31 Metrics

- **Comprehensive assessment**: Full requirements quality evaluation
- **Implementation planning**: Before committing to development
- **Quality gates**: Enforcing constitutional compliance
- **Scientific rigor**: Research-backed validation

### Performance Comparison

| Metric Set | Analysis Time | Accuracy | Dependencies |
|------------|---------------|----------|--------------|
| Base (18) | ~50ms | High | None |
| Enhanced (31) | ~200ms | Very High | Optional spaCy |

---

## Scientific References

### Base Metrics (18)
1. Flesch, R. (1948). *Journal of Applied Psychology*
2. Kincaid, J.P., et al. (1975). "Derivation of new readability formulas"
3. Gunning, R. (1952). "The Technique of Clear Writing"
4. McLaughlin, G.H. (1969). "SMOG Grading"
5. Coleman & Liau (1975). "Computer Readability Formula"
6. IEEE 830-1998. "Software Requirements Specifications"
7. Sweller, J. (1988). "Cognitive load theory"

### Enhanced Metrics (13 new)
8. **Lucassen, G., et al. (2017)**. "Visual Narrator: Requirements engineering using user story quality." *Requirements Engineering*, 22(3), 339-358.
   - **Citations**: 421
   - **Impact**: Semantic role extraction (actor, action, object)

9. **Gildea, D., & Jurafsky, D. (2002)**. "Automatic labeling of semantic roles." *Computational Linguistics*, 28(3), 245-288.
   - **Citations**: 2,891
   - **Impact**: Foundation for semantic role labeling

10. **Ambriola, V., & Gervasi, V. (2006)**. "On the systematic analysis of natural language requirements with CIRCE." *Automated Software Engineering*, 13(1), 107-167.
    - **Citations**: 337
    - **Impact**: Constraint extraction and testability

11. **Harel, D., et al. (2005)**. "From LSCs to Statecharts." *Software & Systems Modeling*, 4(3), 235-247.
    - **Citations**: 156
    - **Impact**: Behavioral modeling from scenarios

12. **Voas, J.M., & Miller, K.W. (1995)**. "Software testability: The new verification." *IEEE Software*, 12(3), 17-28.
    - **Citations**: 678
    - **Impact**: PIE model (propagation, infection, execution)

**Total Research Citations**: 24 peer-reviewed papers, 5,000+ citations

---

## Migration Guide

### From Base 18 to Enhanced 31

**Code changes**:
```python
# Before (base 18)
from understanding.normalized_metrics import analyze_with_normalized_metrics
result = analyze_with_normalized_metrics(text)

# After (enhanced 31)
from understanding.enhanced_metrics import analyze_with_enhanced_metrics
result = analyze_with_enhanced_metrics(text, use_spacy=True)

# Access scores the same way
overall = result["enhanced_metrics"]["overall_weighted_average"]
categories = result["enhanced_metrics"]["category_averages"]
```

**Breaking changes**: None - base metrics still available via `normalized_metrics.py`

---

## Troubleshooting

### Low Semantic Scores

**Issue**: Semantic category score < 0.60

**Common causes**:
- Missing actors: "Email must be validated" → "System must validate email"
- Missing outcomes: "System processes data" → "System processes data and returns status"
- Vague actions: "Data handling occurs" → "System stores validated data"

**Fix**:
```
Before: "Password reset is available to users"
After: "User can request password reset, system sends reset link via email, user receives link within 60 seconds"
  ✓ Actor: User, System
  ✓ Action: request, sends, receives
  ✓ Object: password reset, link, email
  ✓ Outcome: receives within 60 seconds
```

### Low Testability Scores

**Issue**: Testability category score < 0.60

**Common causes**:
- Soft constraints: "fast", "user-friendly", "scalable"
- Missing boundaries: No "must not" statements
- Vague quantities: "many", "few", "some"

**Fix**:
```
Before: "System must be fast and handle many users"
After: "System must respond within 200ms for 95% of requests under 1000 concurrent users. System must not process requests from IP addresses on the blocklist."
  ✓ Hard constraint: 200ms, 95%, 1000 users
  ✓ Negative space: must not process blocklist
```

### Low Behavioral Scores

**Issue**: Behavioral category score < 0.60

**Common causes**:
- No conditionals: All requirements declarative
- Incomplete transitions: Missing guard or outcome
- No error paths: Only happy path described

**Fix**:
```
Before: "System stores user data"
After: "WHEN user submits form with valid data, system stores data in database and returns HTTP 200. IF data is invalid, system returns HTTP 400 with error details."
  ✓ Conditionals: WHEN, IF
  ✓ Complete transitions: guard→action→outcome
  ✓ Error paths: invalid data → 400
```

---

## Quick Reference Card

### Category Weights
- Structure: 30% | Testability: 20% | Readability: 15%
- Cognitive: 15% | Semantic: 10% | Behavioral: 10%

### Top 3 Metrics by Weight
1. Atomicity: 9.00% | 2. Completeness: 9.00% | 3. Hard Constraint Ratio: 9.00%

### Quality Gates
- Overall >= 0.70 | Structure >= 0.70 | Testability >= 0.70
- Semantic >= 0.60 | Cognitive >= 0.60 | Readability >= 0.50

### Score Interpretation
- Excellent: ≥0.90 | Very Good: 0.80-0.89 | Good: 0.70-0.79
- Fair: 0.60-0.69 | Poor: 0.50-0.59 | Very Poor: <0.50

---

## Energy Metrics (Optional Overlay)

Energy metrics are a separate overlay activated with `--energy`. They use token-level perplexity from a local language model (SmolLM2-135M) to detect ambiguity that pattern matching cannot catch.

### How They Relate to the 31 Metrics

The 31 deterministic metrics are a rule-based inspector checking structure, readability, and testability. Energy metrics are a second pair of eyes — a language model reading your requirements and flagging parts that feel ambiguous, even when all rules pass. Energy metrics are NOT part of the 31-metric score or quality gates.

### 5 Energy Metrics

| Metric | Score Range | What It Measures |
|--------|------------|-----------------|
| Mean Energy | 0-1 | Overall plausibility — how well text fits standard language patterns |
| Max Energy | 0-1 | Localized ambiguity — the single most surprising token |
| Dispersion | 0-1 | Uniformity — whether difficulty is spread evenly or concentrated |
| Anchor Ratio | 0-1 | Clarity — percentage of well-predicted, easy tokens |
| Tail Ratio | 0-1 | Ambiguity — percentage of highly surprising tokens |

Plus a composite score (weighted average) and hotspot tokens (top 5 most ambiguous tokens).

### Installation

```bash
pip install "understanding[energy]"
# Or with uv
uv tool install git+https://github.com/Testimonial/understanding.git \
  --with "transformers>=4.30.0" --with "torch>=2.0.0"
```

### Usage

```bash
understanding scan spec.md --energy
```

### Scientific Foundation

- Hinton (1985): Boltzmann Machines — energy as compatibility score
- Friston (2010): Free Energy Principle — brain minimizes surprise
- Gladstone et al. (2025): Energy-Based Transformers — token-level energy

---

**For detailed formulas on base 18 metrics**, see `NORMALIZED_METRICS_COMPLETE_REFERENCE.md`
**For scientific validation**, see `SCIENTIFIC_VALIDATION_REPORT.md`
**For implementation details**, see `src/understanding/enhanced_metrics.py`
