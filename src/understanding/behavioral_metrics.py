#!/usr/bin/env python3
"""
Behavioral Simulatability (SIM) Metrics - Layer 4 of BCI Framework

Measures whether requirements can be modeled as state machines:
- Scenario Decomposition: Presence of conditional structures (IF/WHEN/UNLESS)
- Transition Completeness: Guard→Action→Outcome triples
- Branch Coverage Proxy: Decision branches and error paths
- Observability: Observable outcomes for verification

Based on:
- Harel et al. (2005): Statechart generation from scenarios
- Harel & Marelly (2003): Live Sequence Charts (LSCs)
- Voas & Miller (1995): PIE model (Propagation, Infection, Execution)

Key insight: Requirements should describe state machines (implicitly or explicitly)
"""

import re
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
import math


@dataclass
class Transition:
    """Represents a behavioral transition (guard→action→outcome)."""
    guard: str  # Condition/trigger
    action: str  # What happens
    outcome: str  # Result
    is_complete: bool  # Has all three parts

    def __repr__(self) -> str:
        return f"Transition(guard={self.guard}, action={self.action}, outcome={self.outcome}, complete={self.is_complete})"


@dataclass
class BehavioralMetrics:
    """Behavioral simulatability metrics."""
    scenario_decomposition_score: float  # % with conditional structures
    transition_completeness_score: float  # % complete transitions
    branch_coverage_score: float  # Decision branches present
    observability_score: float  # % with observable outcomes
    sim_score: float  # Composite simulatability score

    def to_dict(self) -> Dict[str, float]:
        return {
            "scenario_decomposition_score": round(self.scenario_decomposition_score, 4),
            "transition_completeness_score": round(self.transition_completeness_score, 4),
            "branch_coverage_score": round(self.branch_coverage_score, 4),
            "observability_score": round(self.observability_score, 4),
            "sim_score": round(self.sim_score, 4),
        }


class BehavioralAnalyzer:
    """Analyzes requirements for behavioral clarity and simulatability."""

    # Conditional/trigger patterns (guards)
    CONDITIONAL_PATTERNS = [
        r'\bif\b',
        r'\bwhen\b',
        r'\bunless\b',
        r'\bgiven\b',
        r'\bafter\b',
        r'\bbefore\b',
        r'\bon\b(?!\s+the)',  # "on" but not "on the" (preposition)
        r'\bin\s+case\b',
        r'\bprovided\b',
        r'\bassuming\b',
        r'\bwhenever\b',
        r'\bupon\b',
    ]

    # Action verb patterns (what system does)
    ACTION_VERBS = [
        'validate', 'verify', 'check', 'confirm',
        'create', 'generate', 'produce', 'build',
        'update', 'modify', 'change', 'edit',
        'delete', 'remove', 'destroy', 'clear',
        'display', 'show', 'present', 'render',
        'send', 'transmit', 'emit', 'notify',
        'store', 'save', 'persist', 'record',
        'retrieve', 'fetch', 'get', 'load',
        'process', 'handle', 'execute', 'perform',
    ]

    # Observable outcome keywords
    OBSERVABLE_KEYWORDS = [
        # UI/Display
        'display', 'show', 'render', 'present', 'visualize',
        'hide', 'highlight', 'enable', 'disable',

        # Output/Response
        'return', 'output', 'respond', 'reply',
        'emit', 'send', 'transmit', 'notify', 'alert',

        # Storage/State
        'store', 'save', 'persist', 'record', 'log', 'write',
        'update', 'modify', 'change', 'set',

        # Status/Code
        'status', 'code', 'message', 'error', 'warning',
        'HTTP', 'response',

        # State changes
        'becomes', 'transitions', 'changes to', 'moves to',
        'active', 'inactive', 'enabled', 'disabled',
    ]

    # Error/exception patterns (branches)
    ERROR_PATTERNS = [
        r'\berror\b', r'\bfail\b', r'\bfailure\b',
        r'\bexception\b', r'\binvalid\b',
        r'\brejected?\b', r'\bdenied\b',
        r'\btimeout\b', r'\bexpired?\b',
        r'\bif\s+not\b', r'\bunless\b',
    ]

    def has_conditional(self, text: str) -> bool:
        """
        Check if requirement contains conditional structure.

        Args:
            text: Requirement text

        Returns:
            True if conditional found
        """
        text_lower = text.lower()
        for pattern in self.CONDITIONAL_PATTERNS:
            if re.search(pattern, text_lower):
                return True
        return False

    def has_observable_outcome(self, text: str) -> bool:
        """
        Check if requirement has observable outcome.

        Args:
            text: Requirement text

        Returns:
            True if observable outcome found
        """
        text_lower = text.lower()
        for keyword in self.OBSERVABLE_KEYWORDS:
            if keyword in text_lower:
                return True
        return False

    def extract_transitions(self, text: str) -> List[Transition]:
        """
        Extract behavioral transitions (guard→action→outcome).

        Args:
            text: Requirement text

        Returns:
            List of extracted transitions
        """
        transitions = []
        text_lower = text.lower()

        # Look for conditional structures
        for cond_pattern in self.CONDITIONAL_PATTERNS:
            match = re.search(cond_pattern, text_lower)
            if match:
                guard = match.group()

                # Look for action verb after condition
                action = None
                for verb in self.ACTION_VERBS:
                    if verb in text_lower:
                        action = verb
                        break

                # Look for observable outcome
                outcome = None
                for keyword in self.OBSERVABLE_KEYWORDS:
                    if keyword in text_lower:
                        outcome = keyword
                        break

                # Check completeness
                is_complete = (guard is not None and
                              action is not None and
                              outcome is not None)

                transitions.append(Transition(
                    guard=guard or "",
                    action=action or "",
                    outcome=outcome or "",
                    is_complete=is_complete
                ))

        # If no conditional but has action + outcome, implicit transition
        if not transitions:
            action = None
            for verb in self.ACTION_VERBS:
                if verb in text_lower:
                    action = verb
                    break

            outcome = None
            for keyword in self.OBSERVABLE_KEYWORDS:
                if keyword in text_lower:
                    outcome = keyword
                    break

            if action or outcome:
                transitions.append(Transition(
                    guard="",  # Implicit/always
                    action=action or "",
                    outcome=outcome or "",
                    is_complete=(action is not None and outcome is not None)
                ))

        return transitions

    def count_branches(self, text: str) -> Tuple[int, int]:
        """
        Count decision branches (total and error branches).

        Args:
            text: Requirement text

        Returns:
            (total_branches, error_branches)
        """
        text_lower = text.lower()

        # Count conditionals
        total_branches = sum(1 for pattern in self.CONDITIONAL_PATTERNS
                            if re.search(pattern, text_lower))

        # Count error/exception branches
        error_branches = sum(1 for pattern in self.ERROR_PATTERNS
                            if re.search(pattern, text_lower))

        return total_branches, error_branches

    def analyze_requirements(self, requirements: List[str]) -> BehavioralMetrics:
        """
        Analyze behavioral simulatability across multiple requirements.

        Args:
            requirements: List of requirement strings

        Returns:
            BehavioralMetrics with simulatability scores
        """
        if not requirements:
            return BehavioralMetrics(0, 0, 0, 0, 0)

        total_reqs = len(requirements)
        conditional_count = 0
        observable_count = 0
        all_transitions = []
        total_branches = 0
        total_error_branches = 0

        for req in requirements:
            # Scenario decomposition
            if self.has_conditional(req):
                conditional_count += 1

            # Observability
            if self.has_observable_outcome(req):
                observable_count += 1

            # Transitions
            transitions = self.extract_transitions(req)
            all_transitions.extend(transitions)

            # Branches
            branches, error_branches = self.count_branches(req)
            total_branches += branches
            total_error_branches += error_branches

        # Scenario Decomposition Score (SDS)
        # Formula from BCI: 1 - e^(-conditionals/sentences)
        # Measures presence of conditional structures
        conditional_ratio = conditional_count / total_reqs
        scenario_decomposition_score = 1.0 - math.exp(-conditional_ratio)

        # Transition Completeness (TC)
        # = complete transitions / total transitions
        if all_transitions:
            complete_transitions = sum(1 for t in all_transitions if t.is_complete)
            transition_completeness_score = complete_transitions / len(all_transitions)
        else:
            transition_completeness_score = 0.0

        # Branch Coverage Proxy (BCP)
        # Formula from BCI: (log(1+branches) + 0.5×log(1+error_branches)) / target
        # Target: log(1+6) + 0.5×log(1+3) ≈ 2.60 (6 branches, 3 error paths is "good")
        target = math.log(1 + 6) + 0.5 * math.log(1 + 3)
        if total_branches > 0:
            branch_coverage_score = min(
                (math.log(1 + total_branches) + 0.5 * math.log(1 + total_error_branches)) / target,
                1.0
            )
        else:
            branch_coverage_score = 0.0

        # Observability Score (OBS)
        # = % requirements with observable outcomes
        observability_score = observable_count / total_reqs

        # SIM Score (Simulatability)
        # Weighted composite from BCI framework
        sim_score = (
            0.25 * scenario_decomposition_score +
            0.35 * transition_completeness_score +
            0.20 * branch_coverage_score +
            0.20 * observability_score
        )

        return BehavioralMetrics(
            scenario_decomposition_score=scenario_decomposition_score,
            transition_completeness_score=transition_completeness_score,
            branch_coverage_score=branch_coverage_score,
            observability_score=observability_score,
            sim_score=sim_score
        )


def analyze_behavioral_simulatability(text: str) -> Dict[str, float]:
    """
    Convenience function to analyze behavioral simulatability of requirements text.

    Args:
        text: Requirements text (can contain multiple requirements)

    Returns:
        Dictionary with behavioral metrics
    """
    # Split into requirements (simple sentence splitting)
    sentences = re.split(r'[.!?]+', text)
    requirements = [s.strip() for s in sentences if len(s.strip()) > 10]

    analyzer = BehavioralAnalyzer()
    metrics = analyzer.analyze_requirements(requirements)

    return metrics.to_dict()
