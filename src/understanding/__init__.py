"""Understanding - Requirements understanding and cognitive load metrics.

This package provides comprehensive requirements quality analysis with:
- 6 Readability metrics (Flesch, Gunning Fog, etc.)
- 5 Structure metrics (Atomicity, Completeness, etc.)
- 7 Cognitive metrics (Sentence length, Complexity, etc.)
- 6 Semantic metrics (Actor, Action, Object, Outcome, Trigger)
- 3 Testability metrics (Hard constraints, Density, Negative space)
- 4 Behavioral metrics (Scenarios, Transitions, Branches, Observability)

Example:
    >>> from understanding import analyze_with_enhanced_metrics
    >>> result = analyze_with_enhanced_metrics(requirements_text)
    >>> print(result["enhanced_metrics"]["overall_weighted_average"])
    0.78
"""

__version__ = "3.4.0"
__author__ = "Ladislav Bihari"

# Public API
from .enhanced_metrics import analyze_with_enhanced_metrics
from .normalized_metrics import analyze_with_normalized_metrics

# Energy metrics (optional — requires pip install understanding[energy])
try:
    from .energy_metrics import analyze_energy, is_energy_available
except ImportError:
    pass

__all__ = [
    "analyze_with_enhanced_metrics",
    "analyze_with_normalized_metrics",
    "analyze_energy",
    "is_energy_available",
]
