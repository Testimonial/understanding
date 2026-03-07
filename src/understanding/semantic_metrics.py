#!/usr/bin/env python3
"""
Semantic Category Coverage (SCC) Metrics - Layer 2 of BCI Framework

Extracts and validates semantic roles in requirements:
- Actor (who): Subject/agent performing action
- Action (what): Verb/predicate
- Object (to what): Direct object/patient
- Outcome (result): Result clause/state change
- Trigger (when): Conditional/event that initiates

Based on:
- Lucassen et al. (2017): Visual Narrator - Actor-Action-Object extraction
- Gildea & Jurafsky (2002): Semantic Role Labeling
- Kiyavitskaya et al. (2008): AAVE Framework

Two-tier implementation:
1. Basic: Regex patterns (no dependencies, good accuracy)
2. Enhanced: spaCy NLP (optional, better accuracy)
"""

import re
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

# Optional spaCy import
try:
    import spacy
    SPACY_AVAILABLE = True
    try:
        _nlp = spacy.load("en_core_web_sm")
    except OSError:
        SPACY_AVAILABLE = False
        _nlp = None
except ImportError:
    SPACY_AVAILABLE = False
    _nlp = None


@dataclass
class SemanticRoles:
    """Container for extracted semantic roles."""
    actors: List[str]
    actions: List[str]
    objects: List[str]
    outcomes: List[str]
    triggers: List[str]

    def has_actor(self) -> bool:
        return len(self.actors) > 0

    def has_action(self) -> bool:
        return len(self.actions) > 0

    def has_object(self) -> bool:
        return len(self.objects) > 0

    def has_outcome(self) -> bool:
        return len(self.outcomes) > 0

    def has_trigger(self) -> bool:
        return len(self.triggers) > 0


@dataclass
class SemanticMetrics:
    """Semantic category coverage metrics."""
    actor_presence: float  # % requirements with actor
    action_presence: float  # % requirements with action
    object_presence: float  # % requirements with object
    outcome_presence: float  # % requirements with outcome
    trigger_presence: float  # % requirements with trigger (conditional)
    scc_score: float  # Composite semantic completeness score

    def to_dict(self) -> Dict[str, float]:
        return {
            "actor_presence": round(self.actor_presence, 4),
            "action_presence": round(self.action_presence, 4),
            "object_presence": round(self.object_presence, 4),
            "outcome_presence": round(self.outcome_presence, 4),
            "trigger_presence": round(self.trigger_presence, 4),
            "scc_score": round(self.scc_score, 4),
        }


class SemanticAnalyzer:
    """Analyzes requirements for semantic role coverage."""

    # Actor patterns (who performs action)
    ACTOR_PATTERNS = [
        r'\b(user|admin|system|customer|client|operator|manager|developer|tester)\b',
        r'\b(application|service|module|component|interface|database|server)\b',
        r'\b(the\s+\w+)\s+(shall|must|should|will|can)\b',  # "the system shall"
    ]

    # Action verbs (common in requirements)
    ACTION_VERBS = [
        'validate', 'verify', 'check', 'confirm', 'ensure',
        'create', 'generate', 'produce', 'build', 'make',
        'update', 'modify', 'change', 'edit', 'revise',
        'delete', 'remove', 'destroy', 'clear', 'purge',
        'display', 'show', 'present', 'render', 'visualize',
        'send', 'transmit', 'emit', 'notify', 'alert',
        'store', 'save', 'persist', 'record', 'log',
        'retrieve', 'fetch', 'get', 'load', 'read',
        'process', 'handle', 'manage', 'execute', 'perform',
        'allow', 'enable', 'permit', 'authorize', 'grant',
        'prevent', 'block', 'deny', 'reject', 'refuse',
    ]

    # Object patterns (what is acted upon)
    OBJECT_PATTERNS = [
        r'\b(data|information|record|entry|item|element)\b',
        r'\b(file|document|report|form|template)\b',
        r'\b(message|notification|alert|email|request)\b',
        r'\b(user|account|profile|session|credential)\b',
        r'\b(input|output|response|result|value)\b',
    ]

    # Outcome/result patterns
    OUTCOME_PATTERNS = [
        r'returns?\s+\w+',  # "return status code"
        r'displays?\s+\w+',  # "display error message"
        r'shows?\s+\w+',  # "show confirmation"
        r'generates?\s+\w+',  # "generate report"
        r'sends?\s+\w+',  # "send notification"
        r'stores?\s+\w+',  # "store result"
        r'becomes?\s+\w+',  # "becomes active"
        r'transitions?\s+to\s+\w+',  # "transitions to state"
        r'changes?\s+to\s+\w+',  # "changes to status"
        r'results?\s+in\s+\w+',  # "results in error"
    ]

    # Trigger/condition patterns (when action occurs)
    # Note: "\bon\b" excluded — too noisy ("based on", "click on", "depends on")
    TRIGGER_PATTERNS = [
        r'\bif\b',
        r'\bwhen\b',
        r'\bunless\b',
        r'\bgiven\b',
        r'\bafter\b',
        r'\bbefore\b',
        r'\bupon\b',
        r'\bin case\b',
        r'\bprovided\b',
        r'\bassuming\b',
        r'\bwhenever\b',
    ]

    def __init__(self, use_spacy: bool = True):
        """
        Initialize semantic analyzer.

        Args:
            use_spacy: If True and spaCy available, use enhanced extraction
        """
        self.use_spacy = use_spacy and SPACY_AVAILABLE
        self.nlp = _nlp if self.use_spacy else None

    def extract_semantic_roles_basic(self, text: str) -> SemanticRoles:
        """
        Extract semantic roles using regex patterns (basic, no dependencies).

        Args:
            text: Requirement text

        Returns:
            SemanticRoles with extracted elements
        """
        text_lower = text.lower()

        # Extract actors
        actors = []
        for pattern in self.ACTOR_PATTERNS:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            actors.extend(matches if isinstance(matches, list) else [matches])

        # Extract actions (verbs)
        actions = [verb for verb in self.ACTION_VERBS if verb in text_lower]

        # Extract objects
        objects = []
        for pattern in self.OBJECT_PATTERNS:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            objects.extend(matches if isinstance(matches, list) else [matches])

        # Extract outcomes
        outcomes = []
        for pattern in self.OUTCOME_PATTERNS:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                outcomes.append(matches[0] if isinstance(matches, str) else str(matches))

        # Extract triggers
        triggers = []
        for pattern in self.TRIGGER_PATTERNS:
            if re.search(pattern, text_lower):
                triggers.append(pattern.strip('\\b'))

        return SemanticRoles(
            actors=list(set(actors)),
            actions=list(set(actions)),
            objects=list(set(objects)),
            outcomes=list(set(outcomes)),
            triggers=list(set(triggers))
        )

    def extract_semantic_roles_spacy(self, text: str) -> SemanticRoles:
        """
        Extract semantic roles using spaCy NLP (enhanced, requires spaCy).

        Args:
            text: Requirement text

        Returns:
            SemanticRoles with extracted elements
        """
        if not self.nlp:
            return self.extract_semantic_roles_basic(text)

        doc = self.nlp(text)

        actors = []
        actions = []
        objects = []
        outcomes = []
        triggers = []

        for token in doc:
            # Actor: nominal subject (nsubj, nsubjpass)
            if token.dep_ in ["nsubj", "nsubjpass"]:
                actors.append(token.text.lower())

            # Action: main verbs
            if token.pos_ == "VERB" and token.dep_ in ["ROOT", "xcomp", "ccomp"]:
                actions.append(token.lemma_.lower())

            # Object: direct object, prepositional object
            if token.dep_ in ["dobj", "pobj", "obj"]:
                objects.append(token.text.lower())

            # Outcome: clausal complements often indicate results
            if token.dep_ in ["ccomp", "xcomp", "advcl"]:
                outcomes.append(token.text.lower())

            # Trigger: subordinating conjunctions
            if token.dep_ == "mark":  # Marker of subordinate clause
                triggers.append(token.text.lower())

        # If no outcomes found via dependency, use regex fallback
        if not outcomes:
            for pattern in self.OUTCOME_PATTERNS:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    outcomes.append(str(matches[0]))

        return SemanticRoles(
            actors=list(set(actors)),
            actions=list(set(actions)),
            objects=list(set(objects)),
            outcomes=list(set(outcomes)),
            triggers=list(set(triggers))
        )

    def extract_semantic_roles(self, text: str) -> SemanticRoles:
        """
        Extract semantic roles (uses spaCy if available, else regex).

        Args:
            text: Requirement text

        Returns:
            SemanticRoles with extracted elements
        """
        if self.use_spacy and self.nlp:
            return self.extract_semantic_roles_spacy(text)
        return self.extract_semantic_roles_basic(text)

    def analyze_requirements(self, requirements: List[str]) -> SemanticMetrics:
        """
        Analyze semantic coverage across multiple requirements.

        Args:
            requirements: List of requirement strings

        Returns:
            SemanticMetrics with coverage percentages
        """
        if not requirements:
            return SemanticMetrics(0, 0, 0, 0, 0, 0)

        total = len(requirements)
        actor_count = 0
        action_count = 0
        object_count = 0
        outcome_count = 0
        trigger_count = 0

        for req in requirements:
            roles = self.extract_semantic_roles(req)

            if roles.has_actor():
                actor_count += 1
            if roles.has_action():
                action_count += 1
            if roles.has_object():
                object_count += 1
            if roles.has_outcome():
                outcome_count += 1
            if roles.has_trigger():
                trigger_count += 1

        # Calculate percentages
        actor_presence = actor_count / total
        action_presence = action_count / total
        object_presence = object_count / total
        outcome_presence = outcome_count / total
        trigger_presence = trigger_count / total

        # SCC score: weighted average
        # Core elements (A, V, O, R) are required (weight 1.0 each)
        # Trigger is optional but valuable (weight 0.7)
        # Formula from BCI: (pA + pV + pO + pR + w_T×pT) / (4 + w_T)
        _trigger_weight = 0.7
        _scc_denominator = 4 + _trigger_weight  # kept in sync with weight above
        scc_score = (
            actor_presence +
            action_presence +
            object_presence +
            outcome_presence +
            _trigger_weight * trigger_presence
        ) / _scc_denominator

        return SemanticMetrics(
            actor_presence=actor_presence,
            action_presence=action_presence,
            object_presence=object_presence,
            outcome_presence=outcome_presence,
            trigger_presence=trigger_presence,
            scc_score=scc_score
        )

    def extract_entities_detailed(
        self,
        requirements: List[str],
        use_nlp: bool = None
    ):
        """
        Extract detailed entity information (not just coverage metrics).

        This method exposes the underlying entity and relationship data
        for use in entity analysis features.

        Args:
            requirements: List of requirement strings
            use_nlp: Whether to use spaCy NLP (None = use instance setting)

        Returns:
            EntityExtractionResult with entities and relationships
        """
        from .entity_metrics import EntityExtractor

        # Use instance setting if not specified
        if use_nlp is None:
            use_nlp = self.use_spacy

        extractor = EntityExtractor(use_spacy=use_nlp)
        all_entities = []
        all_relationships = []

        for idx, req in enumerate(requirements):
            result = extractor.extract(req, requirement_id=str(idx))
            all_entities.extend(result.entities)
            all_relationships.extend(result.relationships)

        # Deduplicate
        all_entities = list(set(all_entities))
        all_relationships = list(set(all_relationships))

        # Import EntityExtractionResult for return type
        from .entity_metrics import EntityExtractionResult, EntityType

        # Count entities by type
        entity_counts = {}
        for entity in all_entities:
            entity_counts[entity.type] = entity_counts.get(entity.type, 0) + 1

        return EntityExtractionResult(
            entities=all_entities,
            relationships=all_relationships,
            entity_counts=entity_counts,
            unique_actors=set(e.normalized for e in all_entities if e.type == EntityType.ACTOR),
            unique_actions=set(e.normalized for e in all_entities if e.type == EntityType.ACTION),
            unique_objects=set(e.normalized for e in all_entities if e.type == EntityType.OBJECT)
        )


def analyze_semantic_coverage(text: str, use_spacy: bool = True) -> Dict[str, float]:
    """
    Convenience function to analyze semantic coverage of requirements text.

    Args:
        text: Requirements text (can contain multiple requirements)
        use_spacy: Whether to use spaCy if available

    Returns:
        Dictionary with semantic metrics
    """
    # Split into requirements (simple sentence splitting)
    sentences = re.split(r'[.!?]+', text)
    requirements = [s.strip() for s in sentences if len(s.strip()) > 10]

    analyzer = SemanticAnalyzer(use_spacy=use_spacy)
    metrics = analyzer.analyze_requirements(requirements)

    return metrics.to_dict()
