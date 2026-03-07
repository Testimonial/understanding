#!/usr/bin/env python3
"""
Enhanced Requirements Metrics - 31 Total Metrics (18 Base + 13 New)

Combines all metric layers:
- Layer 1: Readability + Structure + Cognitive (18 metrics)
- Layer 2: Semantic Category Coverage (6 metrics)
- Layer 3: Constraint Testability (3 metrics)
- Layer 4: Behavioral Simulatability (4 metrics)

Total: 31 metrics across 6 categories

New weight distribution:
- Readability: 25% (reduced from 30%)
- Structure: 35% (reduced from 40%)
- Cognitive: 25% (reduced from 30%)
- Semantic: 5% (NEW)
- Testability: 5% (NEW)
- Behavioral: 5% (NEW)
"""

from typing import Dict, Any
import re

try:
    from .normalized_metrics import analyze_with_normalized_metrics, NormalizedScore, NormalizedMetrics
    from .semantic_metrics import SemanticAnalyzer
    from .constraint_metrics import ConstraintAnalyzer
    from .behavioral_metrics import BehavioralAnalyzer
except ImportError:
    from normalized_metrics import analyze_with_normalized_metrics, NormalizedScore, NormalizedMetrics
    from semantic_metrics import SemanticAnalyzer
    from constraint_metrics import ConstraintAnalyzer
    from behavioral_metrics import BehavioralAnalyzer


# Enhanced category weights (sum to 1.0)
ENHANCED_CATEGORY_WEIGHTS = {
    "readability": 0.25,    # Reduced from 0.30
    "structure": 0.35,      # Reduced from 0.40
    "cognitive": 0.25,      # Reduced from 0.30
    "semantic": 0.05,       # NEW
    "testability": 0.05,    # NEW
    "behavioral": 0.05,     # NEW
}

# Weights within each new category (must sum to 1.0 per category)
NEW_CATEGORY_WEIGHTS = {
    "semantic": {
        "actor_presence": 0.20,
        "action_presence": 0.20,
        "object_presence": 0.20,
        "outcome_presence": 0.20,
        "trigger_presence": 0.10,
        "scc_score": 0.10,  # Composite
    },
    "testability": {
        "hard_constraint_ratio": 0.45,
        "constraint_density": 0.35,
        "negative_space_coverage": 0.20,
    },
    "behavioral": {
        "scenario_decomposition_score": 0.25,
        "transition_completeness_score": 0.35,
        "branch_coverage_score": 0.20,
        "observability_score": 0.20,
    },
}


def analyze_with_enhanced_metrics(
    text: str,
    use_spacy: bool = True
) -> Dict[str, Any]:
    """
    Analyze requirements with all 31 enhanced metrics.

    Args:
        text: Requirements text to analyze
        use_spacy: Whether to use spaCy for semantic extraction (if available)

    Returns:
        Dictionary with 31 normalized metrics (0-1 range)
    """
    # Get base 18 metrics (readability, structure, cognitive)
    base_result = analyze_with_normalized_metrics(text)
    base_normalized = base_result["normalized_metrics"]

    # Extract requirements for new analyzers
    sentences = re.split(r'[.!?]+', text)
    requirements = [s.strip() for s in sentences if len(s.strip()) > 10]

    # Create combined normalized metrics
    enhanced = NormalizedMetrics()

    # Add base metrics with adjusted category weights
    for score_dict in base_normalized["scores"]:
        category = score_dict["category"]
        new_cat_weight = ENHANCED_CATEGORY_WEIGHTS[category]
        old_cat_weight = 0.30 if category in ["readability", "cognitive"] else 0.40  # Old weights

        # Adjust individual metric weight proportionally
        old_metric_weight = score_dict["weight"]
        new_metric_weight = (old_metric_weight / old_cat_weight) * new_cat_weight

        enhanced.add(NormalizedScore(
            name=score_dict["name"],
            score=score_dict["score"],
            weight=new_metric_weight,
            category=category,
            raw_value=score_dict["raw_value"],
            ideal_value=score_dict["ideal_value"],
            description=score_dict["description"]
        ))

    # Add semantic metrics (Layer 2)
    semantic_analyzer = SemanticAnalyzer(use_spacy=use_spacy)
    semantic_metrics = semantic_analyzer.analyze_requirements(requirements)

    cat = "semantic"
    cat_weight = ENHANCED_CATEGORY_WEIGHTS[cat]

    enhanced.add(NormalizedScore(
        name="actor_presence",
        score=semantic_metrics.actor_presence,
        weight=NEW_CATEGORY_WEIGHTS[cat]["actor_presence"] * cat_weight,
        category=cat,
        raw_value=semantic_metrics.actor_presence,
        ideal_value=1.0,
        description="% requirements with identified actor (who)"
    ))

    enhanced.add(NormalizedScore(
        name="action_presence",
        score=semantic_metrics.action_presence,
        weight=NEW_CATEGORY_WEIGHTS[cat]["action_presence"] * cat_weight,
        category=cat,
        raw_value=semantic_metrics.action_presence,
        ideal_value=1.0,
        description="% requirements with identified action (what)"
    ))

    enhanced.add(NormalizedScore(
        name="object_presence",
        score=semantic_metrics.object_presence,
        weight=NEW_CATEGORY_WEIGHTS[cat]["object_presence"] * cat_weight,
        category=cat,
        raw_value=semantic_metrics.object_presence,
        ideal_value=1.0,
        description="% requirements with identified object (to what)"
    ))

    enhanced.add(NormalizedScore(
        name="outcome_presence",
        score=semantic_metrics.outcome_presence,
        weight=NEW_CATEGORY_WEIGHTS[cat]["outcome_presence"] * cat_weight,
        category=cat,
        raw_value=semantic_metrics.outcome_presence,
        ideal_value=1.0,
        description="% requirements with identified outcome (result)"
    ))

    enhanced.add(NormalizedScore(
        name="trigger_presence",
        score=semantic_metrics.trigger_presence,
        weight=NEW_CATEGORY_WEIGHTS[cat]["trigger_presence"] * cat_weight,
        category=cat,
        raw_value=semantic_metrics.trigger_presence,
        ideal_value=0.7,  # Not all requirements need triggers
        description="% requirements with identified trigger (when)"
    ))

    enhanced.add(NormalizedScore(
        name="scc_score",
        score=semantic_metrics.scc_score,
        weight=NEW_CATEGORY_WEIGHTS[cat]["scc_score"] * cat_weight,
        category=cat,
        raw_value=semantic_metrics.scc_score,
        ideal_value=1.0,
        description="Semantic completeness composite score"
    ))

    # Add testability metrics (Layer 3)
    constraint_analyzer = ConstraintAnalyzer()
    constraint_metrics = constraint_analyzer.analyze_requirements(requirements)

    cat = "testability"
    cat_weight = ENHANCED_CATEGORY_WEIGHTS[cat]

    enhanced.add(NormalizedScore(
        name="hard_constraint_ratio",
        score=constraint_metrics.hard_constraint_ratio,
        weight=NEW_CATEGORY_WEIGHTS[cat]["hard_constraint_ratio"] * cat_weight,
        category=cat,
        raw_value=constraint_metrics.hard_constraint_ratio,
        ideal_value=1.0,
        description="Ratio of testable/quantifiable constraints"
    ))

    enhanced.add(NormalizedScore(
        name="constraint_density",
        score=constraint_metrics.constraint_density,
        weight=NEW_CATEGORY_WEIGHTS[cat]["constraint_density"] * cat_weight,
        category=cat,
        raw_value=constraint_metrics.constraint_density,
        ideal_value=0.85,  # Saturation point
        description="Constraints per requirement (saturating)"
    ))

    enhanced.add(NormalizedScore(
        name="negative_space_coverage",
        score=constraint_metrics.negative_space_coverage,
        weight=NEW_CATEGORY_WEIGHTS[cat]["negative_space_coverage"] * cat_weight,
        category=cat,
        raw_value=constraint_metrics.negative_space_coverage,
        ideal_value=0.63,  # Saturation point
        description="Explicit boundary/exclusion statements"
    ))

    # Add behavioral metrics (Layer 4)
    behavioral_analyzer = BehavioralAnalyzer()
    behavioral_metrics = behavioral_analyzer.analyze_requirements(requirements)

    cat = "behavioral"
    cat_weight = ENHANCED_CATEGORY_WEIGHTS[cat]

    enhanced.add(NormalizedScore(
        name="scenario_decomposition_score",
        score=behavioral_metrics.scenario_decomposition_score,
        weight=NEW_CATEGORY_WEIGHTS[cat]["scenario_decomposition_score"] * cat_weight,
        category=cat,
        raw_value=behavioral_metrics.scenario_decomposition_score,
        ideal_value=0.85,  # Saturation point
        description="Presence of conditional structures"
    ))

    enhanced.add(NormalizedScore(
        name="transition_completeness_score",
        score=behavioral_metrics.transition_completeness_score,
        weight=NEW_CATEGORY_WEIGHTS[cat]["transition_completeness_score"] * cat_weight,
        category=cat,
        raw_value=behavioral_metrics.transition_completeness_score,
        ideal_value=1.0,
        description="% complete guard→action→outcome transitions"
    ))

    enhanced.add(NormalizedScore(
        name="branch_coverage_score",
        score=behavioral_metrics.branch_coverage_score,
        weight=NEW_CATEGORY_WEIGHTS[cat]["branch_coverage_score"] * cat_weight,
        category=cat,
        raw_value=behavioral_metrics.branch_coverage_score,
        ideal_value=1.0,
        description="Decision branches and error paths"
    ))

    enhanced.add(NormalizedScore(
        name="observability_score",
        score=behavioral_metrics.observability_score,
        weight=NEW_CATEGORY_WEIGHTS[cat]["observability_score"] * cat_weight,
        category=cat,
        raw_value=behavioral_metrics.observability_score,
        ideal_value=1.0,
        description="% requirements with observable outcomes"
    ))

    return {
        "base_metrics": base_result,
        "enhanced_metrics": enhanced.to_dict(),
        "metric_count": {
            "total": len(enhanced.scores),
            "readability": len(enhanced.get_by_category("readability")),
            "structure": len(enhanced.get_by_category("structure")),
            "cognitive": len(enhanced.get_by_category("cognitive")),
            "semantic": len(enhanced.get_by_category("semantic")),
            "testability": len(enhanced.get_by_category("testability")),
            "behavioral": len(enhanced.get_by_category("behavioral")),
        }
    }


if __name__ == "__main__":
    # Test with sample requirements
    sample_text = """
    FR-001: System must validate user email format before saving to database.
    FR-002: When user clicks submit button with invalid email, system displays error message "Invalid email format" and returns HTTP 400.
    FR-003: System must store validated user data within 200ms.
    FR-004: Users must be able to update their profile information.
    FR-005: System must not allow access to deleted accounts.
    """

    result = analyze_with_enhanced_metrics(sample_text)

    print("=" * 80)
    print("ENHANCED REQUIREMENTS METRICS (31 Total)")
    print("=" * 80)
    print()

    enhanced = result["enhanced_metrics"]

    print(f"Overall Score: {enhanced['overall_weighted_average']:.4f}/1.00")
    print()

    print("Category Scores:")
    for cat, score in sorted(enhanced["category_averages"].items()):
        weight_pct = ENHANCED_CATEGORY_WEIGHTS[cat] * 100
        print(f"  {cat.capitalize():<15} {score:.4f} ({weight_pct:.0f}% weight)")
    print()

    print("Metric Count:")
    for cat, count in sorted(result["metric_count"].items()):
        if cat != "total":
            print(f"  {cat.capitalize():<15} {count} metrics")
    print(f"  {'TOTAL':<15} {result['metric_count']['total']} metrics")
    print()

    print("=" * 80)
    print("Top 10 Metrics by Impact (Weighted Score)")
    print("=" * 80)
    print()

    # Sort by weighted score
    sorted_scores = sorted(enhanced["scores"],
                          key=lambda x: x["weighted_score"],
                          reverse=True)

    print(f"{'Rank':<6} {'Metric':<40} {'Score':<8} {'Weight':<10} {'Impact':<10}")
    print("-" * 80)

    for i, score in enumerate(sorted_scores[:10], 1):
        print(f"{i:<6} {score['name']:<40} "
              f"{score['score']:<8.4f} "
              f"{score['weight']:<10.4f} "
              f"{score['weighted_score']:<10.4f}")
