#!/usr/bin/env python3
"""
Constraint Testability Metrics

Simple pattern-based detection of testable vs subjective constraints.

IMPORTANT: This is basic regex pattern matching, NOT sophisticated NLP.
We count numeric values, comparison operators, and subjective keywords.

Metrics:
- Hard Constraint Ratio: % of constraints that are quantifiable
- Constraint Density: Number of constraints per requirement
- Negative Space Coverage: Explicit exclusions/boundaries

Based on general requirements engineering principles:
- IEEE 830-1998 §4.3.7: Verifiable requirements standard
- Hard vs soft constraints (standard RE terminology)

Implementation:
- Regex patterns for numbers, units, comparisons, enums
- Keyword lists for subjective terms
- Negative pattern detection (must not, shall not, etc.)

NOT based on: CIRCE tool (which does semantic modeling, UML generation, etc.)
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
import math


@dataclass
class ConstraintMetrics:
    """Constraint testability metrics."""
    hard_constraint_ratio: float  # testable / total constraints
    constraint_density: float  # constraints per requirement (saturating)
    negative_space_coverage: float  # explicit boundaries/exclusions
    csb_score: float  # Composite constraint sharpness score

    def to_dict(self) -> Dict[str, float]:
        return {
            "hard_constraint_ratio": round(self.hard_constraint_ratio, 4),
            "constraint_density": round(self.constraint_density, 4),
            "negative_space_coverage": round(self.negative_space_coverage, 4),
            "csb_score": round(self.csb_score, 4),
        }


class ConstraintAnalyzer:
    """Analyzes requirements for constraint testability."""

    # Hard constraint patterns (quantifiable, testable)
    HARD_CONSTRAINT_PATTERNS = [
        # Numeric with units
        r'\d+(\.\d+)?\s*(ms|milliseconds?|sec|seconds?|min|minutes?|hours?|days?)',
        r'\d+(\.\d+)?\s*(B|KB|MB|GB|TB|bytes?|kilobytes?|megabytes?|gigabytes?)',
        r'\d+(\.\d+)?\s*%',
        r'\d+(\.\d+)?\s*(requests?|queries?|transactions?|operations?)\s*per\s*(sec|second|min|minute|hour|day)',

        # Comparisons
        r'<\s*\d+', r'>\s*\d+', r'=\s*\d+', r'<=\s*\d+', r'>=\s*\d+',
        r'less\s+than\s+\d+', r'greater\s+than\s+\d+', r'equal\s+to\s+\d+',
        r'at\s+least\s+\d+', r'at\s+most\s+\d+', r'no\s+more\s+than\s+\d+',
        r'between\s+\d+\s+and\s+\d+', r'from\s+\d+\s+to\s+\d+',

        # Ranges and thresholds
        r'\d+\s*-\s*\d+',  # "10-20 items"
        r'maximum\s+of\s+\d+', r'minimum\s+of\s+\d+',
        r'up\s+to\s+\d+', r'within\s+\d+',

        # Specific enumerated values (HTTP status codes are testable exact values)
        r'\b(HTTP\s+\d{3})\b',  # HTTP status codes
        r'\bHTTP[_\s]?\d{3}\b',  # HTTP 200, HTTP_404, etc.

        # Exact values
        r'exactly\s+\d+', r'precisely\s+\d+',
    ]

    # Soft constraint keywords (subjective, not testable)
    SOFT_CONSTRAINT_KEYWORDS = [
        'fast', 'slow', 'quick', 'responsive',
        'user-friendly', 'intuitive', 'easy', 'simple',
        'secure', 'robust', 'reliable', 'stable',
        'scalable', 'flexible', 'maintainable',
        'efficient', 'optimal', 'high-quality',
        'appropriate', 'reasonable', 'adequate',
    ]

    # Negative space patterns (explicit boundaries)
    NEGATIVE_PATTERNS = [
        r'\bmust\s+not\b',
        r'\bshall\s+not\b',
        r'\bshould\s+not\b',
        r'\bcannot\b',
        r'\bcan\s+not\b',
        r'\bdo\s+not\b',
        r'\bdoes\s+not\b',
        r'\bwill\s+not\b',
        r'\bnever\b',
        r'\bprohibited\b',
        r'\bforbidden\b',
        r'\bnot\s+allowed\b',
        r'\bnot\s+permitted\b',
        r'\bout\s+of\s+scope\b',
        r'\bexcludes?\b',
        r'\bomits?\b',
    ]

    def count_hard_constraints(self, text: str) -> int:
        """
        Count quantifiable, testable constraints.

        Args:
            text: Requirement text

        Returns:
            Number of hard constraints found
        """
        count = 0
        text_lower = text.lower()

        for pattern in self.HARD_CONSTRAINT_PATTERNS:
            matches = re.findall(pattern, text_lower)
            count += len(matches)

        return count

    def count_soft_constraints(self, text: str) -> int:
        """
        Count subjective, non-testable constraint keywords.

        Args:
            text: Requirement text

        Returns:
            Number of soft constraints found
        """
        count = 0
        text_lower = text.lower()

        for keyword in self.SOFT_CONSTRAINT_KEYWORDS:
            if keyword in text_lower:
                count += 1

        return count

    def count_negative_statements(self, text: str) -> int:
        """
        Count explicit boundary/exclusion statements.

        Args:
            text: Requirement text

        Returns:
            Number of negative space indicators
        """
        count = 0
        text_lower = text.lower()

        for pattern in self.NEGATIVE_PATTERNS:
            matches = re.findall(pattern, text_lower)
            count += len(matches)

        return count

    def analyze_requirements(self, requirements: List[str]) -> ConstraintMetrics:
        """
        Analyze constraint testability across multiple requirements.

        Args:
            requirements: List of requirement strings

        Returns:
            ConstraintMetrics with testability scores
        """
        if not requirements:
            return ConstraintMetrics(0, 0, 0, 0)

        total_reqs = len(requirements)
        total_hard = 0
        total_soft = 0
        total_negative = 0

        for req in requirements:
            total_hard += self.count_hard_constraints(req)
            total_soft += self.count_soft_constraints(req)
            total_negative += self.count_negative_statements(req)

        total_constraints = total_hard + total_soft

        # Hard Constraint Ratio (HCR)
        # = testable constraints / all constraints
        # Higher is better (more testable)
        if total_constraints > 0:
            hard_constraint_ratio = total_hard / total_constraints
        else:
            hard_constraint_ratio = 0.0  # No constraints found means not testable

        # Constraint Density (CDS)
        # = constraints per requirement (saturating exponential)
        # Formula from BCI: 1 - e^(-density)
        # Sweet spot: 1-2 constraints per requirement
        density = total_constraints / total_reqs
        constraint_density = 1.0 - math.exp(-density)

        # Negative Space Coverage (NSC)
        # = presence of explicit boundaries (saturating)
        # Formula from BCI: 1 - e^(-negatives/sentences)
        # Higher is better (clearer boundaries)
        negative_ratio = total_negative / total_reqs
        negative_space_coverage = 1.0 - math.exp(-negative_ratio)

        # CSB Score (Constraint Sharpness & Boundaries)
        # Weighted composite from BCI framework
        csb_score = (
            0.45 * hard_constraint_ratio +
            0.35 * constraint_density +
            0.20 * negative_space_coverage
        )

        return ConstraintMetrics(
            hard_constraint_ratio=hard_constraint_ratio,
            constraint_density=constraint_density,
            negative_space_coverage=negative_space_coverage,
            csb_score=csb_score
        )


def analyze_constraint_testability(text: str) -> Dict[str, float]:
    """
    Convenience function to analyze constraint testability of requirements text.

    Args:
        text: Requirements text (can contain multiple requirements)

    Returns:
        Dictionary with constraint metrics
    """
    # Split into requirements (simple sentence splitting)
    sentences = re.split(r'[.!?]+', text)
    requirements = [s.strip() for s in sentences if len(s.strip()) > 10]

    analyzer = ConstraintAnalyzer()
    metrics = analyzer.analyze_requirements(requirements)

    return metrics.to_dict()
