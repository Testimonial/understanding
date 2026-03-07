#!/usr/bin/env python3
"""
Entity extraction for requirements analysis.

Extracts actors, actions, objects, and their relationships from requirement text.
Uses the same patterns as SemanticAnalyzer but produces structured Entity/Relationship
objects for cross-spec analysis and diagram generation.

Two-tier:
1. Basic: Regex patterns (no dependencies)
2. Enhanced: spaCy NLP (optional, better accuracy)
"""

import re
from enum import Enum
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field

# Optional spaCy
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

# Optional graphviz
try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False


class EntityType(Enum):
    ACTOR = "actor"
    ACTION = "action"
    OBJECT = "object"


@dataclass(frozen=True)
class Entity:
    text: str
    type: EntityType
    normalized: str
    requirement_id: str = ""
    confidence: float = 1.0

    def __hash__(self):
        return hash((self.normalized, self.type, self.requirement_id))

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return (self.normalized == other.normalized
                and self.type == other.type
                and self.requirement_id == other.requirement_id)


@dataclass(frozen=True)
class Relationship:
    source: Entity
    relation: str
    target: Entity
    requirement_id: str = ""

    def __hash__(self):
        return hash((self.source.normalized, self.relation, self.target.normalized, self.requirement_id))

    def __eq__(self, other):
        if not isinstance(other, Relationship):
            return False
        return (self.source.normalized == other.source.normalized
                and self.relation == other.relation
                and self.target.normalized == other.target.normalized
                and self.requirement_id == other.requirement_id)


@dataclass
class EntityExtractionResult:
    entities: List[Entity]
    relationships: List[Relationship]
    entity_counts: Dict[EntityType, int] = field(default_factory=dict)
    unique_actors: Set[str] = field(default_factory=set)
    unique_actions: Set[str] = field(default_factory=set)
    unique_objects: Set[str] = field(default_factory=set)


# Patterns (aligned with semantic_metrics.py)
ACTOR_PATTERNS = [
    r'\b(user|admin|system|customer|client|operator|manager|developer|tester)\b',
    r'\b(application|service|module|component|interface|database|server)\b',
]

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

OBJECT_PATTERNS = [
    r'\b(data|information|record|entry|item|element)\b',
    r'\b(file|document|report|form|template)\b',
    r'\b(message|notification|alert|email|request|response)\b',
    r'\b(user|account|profile|session|credential|password)\b',
    r'\b(input|output|result|value|status|state)\b',
    r'\b(button|page|screen|view|dialog|menu)\b',
    r'\b(error|warning|confirmation|feedback)\b',
]


class EntityExtractor:
    """Extracts entities and relationships from requirements."""

    def __init__(self, use_spacy: bool = True):
        self.use_spacy = use_spacy and SPACY_AVAILABLE
        self.nlp = _nlp if self.use_spacy else None

    def extract(self, text: str, requirement_id: str = "") -> EntityExtractionResult:
        if self.use_spacy and self.nlp:
            return self._extract_spacy(text, requirement_id)
        return self._extract_regex(text, requirement_id)

    def _extract_regex(self, text: str, requirement_id: str) -> EntityExtractionResult:
        text_lower = text.lower()
        entities = []
        relationships = []

        # Extract actors
        actors = set()
        for pattern in ACTOR_PATTERNS:
            for match in re.finditer(pattern, text_lower):
                word = match.group(1)
                actors.add(word)
                entities.append(Entity(
                    text=word, type=EntityType.ACTOR,
                    normalized=word, requirement_id=requirement_id,
                ))

        # Extract actions
        actions = set()
        for verb in ACTION_VERBS:
            # Match verb forms (validate, validates, validated, validating)
            pattern = rf'\b{re.escape(verb)}[seding]*\b'
            if re.search(pattern, text_lower):
                actions.add(verb)
                entities.append(Entity(
                    text=verb, type=EntityType.ACTION,
                    normalized=verb, requirement_id=requirement_id,
                ))

        # Extract objects
        objects = set()
        for pattern in OBJECT_PATTERNS:
            for match in re.finditer(pattern, text_lower):
                word = match.group(1)
                # Skip if already captured as actor
                if word not in actors:
                    objects.add(word)
                    entities.append(Entity(
                        text=word, type=EntityType.OBJECT,
                        normalized=word, requirement_id=requirement_id,
                    ))

        # Build relationships: actor -> action -> object
        for actor in actors:
            actor_entity = Entity(text=actor, type=EntityType.ACTOR, normalized=actor, requirement_id=requirement_id)
            for action in actions:
                action_entity = Entity(text=action, type=EntityType.ACTION, normalized=action, requirement_id=requirement_id)
                relationships.append(Relationship(
                    source=actor_entity, relation="performs", target=action_entity,
                    requirement_id=requirement_id,
                ))
                for obj in objects:
                    obj_entity = Entity(text=obj, type=EntityType.OBJECT, normalized=obj, requirement_id=requirement_id)
                    relationships.append(Relationship(
                        source=action_entity, relation="on", target=obj_entity,
                        requirement_id=requirement_id,
                    ))

        return EntityExtractionResult(
            entities=entities,
            relationships=relationships,
            entity_counts={t: sum(1 for e in entities if e.type == t) for t in EntityType},
            unique_actors=actors,
            unique_actions=actions,
            unique_objects=objects,
        )

    def _extract_spacy(self, text: str, requirement_id: str) -> EntityExtractionResult:
        doc = self.nlp(text)
        entities = []
        actors = set()
        actions = set()
        objects = set()
        relationships = []

        actor_entities = []
        action_entities = []
        object_entities = []

        for token in doc:
            if token.dep_ in ("nsubj", "nsubjpass"):
                word = token.text.lower()
                actors.add(word)
                e = Entity(text=word, type=EntityType.ACTOR, normalized=word, requirement_id=requirement_id)
                entities.append(e)
                actor_entities.append(e)

            if token.pos_ == "VERB" and token.dep_ in ("ROOT", "xcomp", "ccomp"):
                word = token.lemma_.lower()
                actions.add(word)
                e = Entity(text=word, type=EntityType.ACTION, normalized=word, requirement_id=requirement_id)
                entities.append(e)
                action_entities.append(e)

            if token.dep_ in ("dobj", "pobj", "obj"):
                word = token.text.lower()
                if word not in actors:
                    objects.add(word)
                    e = Entity(text=word, type=EntityType.OBJECT, normalized=word, requirement_id=requirement_id)
                    entities.append(e)
                    object_entities.append(e)

        # Build relationships
        for ae in actor_entities:
            for ve in action_entities:
                relationships.append(Relationship(source=ae, relation="performs", target=ve, requirement_id=requirement_id))
        for ve in action_entities:
            for oe in object_entities:
                relationships.append(Relationship(source=ve, relation="on", target=oe, requirement_id=requirement_id))

        # Fallback: if spaCy found nothing, try regex
        if not entities:
            return self._extract_regex(text, requirement_id)

        return EntityExtractionResult(
            entities=entities,
            relationships=relationships,
            entity_counts={t: sum(1 for e in entities if e.type == t) for t in EntityType},
            unique_actors=actors,
            unique_actions=actions,
            unique_objects=objects,
        )

    def generate_text_diagram(self, entities: List[Entity], relationships: List[Relationship]) -> str:
        """Generate ASCII text diagram of entity relationships."""
        lines = []

        # Group by type
        actors = sorted(set(e.normalized for e in entities if e.type == EntityType.ACTOR))
        actions = sorted(set(e.normalized for e in entities if e.type == EntityType.ACTION))
        objects = sorted(set(e.normalized for e in entities if e.type == EntityType.OBJECT))

        if actors:
            lines.append("ACTORS:")
            for a in actors:
                lines.append(f"  [{a}]")

        if actions:
            lines.append("\nACTIONS:")
            for a in actions:
                lines.append(f"  ({a})")

        if objects:
            lines.append("\nOBJECTS:")
            for o in objects:
                lines.append(f"  <{o}>")

        if relationships:
            lines.append("\nRELATIONSHIPS:")
            seen = set()
            for r in relationships:
                key = (r.source.normalized, r.relation, r.target.normalized)
                if key not in seen:
                    seen.add(key)
                    lines.append(f"  {r.source.normalized} --{r.relation}--> {r.target.normalized}")

        return "\n".join(lines)

    def generate_graphviz_diagram(
        self, entities: List[Entity], relationships: List[Relationship],
        title: str = "Entity Relationships", output_path: str = None, fmt: str = "png"
    ) -> Optional[str]:
        """Generate graphviz diagram. Returns path if saved, None otherwise."""
        if not GRAPHVIZ_AVAILABLE:
            return None

        dot = graphviz.Digraph(comment=title)
        dot.attr(rankdir="LR", label=title, fontsize="14")

        # Add nodes by type with different shapes/colors
        for e in set((en.normalized, en.type) for en in entities):
            name, etype = e
            if etype == EntityType.ACTOR:
                dot.node(name, name, shape="box", style="filled", fillcolor="#E3F2FD")
            elif etype == EntityType.ACTION:
                dot.node(name, name, shape="ellipse", style="filled", fillcolor="#FFF3E0")
            elif etype == EntityType.OBJECT:
                dot.node(name, name, shape="box", style="filled,rounded", fillcolor="#E8F5E9")

        # Add edges
        seen = set()
        for r in relationships:
            key = (r.source.normalized, r.target.normalized)
            if key not in seen:
                seen.add(key)
                dot.edge(r.source.normalized, r.target.normalized, label=r.relation)

        if output_path:
            dot.render(output_path, format=fmt, cleanup=True)
            return f"{output_path}.{fmt}"
        return dot.source
