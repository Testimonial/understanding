# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.4.0] - 2026-03-07

### Added
- **Energy Metrics** (`--energy` flag): Token-level perplexity analysis using a local language model (SmolLM2-135M) as a proxy for Hinton-style energy-based understanding
  - 5 new metrics: Mean Energy, Max Energy (hotspot), Dispersion, Anchor Ratio, Tail Ratio + Composite
  - Hotspot token detection: identifies the most ambiguous/surprising tokens in a requirement
  - Based on: Hinton (1985) Boltzmann Machines, Friston (2010) Free Energy Principle, Gladstone et al. (2025) Energy-Based Transformers
  - Optional dependency: `pip install understanding[energy]` (installs transformers + torch)
  - Model auto-downloads (~270MB) on first use, cached locally
- New optional dependency group: `[energy]` in pyproject.toml

### Fixed
- **`_has_object()` was nearly always true**: Previously returned True for any requirement with 3+ words. Now checks for content words after an action verb
- **`_has_actor()` matched "the" as an actor**: No longer returns True just because requirement starts with "the/a/an". Requires explicit actor keywords or a `the <noun> shall/must` pattern
- **`hard_constraint_ratio` defaulted to 0.5 with zero constraints**: Changed to 0.0 — specs with no quantifiable constraints should not score 50% on testability
- **Enum status words inflated hard constraint count**: Removed `active/inactive/pending/approved/rejected/completed`, `enabled/disabled`, `true/false`, `yes/no`, `read/write/execute` from hard constraint patterns — these are domain vocabulary, not quantifiable constraints
- **Action verb matching missed inflected forms**: `validates`, `creating`, `stored` etc. now match via compiled regex stem patterns instead of exact word list
- **`\bon\b` trigger pattern was too noisy**: Replaced with `\bupon\b` and `\bwhenever\b` in semantic_metrics.py — "based on", "click on", "depends on" no longer count as triggers
- **SCC denominator was hardcoded `4.7`**: Now computed dynamically as `4 + trigger_weight` to stay in sync if the trigger weight changes

### Changed
- Updated README category weights to match actual code: Structure 30%, Testability 20%, Semantic 10%, Cognitive 15%, Readability 15%, Behavioral 10%
- Updated all docs to use correct package name "understanding" (was "speckit-metrics-enhanced" in some files)
- Version bump: 3.3.0 -> 3.4.0

## [3.3.0] - 2026-02-04

### Added
- **EARS (Easy Approach to Requirements Syntax) Compliance Checking**: Validate requirements against industry-standard EARS patterns
  - 5 pattern types: Ubiquitous, Event-Driven (WHEN), State-Driven (WHILE), Unwanted Behavior (IF-THEN), Optional Feature (WHERE)
  - Pattern detection with confidence scoring (0-100%)
  - Compliance validation with issue identification
  - Suggestion engine for non-compliant requirements
  - Overall EARS score calculation for specifications
- **New CLI flag**: `--ears` for EARS compliance analysis
- **New module**: `ears_patterns.py` with `EARSPatternDetector` class
- **Per-requirement EARS analysis**: Shows pattern, confidence, issues, and suggestions for each requirement
- **Pattern distribution**: Summary of which EARS patterns are used across all requirements

### Enhanced
- CLI output: New "EARS Compliance Analysis" section
- Per-requirement display: Color-coded status (✓/✗), pattern type, confidence, issues, and improvement suggestions
- JSON export: EARS analysis data included when `--ears` flag used

### Research Foundation
Based on Mavin et al. (2009) "Easy Approach to Requirements Syntax (EARS)"
IEEE 17th International Requirements Engineering Conference
- Industry adoption: Rolls-Royce, Airbus, BAE Systems, Boeing
- Proven: 64% reduction in ambiguity, 50% fewer defects

### Usage
```bash
# Check EARS compliance
understanding scan spec.md --ears

# Per-requirement analysis with EARS
understanding scan spec.md --ears --per-req

# Combined with NLP
understanding scan spec.md --ears --nlp
```

### Documentation
- Added FORMAL_LANGUAGES_FOR_REQUIREMENTS.md with research-grounded analysis
- EARS patterns, industry usage, and effectiveness data
- Comparison of formal specification languages (Z, VDM, B-Method, TLA+, Alloy)

## [3.2.0] - 2026-02-04 🎨 PNG DIAGRAMS + CLI IMPROVEMENTS + CROSS-SPEC AGGREGATION

### Added
- **PNG/SVG/PDF Diagram Export**: Professional diagram generation using Graphviz
  - New CLI flag: `--png <output_file>` for diagram export
  - New CLI flag: `--png-format` for format selection (png, svg, pdf)
  - Color-coded nodes by entity type (blue=actors, green=actions, orange=objects, purple=systems, yellow=conditions, red=constraints)
  - Styled edges by relationship type (solid=performs/modifies, dashed=triggers)
  - Professional layout using Graphviz DOT engine
  - Optional dependency: `pip install understanding[diagram]`
  - System requirement: Graphviz must be installed (`brew install graphviz` on macOS)
- **Cross-Spec Entity Aggregation**: Unified entity analysis across multiple specifications
  - Single spec: Focused entity analysis (existing behavior)
  - Multiple specs: Automatic aggregation into unified view (NEW)
  - Entity deduplication: Same entities across specs merged by normalized form
  - Relationship consolidation: Cross-spec relationships detected and combined
  - Unified system diagram: One comprehensive diagram showing full system architecture
  - Spec source tracking: Track which entities come from which specs
- **Enhanced Entity Vocabulary (Tier 2)**: Expanded from ~60 to ~170+ patterns
  - ACTOR_PATTERNS: 10 → 30+ (added microservices, gateways, external systems, specialized services)
  - ACTION_VERBS: 50 → 90+ (added auth, encryption, routing, pub/sub, caching, resilience, monitoring)
  - OBJECT_PATTERNS: 25 → 50+ (added tokens, events, queues, metrics, infrastructure objects)
  - Better support for: Microservices architectures, event-driven systems, API gateways
- **New optional dependency group**: `[diagram]` for graphviz support
- **New optional dependency group**: `[all]` for both nlp + diagram

### Enhanced
- `entity_metrics.py`: Added `generate_graphviz_diagram()` and `export_png_diagram()` methods
- `entity_metrics.py`: Expanded entity vocabulary for comprehensive system analysis (Tier 2)
- CLI: PNG export integrated with entity extraction workflow
- CLI: Added `_aggregate_entity_analysis()` for cross-spec entity consolidation
- CLI: Enhanced `_print_entity_analysis()` to show cross-spec metadata
- Error handling: Clear messages when Graphviz not installed

### Improved (CLI Simplifications)
- **Auto-enable entities**: `--diagram` and `--png` now automatically enable `--entities`
  - Before: `understanding scan spec.md --entities --png diagram.png`
  - After: `understanding scan spec.md --png diagram.png` (simpler!)
- **Format inference**: PNG format auto-detected from file extension
  - Before: `understanding scan spec.md --entities --png diagram.svg --png-format svg`
  - After: `understanding scan spec.md --png diagram.svg` (format inferred from .svg)
- **Cross-spec analysis**: Automatic entity aggregation when scanning directories
  - Single spec: `understanding scan spec.md --entities` (focused analysis)
  - Multiple specs: `understanding scan specs/ --entities` (unified view - NEW!)
  - Before: Separate per-spec analyses, no big picture
  - After: One aggregated analysis showing full system architecture
- **Validation conflict**: Error if both `--json` and `--csv` specified (prevents confusion)
- **Test alias**: `--test` now an alias for `--validate` (backward compatible)
- **Clearer help text**: Updated flag descriptions to show auto-enabling behavior

### Usage Examples
```bash
# Cross-spec entity aggregation (NEW)
understanding scan specs/ --entities --nlp

# Generate unified system architecture diagram (NEW)
understanding scan specs/ --entities --nlp --png system-architecture.svg

# Single spec (focused analysis)
understanding scan spec.md --entities --nlp --png feature-diagram.png
```

### Documentation
- README: PNG diagram usage examples and installation instructions
- CHANGELOG: PNG diagram export release notes

### Testing
- Added 8 new tests for PNG generation (conditional on graphviz availability)
- Total tests: 49 (23 entity + 18 CLI + 8 PNG)

## [3.1.0] - 2026-02-04 🎯 ENTITY EXTRACTION

### Added
- **Entity Extraction**: Extract actors, actions, objects, and system components from requirements
  - Pattern-based extraction (basic mode): Regex patterns for actors/actions/objects
  - spaCy NLP extraction (enhanced mode): Dependency parsing and NER
  - Entity types: Actor, Action, Object, System, Condition, Constraint
  - Confidence scoring for extracted entities
- **Relationship Detection**: Identify relationships between entities
  - Actor→Action→Object chains
  - Trigger/condition relationships ("if X then Y")
  - Relationship types: performs, modifies, triggers
  - Automatic deduplication and filtering
- **Text-Based Diagrams**: Simple entity relationship visualization
  - ASCII-style diagrams showing entity relationships
  - Grouped by relationship type
  - Configurable detail level
- **CLI Flags**: New command-line options for entity analysis
  - `--entities`: Extract and display entities and relationships
  - `--diagram`: Generate text-based entity relationship diagram (requires --entities)
  - Works with `--nlp` for better extraction accuracy
- **JSON Export**: Entity data included in JSON output
  - Full entity details (text, type, normalized form, confidence)
  - Relationship data (source, relation, target)
  - Summary statistics (counts, unique entities)

### Enhanced
- `semantic_metrics.py`: Added `extract_entities_detailed()` method to expose entity data
- CLI output: New entity analysis section displayed after metrics
- JSON schema: Added "entity_analysis" key with entities, relationships, and summary

### Performance
- Pattern-based entity extraction: ~50ms overhead
- NLP entity extraction: ~200ms overhead (better accuracy)

### Documentation
- README: Added entity extraction usage examples and output samples
- CHANGELOG: Entity extraction release notes

### Added (Previous Unreleased)
- **NLP Enhancement (Optional)**: Added `--nlp` flag to enable spaCy-based semantic analysis
  - Better actor/action/object detection using dependency parsing
  - POS tagging for accurate verb extraction
  - Named entity recognition
  - Improves semantic scores by ~13% (58% → 71% in testing)
  - Requires: `pip install understanding[nlp] && python -m spacy download en_core_web_sm`
  - Default remains pattern-based (fast, no dependencies)
- **Detailed Installation Guide**: Comprehensive installation instructions in README
  - Three installation methods (uv tool, pip, editable)
  - Step-by-step NLP setup for both uv and pip
  - Troubleshooting section for common issues
  - Performance comparison table

### Documentation - Major Honesty Update
- **CRITICAL FIX**: Removed false claims about CIRCE/Ambriola & Gervasi
  - Our code does simple regex, NOT semantic modeling like CIRCE
  - CIRCE builds UML/ER models, FSMs, has Eclipse integration
  - We just count numbers and keywords - completely different
- **Transparency**: Added "Implementation Approach" section clearly stating:
  - Pattern-based analysis (regex, keywords)
  - Mathematical formulas (readability)
  - Statistical methods (cognitive load)
  - NOT NLP, NOT semantic parsing, NOT ML
- Removed all misleading research attributions
- Fixed quality gates documentation (Testability is ≥0.70, not ≥0.60)
- Added complete gate list: Overall, Structure, Testability, Semantic, Cognitive, Readability
- Removed broken GitHub links

## [3.0.0] - 2026-02-03 🎯 REBRANDING + SIMPLIFIED API

### Breaking Changes
- **Package renamed**: `speckit-metrics-enhanced` → `understanding`
- **CLI command**: `speckit-metrics` → `understanding`
- **Python package**: `speckit_metrics` → `understanding`
- **Repository**: Moved to https://github.com/Testimonial/understanding
- **CLI simplified**: Removed `validate` command - use `scan --validate` or `scan --test` instead

### Why "Understanding"?
This package measures **requirements understanding** and **cognitive load** - how easily humans can comprehend requirements. The new name reflects this core purpose and makes it clear this is a general-purpose tool, not tied to any specific framework.

### Simplified CLI
The `validate` command has been removed to simplify the API. All functionality is now available through the `scan` command:

```bash
# OLD: understanding validate spec.md
# NEW: understanding scan spec.md --validate

# NEW: Test mode with pass/fail status
understanding scan spec.md --test
```

### Migration Guide
```bash
# Uninstall old package
pip uninstall speckit-metrics-enhanced

# Install new package
pip install understanding

# Update imports in code
# OLD: from speckit_metrics import analyze_with_enhanced_metrics
# NEW: from understanding import analyze_with_enhanced_metrics

# Update CLI commands
# OLD: speckit-metrics scan spec.md
# NEW: understanding scan spec.md

# OLD: speckit-metrics validate spec.md
# NEW: understanding scan spec.md --validate
# OR:  understanding scan spec.md --test
```

## [2.0.0] - 2026-02-03 🎯 MAJOR RELEASE

### 🔬 Research-Backed Weight Rebalancing

**Breaking Change**: Metric weights updated based on ISO 29148:2018, IEEE 830-1998, ISO 25010:2023

#### Weight Changes
- **Testability: 5% → 20%** (4x increase) - ISO 29148 makes verifiability MANDATORY
- **Semantic: 5% → 10%** (2x increase) - Lucassen 2017: 40% fewer defects
- **Structure: 35% → 30%** (still highest) - ISO 29148 atomicity & completeness
- **Cognitive: 25% → 15%** (rebalanced) - Important but not mandatory
- **Readability: 25% → 15%** (rebalanced) - Important but not mandatory
- **Behavioral: 5% → 10%** (doubled) - Increased importance

#### New Quality Gates (6 total, up from 3)
- ✅ Overall ≥ 0.70 (unchanged)
- ✅ **Structure ≥ 0.70** (NEW) - ISO 29148 §5.2.5
- ✅ **Testability ≥ 0.70** (raised from 0.60) - ISO 29148 mandatory
- ✅ Semantic ≥ 0.60 (unchanged)
- ✅ **Cognitive ≥ 0.60** (NEW) - Sweller 1988
- ✅ **Readability ≥ 0.50** (NEW) - Flesch 1948

### Added
- **Comprehensive justification document** (docs/WEIGHTS_AND_GATES_JUSTIFICATION.md)
  - 24+ peer-reviewed research citations with DOIs
  - 3 international standards (ISO 29148, IEEE 830, ISO 25010)
  - Systematic literature reviews (2023-2024)
  - Impact analysis and comparison tables
- Quality gates constants (QUALITY_GATES) in CLI
- Helper function `_check_quality_gates()` for validation
- Research references in code comments
- Enhanced validation output showing all 6 gates with references

### Changed
- **BREAKING**: Overall scores will change due to weight rebalancing
- **BREAKING**: More specs may fail due to stricter gates (6 vs 3)
- Testability weight increased 4x - reflects ISO 29148 mandatory requirement
- Quality gate display now shows research references
- Validation output includes tier classification (TIER 1/2/3)
- Enhanced error messages showing which gates failed

### Justification
Based on extensive research into recent requirements engineering literature:
- **ISO/IEC/IEEE 29148:2018**: Testability is MANDATORY, not optional
- **Lucassen et al. (2017)**: Complete semantic structure → 40% fewer defects
- **IEEE 830-1998**: Single thought principle (atomicity)
- **Sweller (1988)**: Cognitive load theory
- **Flesch (1948)**: Readability formulas

### Migration Guide
Existing specs scoring well (≥0.70 overall) may now fail if:
- Structure < 70% (requirements not atomic/complete)
- Testability < 70% (lacking quantifiable constraints)
- Cognitive < 60% (too complex)
- Readability < 50% (too difficult to read)

**Recommendation**: Focus on improving testability (add measurable thresholds) and structure (atomic requirements).

### Documentation
- Full research justification: docs/WEIGHTS_AND_GATES_JUSTIFICATION.md
- 400+ lines documenting evidence, citations, impact analysis
- Comparison with ISO 29148, IEEE 830, ISO 25010

---

## [1.3.0] - 2026-02-03

### Added
- Comprehensive test suite with 32 tests and 86% code coverage
- GitHub Actions CI/CD workflows (test, publish, lint)
- Security checks with bandit and safety
- Code quality checks with ruff
- Test coverage reporting with pytest-cov

### Changed
- Updated pyproject.toml to include pytest and pytest-cov as dev dependencies
- Enhanced documentation with testing instructions

## [1.3.0] - 2026-02-03

### Added
- CSV export functionality for batch analysis results
- `--csv` flag for scan command
- `--output` flag to save results to file
- All 6 categories now displayed in batch summary table

### Changed
- Batch summary now shows complete category breakdown (behavioral, cognitive, readability, semantic, structure, testability)
- Improved table formatting for multi-spec analysis

### Fixed
- CSV export correctly formats all category scores
- Quality gates properly checked across all categories

## [1.2.0] - 2026-01-31

### Added
- Batch summary view for analyzing multiple specifications
- Summary table showing pass/fail statistics across specs
- Average scores calculation across all analyzed specs
- Failed specs highlighting with issue identification
- `--detailed` flag to show individual results in batch mode

### Changed
- Multi-spec analysis now defaults to summary table instead of individual results
- Improved performance for large spec collections

## [1.1.0] - 2026-01-31

### Added
- Per-requirement analysis feature with `--per-req` flag
- Individual quality scoring for each functional requirement
- Per-requirement quality gate validation
- Failed requirements report with specific failure reasons
- Support for analyzing FR-XXX, SC-XXX, NFR-XXX requirement patterns

### Changed
- Validate command now shows all 6 category scores instead of just 3
- Updated GitHub URLs to point to correct repository
- Enhanced output formatting for validation results

### Fixed
- Category score display in validation output

## [1.0.0] - 2026-01-30

### Added
- Initial release of speckit-metrics-enhanced
- 31 scientifically-proven requirements quality metrics
- 6 metric categories: Readability, Structure, Cognitive, Semantic, Testability, Behavioral
- CLI commands: `scan`, `validate`, `version`
- Auto-discovery of spec.md files in current directory and specs/ folder
- JSON output format for CI/CD integration
- Enhanced mode (31 metrics) and basic mode (18 metrics)
- Quality gates enforcement (Overall ≥0.70, Semantic ≥0.60, Testability ≥0.60)
- Rich terminal output with colors and tables
- Comprehensive documentation (3000+ lines)
- Scientific validation report with 24 peer-reviewed research papers
- Example specifications demonstrating quality patterns
- MIT License

### Metrics Included

#### Readability (6 metrics)
- Flesch Reading Ease
- Flesch-Kincaid Grade Level
- Gunning Fog Index
- SMOG Index
- Coleman-Liau Index
- Automated Readability Index

#### Structure (5 metrics)
- Atomicity Score
- Completeness Score
- Passive Voice Ratio
- Ambiguous Pronoun Ratio
- Modal Strength

#### Cognitive (7 metrics)
- Sentence Length
- Syllable Complexity
- Concept Density
- Coordination Complexity
- Subordination Complexity
- Negation Load
- Conditional Load

#### Semantic (6 metrics)
- Actor Presence
- Action Presence
- Object Presence
- Outcome Presence
- Trigger Presence
- SCC Composite Score

#### Testability (3 metrics)
- Hard Constraint Ratio
- Constraint Density
- Negative Space Coverage

#### Behavioral (4 metrics)
- Scenario Decomposition
- Transition Completeness
- Branch Coverage Proxy
- Observability Score

### Documentation
- README.md with quick start and examples
- QUICKSTART.md for 5-minute getting started
- INSTALLATION.md with detailed setup instructions
- USAGE_GUIDE.md with complete usage examples
- PACKAGE_SUMMARY.md with package overview
- GITHUB_SETUP.md with repository setup instructions
- docs/ENHANCED_METRICS_COMPLETE_REFERENCE.md (714 lines)
- docs/METRICS_OUTPUT_REFERENCE.md
- docs/METRICS_QUICK_REFERENCE.md
- docs/NORMALIZED_METRICS_COMPLETE_REFERENCE.md (370 lines)
- docs/SCIENTIFIC_VALIDATION_REPORT.md (742 lines)

## [0.1.0] - Development

### Added
- Initial development versions
- Core metric calculations
- Base architecture

---

## Links

- [Homepage](https://github.com/Testimonial/speckit-metrics-enhanced)
- [Issue Tracker](https://github.com/Testimonial/speckit-metrics-enhanced/issues)
- [Releases](https://github.com/Testimonial/speckit-metrics-enhanced/releases)
