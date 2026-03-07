#!/usr/bin/env python3
"""
Normalized Requirements Metrics - All metrics in 0-1 range with weights

Provides normalized scores (0-1) for all requirements quality metrics with
configurable weights for weighted average calculation.

Score interpretation:
- 1.0 = Perfect/Ideal
- 0.8-1.0 = Excellent
- 0.6-0.8 = Good
- 0.4-0.6 = Fair
- 0.2-0.4 = Poor
- 0.0-0.2 = Very Poor
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field
import math

try:
    from .requirements_metrics import RequirementsAnalyzer, RequirementQualityMetrics
except ImportError:
    from requirements_metrics import RequirementsAnalyzer, RequirementQualityMetrics


@dataclass
class NormalizedScore:
    """Container for a normalized metric with its weight."""
    name: str
    score: float  # 0-1
    weight: float  # 0-1
    category: str  # readability, structure, cognitive
    raw_value: Any  # Original value before normalization
    ideal_value: Any  # Ideal/target value
    description: str

    def weighted_score(self) -> float:
        """Calculate weighted score."""
        return self.score * self.weight

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "score": round(self.score, 4),
            "weight": round(self.weight, 4),
            "weighted_score": round(self.weighted_score(), 4),
            "category": self.category,
            "raw_value": self.raw_value,
            "ideal_value": self.ideal_value,
            "description": self.description,
        }


@dataclass
class NormalizedMetrics:
    """Complete set of normalized metrics with weights."""
    scores: List[NormalizedScore] = field(default_factory=list)

    def add(self, score: NormalizedScore):
        """Add a normalized score."""
        self.scores.append(score)

    def get_by_category(self, category: str) -> List[NormalizedScore]:
        """Get all scores for a category."""
        return [s for s in self.scores if s.category == category]

    def weighted_average(self, category: str = None) -> float:
        """
        Calculate weighted average score.

        Args:
            category: If provided, calculate only for that category.
                     If None, calculate overall average.

        Returns:
            Weighted average score (0-1)
        """
        if category:
            scores = self.get_by_category(category)
        else:
            scores = self.scores

        if not scores:
            return 0.0

        total_weighted = sum(s.weighted_score() for s in scores)
        total_weight = sum(s.weight for s in scores)

        return total_weighted / total_weight if total_weight > 0 else 0.0

    def category_averages(self) -> Dict[str, float]:
        """Calculate weighted average for each category."""
        categories = set(s.category for s in self.scores)
        return {
            cat: self.weighted_average(cat)
            for cat in categories
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scores": [s.to_dict() for s in self.scores],
            "overall_weighted_average": round(self.weighted_average(), 4),
            "category_averages": {
                k: round(v, 4)
                for k, v in self.category_averages().items()
            },
        }


class MetricsNormalizer:
    """Normalizes requirements metrics to 0-1 range with weights."""

    # Default weights for each metric (must sum to 1.0 per category)
    DEFAULT_WEIGHTS = {
        "readability": {
            "flesch_reading_ease": 0.25,
            "flesch_kincaid_grade": 0.15,
            "gunning_fog_index": 0.15,
            "smog_index": 0.15,
            "coleman_liau_index": 0.15,
            "automated_readability_index": 0.15,
        },
        "structure": {
            "atomicity_score": 0.30,
            "completeness_score": 0.30,
            "passive_voice_ratio": 0.15,
            "ambiguous_pronoun_ratio": 0.10,
            "modal_strength": 0.15,
        },
        "cognitive": {
            "sentence_length": 0.20,
            "syllable_complexity": 0.15,
            "concept_density": 0.15,
            "coordination_complexity": 0.15,
            "subordination_complexity": 0.15,
            "negation_load": 0.10,
            "conditional_load": 0.10,
        },
    }

    # Category weights for overall score
    CATEGORY_WEIGHTS = {
        "readability": 0.30,
        "structure": 0.40,
        "cognitive": 0.30,
    }

    # Ideal/target values for each metric
    IDEAL_VALUES = {
        "flesch_reading_ease": 65.0,  # 8th-9th grade level
        "flesch_kincaid_grade": 10.0,  # 10th grade
        "gunning_fog_index": 12.0,  # 12th grade
        "smog_index": 12.0,  # 12th grade
        "coleman_liau_index": 10.0,  # 10th grade
        "automated_readability_index": 10.0,  # 10th grade
        "atomicity_score": 1.0,  # 100% atomic
        "completeness_score": 1.0,  # 100% complete
        "passive_voice_ratio": 0.0,  # 0% passive
        "ambiguous_pronoun_ratio": 0.0,  # 0% ambiguous
        "modal_strength": 1.0,  # Strong modals (MUST/SHALL)
        "sentence_length": 20.0,  # 20 words per sentence
        "syllable_complexity": 1.5,  # 1.5 syllables per word
        "concept_density": 0.20,  # 20% concept density
        "coordination_complexity": 0.05,  # 5% coordination
        "subordination_complexity": 0.05,  # 5% subordination
        "negation_load": 0.02,  # 2% negations
        "conditional_load": 0.05,  # 5% conditionals
    }

    def __init__(self, custom_weights: Dict[str, Dict[str, float]] = None,
                 custom_category_weights: Dict[str, float] = None):
        """
        Initialize normalizer with optional custom weights.

        Args:
            custom_weights: Override default metric weights
            custom_category_weights: Override default category weights
        """
        self.weights = custom_weights or self.DEFAULT_WEIGHTS
        self.category_weights = custom_category_weights or self.CATEGORY_WEIGHTS
        self._validate_weights()

    def _validate_weights(self):
        """Ensure all weights sum to 1.0."""
        for category, weights_dict in self.weights.items():
            total = sum(weights_dict.values())
            if not math.isclose(total, 1.0, rel_tol=0.01):
                raise ValueError(f"Weights for {category} sum to {total}, must sum to 1.0")

        total_cat = sum(self.category_weights.values())
        if not math.isclose(total_cat, 1.0, rel_tol=0.01):
            raise ValueError(f"Category weights sum to {total_cat}, must sum to 1.0")

    def normalize_metrics(self, metrics: RequirementQualityMetrics) -> NormalizedMetrics:
        """
        Normalize all metrics to 0-1 range.

        Args:
            metrics: Raw metrics from RequirementsAnalyzer

        Returns:
            NormalizedMetrics with all scores in 0-1 range
        """
        normalized = NormalizedMetrics()

        # Apply category weights to individual metric weights
        self._normalize_readability(metrics, normalized)
        self._normalize_structure(metrics, normalized)
        self._normalize_cognitive(metrics, normalized)

        return normalized

    def _normalize_readability(self, metrics: RequirementQualityMetrics,
                               normalized: NormalizedMetrics):
        """Normalize readability metrics."""
        cat = "readability"
        cat_weight = self.category_weights[cat]

        # Flesch Reading Ease (0-100, ideal=65)
        # Score = 1.0 - |FRE - 65| / 100
        fre = metrics.readability.flesch_reading_ease
        fre_distance = abs(fre - self.IDEAL_VALUES["flesch_reading_ease"])
        fre_score = max(0.0, 1.0 - (fre_distance / 100.0))

        normalized.add(NormalizedScore(
            name="flesch_reading_ease",
            score=fre_score,
            weight=self.weights[cat]["flesch_reading_ease"] * cat_weight,
            category=cat,
            raw_value=fre,
            ideal_value=self.IDEAL_VALUES["flesch_reading_ease"],
            description="Overall readability (higher = easier)"
        ))

        # Grade level metrics (lower is better, ideal=10, max acceptable=20)
        for metric_name, metric_value in [
            ("flesch_kincaid_grade", metrics.readability.flesch_kincaid_grade),
            ("gunning_fog_index", metrics.readability.gunning_fog_index),
            ("smog_index", metrics.readability.smog_index),
            ("coleman_liau_index", metrics.readability.coleman_liau_index),
            ("automated_readability_index", metrics.readability.automated_readability_index),
        ]:
            ideal = self.IDEAL_VALUES[metric_name]
            # Score decreases as we move away from ideal
            # Perfect score at ideal, 0 at 3x ideal
            distance = abs(metric_value - ideal)
            score = max(0.0, 1.0 - (distance / (ideal * 2)))

            normalized.add(NormalizedScore(
                name=metric_name,
                score=score,
                weight=self.weights[cat][metric_name] * cat_weight,
                category=cat,
                raw_value=metric_value,
                ideal_value=ideal,
                description=f"Grade level complexity (ideal: {ideal})"
            ))

    def _normalize_structure(self, metrics: RequirementQualityMetrics,
                            normalized: NormalizedMetrics):
        """Normalize structural metrics."""
        cat = "structure"
        cat_weight = self.category_weights[cat]

        # Atomicity (already 0-1, higher is better)
        normalized.add(NormalizedScore(
            name="atomicity_score",
            score=metrics.structure.atomicity_score,
            weight=self.weights[cat]["atomicity_score"] * cat_weight,
            category=cat,
            raw_value=metrics.structure.atomicity_score,
            ideal_value=1.0,
            description="Single testable statement per requirement"
        ))

        # Completeness (already 0-1, higher is better)
        normalized.add(NormalizedScore(
            name="completeness_score",
            score=metrics.structure.completeness_score,
            weight=self.weights[cat]["completeness_score"] * cat_weight,
            category=cat,
            raw_value=metrics.structure.completeness_score,
            ideal_value=1.0,
            description="Complete actor-action-object patterns"
        ))

        # Passive voice ratio (lower is better, 0-1)
        total_reqs = max(metrics.structure.total_requirements, 1)
        passive_ratio = metrics.structure.passive_voice_count / total_reqs
        passive_score = 1.0 - min(passive_ratio, 1.0)

        normalized.add(NormalizedScore(
            name="passive_voice_ratio",
            score=passive_score,
            weight=self.weights[cat]["passive_voice_ratio"] * cat_weight,
            category=cat,
            raw_value=passive_ratio,
            ideal_value=0.0,
            description="Passive voice usage (lower is better)"
        ))

        # Ambiguous pronoun ratio (lower is better, 0-1)
        ambiguous_ratio = metrics.structure.ambiguous_pronouns / total_reqs
        ambiguous_score = 1.0 - min(ambiguous_ratio, 1.0)

        normalized.add(NormalizedScore(
            name="ambiguous_pronoun_ratio",
            score=ambiguous_score,
            weight=self.weights[cat]["ambiguous_pronoun_ratio"] * cat_weight,
            category=cat,
            raw_value=ambiguous_ratio,
            ideal_value=0.0,
            description="Ambiguous pronoun usage (lower is better)"
        ))

        # Modal verb strength (MUST/SHALL=strong, SHOULD=medium, MAY=weak)
        modal_strength = self._calculate_modal_strength(metrics.structure.modal_verbs, total_reqs)

        normalized.add(NormalizedScore(
            name="modal_strength",
            score=modal_strength,
            weight=self.weights[cat]["modal_strength"] * cat_weight,
            category=cat,
            raw_value=modal_strength,
            ideal_value=1.0,
            description="Requirement strength (MUST/SHALL preferred)"
        ))

    def _normalize_cognitive(self, metrics: RequirementQualityMetrics,
                            normalized: NormalizedMetrics):
        """Normalize cognitive complexity metrics."""
        cat = "cognitive"
        cat_weight = self.category_weights[cat]

        # Sentence length (ideal=20, acceptable up to 30)
        ideal_length = self.IDEAL_VALUES["sentence_length"]
        length = metrics.cognitive.avg_words_per_sentence
        length_distance = abs(length - ideal_length)
        length_score = max(0.0, 1.0 - (length_distance / ideal_length))

        normalized.add(NormalizedScore(
            name="sentence_length",
            score=length_score,
            weight=self.weights[cat]["sentence_length"] * cat_weight,
            category=cat,
            raw_value=length,
            ideal_value=ideal_length,
            description=f"Average words per sentence (ideal: {ideal_length})"
        ))

        # Syllable complexity (ideal=1.5, acceptable up to 2.5)
        ideal_syllables = self.IDEAL_VALUES["syllable_complexity"]
        syllables = metrics.cognitive.avg_syllables_per_word
        syllable_distance = abs(syllables - ideal_syllables)
        syllable_score = max(0.0, 1.0 - (syllable_distance / ideal_syllables))

        normalized.add(NormalizedScore(
            name="syllable_complexity",
            score=syllable_score,
            weight=self.weights[cat]["syllable_complexity"] * cat_weight,
            category=cat,
            raw_value=syllables,
            ideal_value=ideal_syllables,
            description=f"Average syllables per word (ideal: {ideal_syllables})"
        ))

        # Concept density (ideal=0.20, max acceptable=0.40)
        ideal_density = self.IDEAL_VALUES["concept_density"]
        density = metrics.cognitive.concept_density
        density_score = max(0.0, 1.0 - (abs(density - ideal_density) / ideal_density))

        normalized.add(NormalizedScore(
            name="concept_density",
            score=density_score,
            weight=self.weights[cat]["concept_density"] * cat_weight,
            category=cat,
            raw_value=density,
            ideal_value=ideal_density,
            description="Unique concepts per word (lower is better)"
        ))

        # Coordination complexity (normalize by word count)
        total_words = max(
            int(metrics.cognitive.avg_words_per_sentence *
                (metrics.cognitive.coordination_complexity +
                 metrics.cognitive.subordination_complexity + 1)),
            1
        )
        coord_ratio = metrics.cognitive.coordination_complexity / total_words
        coord_score = max(0.0, 1.0 - (coord_ratio / 0.10))  # 10% = score 0

        normalized.add(NormalizedScore(
            name="coordination_complexity",
            score=coord_score,
            weight=self.weights[cat]["coordination_complexity"] * cat_weight,
            category=cat,
            raw_value=coord_ratio,
            ideal_value=0.05,
            description="Coordinating conjunctions (and/or/but)"
        ))

        # Subordination complexity (normalize by word count)
        sub_ratio = metrics.cognitive.subordination_complexity / total_words
        sub_score = max(0.0, 1.0 - (sub_ratio / 0.10))  # 10% = score 0

        normalized.add(NormalizedScore(
            name="subordination_complexity",
            score=sub_score,
            weight=self.weights[cat]["subordination_complexity"] * cat_weight,
            category=cat,
            raw_value=sub_ratio,
            ideal_value=0.05,
            description="Subordinating conjunctions (if/when/because)"
        ))

        # Negation load (normalize by word count)
        neg_ratio = metrics.cognitive.negation_count / total_words
        neg_score = max(0.0, 1.0 - (neg_ratio / 0.05))  # 5% = score 0

        normalized.add(NormalizedScore(
            name="negation_load",
            score=neg_score,
            weight=self.weights[cat]["negation_load"] * cat_weight,
            category=cat,
            raw_value=neg_ratio,
            ideal_value=0.02,
            description="Negations (not/no/never)"
        ))

        # Conditional load (normalize by word count)
        cond_ratio = metrics.cognitive.conditional_count / total_words
        cond_score = max(0.0, 1.0 - (cond_ratio / 0.10))  # 10% = score 0

        normalized.add(NormalizedScore(
            name="conditional_load",
            score=cond_score,
            weight=self.weights[cat]["conditional_load"] * cat_weight,
            category=cat,
            raw_value=cond_ratio,
            ideal_value=0.05,
            description="Conditionals (if/when/unless)"
        ))

    def _calculate_modal_strength(self, modal_verbs: Dict[str, int],
                                  total_reqs: int) -> float:
        """
        Calculate modal verb strength score.

        Strong modals (must/shall) = 1.0
        Medium modals (should) = 0.6
        Weak modals (may/might/could/would) = 0.3
        No modals = 0.0

        Returns score 0-1 based on weighted distribution.
        """
        if total_reqs == 0:
            return 0.0

        strong = modal_verbs.get("must", 0) + modal_verbs.get("shall", 0)
        medium = modal_verbs.get("should", 0)
        weak = (modal_verbs.get("may", 0) + modal_verbs.get("might", 0) +
                modal_verbs.get("could", 0) + modal_verbs.get("would", 0))

        total_modals = strong + medium + weak

        if total_modals == 0:
            return 0.5  # Neutral score for no modal verbs

        # Weighted score
        score = (strong * 1.0 + medium * 0.6 + weak * 0.3) / total_modals
        return score


def analyze_with_normalized_metrics(
    text: str,
    custom_weights: Dict[str, Dict[str, float]] = None,
    custom_category_weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Convenience function to analyze requirements with normalized metrics.

    Args:
        text: Requirements text to analyze
        custom_weights: Optional custom metric weights
        custom_category_weights: Optional custom category weights

    Returns:
        Dictionary with both raw and normalized metrics
    """
    # Get raw metrics
    analyzer = RequirementsAnalyzer()
    raw_metrics = analyzer.analyze_requirements(text)

    # Normalize
    normalizer = MetricsNormalizer(custom_weights, custom_category_weights)
    normalized = normalizer.normalize_metrics(raw_metrics)

    return {
        "raw_metrics": raw_metrics.to_dict(),
        "normalized_metrics": normalized.to_dict(),
    }


if __name__ == "__main__":
    # Example usage
    sample_text = """
    FR-001: System must allow users to create profiles.
    FR-002: System must validate email format before saving.
    FR-003: Users must be able to update profile information.
    FR-004: System must display user profile data on request.
    """

    result = analyze_with_normalized_metrics(sample_text)

    print("=" * 70)
    print("NORMALIZED METRICS (All in 0-1 range)")
    print("=" * 70)

    normalized = result["normalized_metrics"]

    print(f"\nOverall Weighted Average: {normalized['overall_weighted_average']:.4f}")
    print("\nCategory Averages:")
    for cat, score in normalized["category_averages"].items():
        print(f"  {cat.capitalize()}: {score:.4f}")

    print("\nDetailed Scores:")
    print(f"{'Metric':<35} {'Score':<8} {'Weight':<8} {'Weighted':<10}")
    print("-" * 70)

    for score_dict in normalized["scores"]:
        print(f"{score_dict['name']:<35} "
              f"{score_dict['score']:<8.4f} "
              f"{score_dict['weight']:<8.4f} "
              f"{score_dict['weighted_score']:<10.4f}")
