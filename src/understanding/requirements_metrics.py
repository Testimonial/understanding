#!/usr/bin/env python3
"""
Requirements Quality Metrics - Deterministic Evaluation

Implements scientifically-proven metrics for requirement understanding and cognitive analysis:
1. Readability metrics (Flesch, Gunning Fog, etc.)
2. Structural analysis (noun-verb relationships, actor-action-object patterns)
3. Cognitive complexity metrics
4. Requirements-specific quality indicators

References:
- Flesch, R. (1948). "A new readability yardstick"
- Gunning, R. (1952). "The Technique of Clear Writing"
- Kincaid et al. (1975). "Derivation of new readability formulas"
- Lucassen et al. (2017). "Visual Narrator: Requirements engineering using user story quality"
- IEEE 830-1998: Software Requirements Specifications
- ISO/IEC/IEEE 29148:2018: Requirements engineering
"""

import re
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass, field
from collections import Counter
import math


@dataclass
class ReadabilityScores:
    """Container for various readability metrics."""
    flesch_reading_ease: float  # 0-100, higher = easier
    flesch_kincaid_grade: float  # US grade level
    gunning_fog_index: float  # Years of education needed
    smog_index: float  # Years of education needed
    coleman_liau_index: float  # US grade level
    automated_readability_index: float  # US grade level
    average_grade_level: float  # Average of grade-based metrics

    def to_dict(self) -> Dict[str, float]:
        return {
            "flesch_reading_ease": round(self.flesch_reading_ease, 2),
            "flesch_kincaid_grade": round(self.flesch_kincaid_grade, 2),
            "gunning_fog_index": round(self.gunning_fog_index, 2),
            "smog_index": round(self.smog_index, 2),
            "coleman_liau_index": round(self.coleman_liau_index, 2),
            "automated_readability_index": round(self.automated_readability_index, 2),
            "average_grade_level": round(self.average_grade_level, 2),
        }


@dataclass
class StructuralAnalysis:
    """Analysis of requirement structure and noun-verb relationships."""
    total_requirements: int
    atomic_requirements: int  # Single testable statement
    compound_requirements: int  # Multiple statements joined
    actor_action_complete: int  # Complete who-what-how pattern
    actor_action_incomplete: int  # Missing elements
    passive_voice_count: int  # Passive constructions
    ambiguous_pronouns: int  # This, that, it without clear antecedent
    modal_verbs: Dict[str, int]  # shall, must, may, should, could counts
    atomicity_score: float  # 0-1, higher = more atomic
    completeness_score: float  # 0-1, higher = more complete

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_requirements": self.total_requirements,
            "atomic_requirements": self.atomic_requirements,
            "compound_requirements": self.compound_requirements,
            "actor_action_complete": self.actor_action_complete,
            "actor_action_incomplete": self.actor_action_incomplete,
            "passive_voice_count": self.passive_voice_count,
            "ambiguous_pronouns": self.ambiguous_pronouns,
            "modal_verbs": dict(self.modal_verbs),
            "atomicity_score": round(self.atomicity_score, 2),
            "completeness_score": round(self.completeness_score, 2),
        }


@dataclass
class CognitiveComplexity:
    """Cognitive load and complexity metrics."""
    avg_words_per_sentence: float
    avg_syllables_per_word: float
    avg_chars_per_word: float
    unique_concepts: int  # Unique nouns/entities
    concept_density: float  # Unique concepts / total words
    coordination_complexity: int  # And, or, but conjunctions
    subordination_complexity: int  # Because, if, when, while
    negation_count: int  # Not, no, never (increases cognitive load)
    conditional_count: int  # If, when, unless
    cognitive_load_score: float  # 0-1, higher = more complex

    def to_dict(self) -> Dict[str, Any]:
        return {
            "avg_words_per_sentence": round(self.avg_words_per_sentence, 2),
            "avg_syllables_per_word": round(self.avg_syllables_per_word, 2),
            "avg_chars_per_word": round(self.avg_chars_per_word, 2),
            "unique_concepts": self.unique_concepts,
            "concept_density": round(self.concept_density, 3),
            "coordination_complexity": self.coordination_complexity,
            "subordination_complexity": self.subordination_complexity,
            "negation_count": self.negation_count,
            "conditional_count": self.conditional_count,
            "cognitive_load_score": round(self.cognitive_load_score, 2),
        }


@dataclass
class RequirementQualityMetrics:
    """Comprehensive requirement quality assessment."""
    readability: ReadabilityScores
    structure: StructuralAnalysis
    cognitive: CognitiveComplexity
    overall_score: float  # 0-100, weighted combination
    quality_level: str  # Excellent, Good, Fair, Poor

    def to_dict(self) -> Dict[str, Any]:
        return {
            "readability": self.readability.to_dict(),
            "structure": self.structure.to_dict(),
            "cognitive": self.cognitive.to_dict(),
            "overall_score": round(self.overall_score, 2),
            "quality_level": self.quality_level,
        }


class RequirementsAnalyzer:
    """Deterministic analyzer for requirement quality."""

    # Passive voice indicators (be verbs + past participles)
    PASSIVE_INDICATORS = {
        "is", "are", "was", "were", "be", "been", "being",
        "has been", "have been", "had been", "will be", "shall be"
    }

    # Modal verbs for requirement strength analysis
    MODAL_VERBS = {
        "must": 3,      # Mandatory
        "shall": 3,     # Mandatory (formal)
        "should": 2,    # Recommended
        "may": 1,       # Optional
        "might": 1,     # Optional
        "could": 1,     # Optional
        "would": 1,     # Conditional
    }

    # Ambiguous pronouns
    AMBIGUOUS_PRONOUNS = {"this", "that", "it", "these", "those", "they", "them"}

    # Coordination conjunctions
    COORDINATING = {"and", "or", "but", "nor", "yet", "so"}

    # Compiled regex for action verb stem matching (handles inflected forms)
    # Stems are truncated so suffixes like -s, -ed, -ing, -ion, -tion match too
    _ACTION_VERB_RE = re.compile(
        r'\b(creat|updat|delet|remov|modif|display|shows?|send|receiv|'
        r'validat|verif|allow|enabl|prevent|provid|support|process|generat|'
        r'calculat|stor|retriev|authenticat|check|submit|confirm|notif|log|'
        r'track|read|add)\w*\b',
        re.IGNORECASE
    )

    # Subordinating conjunctions
    SUBORDINATING = {
        "because", "since", "as", "if", "when", "while", "after", "before",
        "unless", "until", "though", "although", "whereas", "wherever"
    }

    # Negations
    NEGATIONS = {"not", "no", "never", "neither", "nor", "nothing", "nowhere", "none"}

    # Conditionals
    CONDITIONALS = {"if", "when", "unless", "provided", "assuming"}

    def __init__(self):
        pass

    def analyze_requirements(self, text: str) -> RequirementQualityMetrics:
        """
        Perform comprehensive analysis on requirements text.

        Args:
            text: Raw requirements text (can include markdown)

        Returns:
            RequirementQualityMetrics with all computed metrics
        """
        # Clean text (remove markdown, code blocks, but keep structure)
        clean_text = self._clean_text(text)

        # Extract individual requirements
        requirements = self._extract_requirements(clean_text)

        # Calculate all metrics
        readability = self._calculate_readability(clean_text)
        structure = self._analyze_structure(requirements)
        cognitive = self._analyze_cognitive_complexity(clean_text, requirements)

        # Calculate overall score (0-100)
        overall_score = self._calculate_overall_score(readability, structure, cognitive)
        quality_level = self._determine_quality_level(overall_score)

        return RequirementQualityMetrics(
            readability=readability,
            structure=structure,
            cognitive=cognitive,
            overall_score=overall_score,
            quality_level=quality_level
        )

    def _clean_text(self, text: str) -> str:
        """Remove markdown formatting but preserve sentence structure."""
        # Remove code blocks
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"`[^`]+`", "", text)

        # Remove markdown formatting
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)  # Bold
        text = re.sub(r"\*([^*]+)\*", r"\1", text)  # Italic
        text = re.sub(r"__([^_]+)__", r"\1", text)  # Bold
        text = re.sub(r"_([^_]+)_", r"\1", text)  # Italic
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # Links
        text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)  # Headers
        text = re.sub(r"^[*\-+]\s+", "", text, flags=re.MULTILINE)  # Lists
        text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)  # Numbered lists

        # Remove HTML comments
        text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

        return text.strip()

    def _extract_requirements(self, text: str) -> List[str]:
        """Extract individual requirement statements."""
        requirements = []

        # Look for FR-NNN patterns or numbered requirements
        fr_pattern = r"(?:^|\n)\s*(?:FR-\d+|REQ-\d+|\d+\.)\s*[:\-]?\s*(.+?)(?=\n\s*(?:FR-\d+|REQ-\d+|\d+\.)|$)"
        matches = re.findall(fr_pattern, text, re.DOTALL | re.MULTILINE)

        if matches:
            requirements.extend([m.strip() for m in matches if m.strip()])
        else:
            # Fall back to sentence splitting
            sentences = re.split(r'[.!?]+\s+', text)
            requirements = [s.strip() for s in sentences if len(s.strip()) > 10]

        return requirements

    def _calculate_readability(self, text: str) -> ReadabilityScores:
        """Calculate multiple readability metrics."""
        # Basic text statistics
        sentences = self._count_sentences(text)
        words = self._count_words(text)
        syllables = self._count_syllables(text)
        characters = len(re.sub(r'\s', '', text))

        # Avoid division by zero
        if sentences == 0 or words == 0:
            return ReadabilityScores(0, 0, 0, 0, 0, 0, 0)

        avg_words_per_sentence = words / sentences
        avg_syllables_per_word = syllables / words

        # Flesch Reading Ease (0-100, higher = easier)
        # 90-100: 5th grade, 60-70: 8th-9th grade, 0-30: college graduate
        flesch_reading_ease = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        flesch_reading_ease = max(0, min(100, flesch_reading_ease))

        # Flesch-Kincaid Grade Level
        flesch_kincaid = (0.39 * avg_words_per_sentence) + (11.8 * avg_syllables_per_word) - 15.59
        flesch_kincaid = max(0, flesch_kincaid)

        # Gunning Fog Index (years of education needed)
        complex_words = self._count_complex_words(text)
        gunning_fog = 0.4 * (avg_words_per_sentence + (100 * complex_words / words))

        # SMOG Index (years of education needed)
        # Requires at least 30 sentences for accuracy
        polysyllable_count = self._count_polysyllables(text)
        smog = 1.0430 * math.sqrt(polysyllable_count * (30 / max(sentences, 1))) + 3.1291
        smog = max(0, smog)

        # Coleman-Liau Index
        avg_letters_per_100_words = (characters / words) * 100
        avg_sentences_per_100_words = (sentences / words) * 100
        coleman_liau = (0.0588 * avg_letters_per_100_words) - (0.296 * avg_sentences_per_100_words) - 15.8
        coleman_liau = max(0, coleman_liau)

        # Automated Readability Index (ARI)
        avg_chars_per_word = characters / words
        ari = (4.71 * avg_chars_per_word) + (0.5 * avg_words_per_sentence) - 21.43
        ari = max(0, ari)

        # Average grade level
        grade_metrics = [flesch_kincaid, gunning_fog, smog, coleman_liau, ari]
        average_grade = sum(grade_metrics) / len(grade_metrics)

        return ReadabilityScores(
            flesch_reading_ease=flesch_reading_ease,
            flesch_kincaid_grade=flesch_kincaid,
            gunning_fog_index=gunning_fog,
            smog_index=smog,
            coleman_liau_index=coleman_liau,
            automated_readability_index=ari,
            average_grade_level=average_grade
        )

    def _analyze_structure(self, requirements: List[str]) -> StructuralAnalysis:
        """Analyze structural quality of requirements."""
        total = len(requirements)
        if total == 0:
            return StructuralAnalysis(0, 0, 0, 0, 0, 0, 0, {}, 0.0, 0.0)

        atomic = 0
        compound = 0
        actor_action_complete = 0
        actor_action_incomplete = 0
        passive_voice = 0
        ambiguous = 0
        modal_counts: Dict[str, int] = {modal: 0 for modal in self.MODAL_VERBS.keys()}

        for req in requirements:
            req_lower = req.lower()
            words = req_lower.split()

            # Check atomicity (single vs compound requirements)
            conjunctions = sum(1 for word in words if word in self.COORDINATING)
            if conjunctions == 0:
                atomic += 1
            else:
                compound += 1

            # Check actor-action-object pattern
            # Complete: has subject (actor), verb (action), object
            has_actor = self._has_actor(req)
            has_action = self._has_action_verb(req)
            has_object = self._has_object(req)

            if has_actor and has_action and has_object:
                actor_action_complete += 1
            else:
                actor_action_incomplete += 1

            # Check passive voice
            if self._is_passive_voice(req_lower):
                passive_voice += 1

            # Check ambiguous pronouns
            for pronoun in self.AMBIGUOUS_PRONOUNS:
                if f" {pronoun} " in f" {req_lower} ":
                    ambiguous += 1
                    break

            # Count modal verbs
            for modal in self.MODAL_VERBS.keys():
                modal_counts[modal] += req_lower.count(f" {modal} ")

        # Calculate scores
        atomicity_score = atomic / total if total > 0 else 0.0
        completeness_score = actor_action_complete / total if total > 0 else 0.0

        return StructuralAnalysis(
            total_requirements=total,
            atomic_requirements=atomic,
            compound_requirements=compound,
            actor_action_complete=actor_action_complete,
            actor_action_incomplete=actor_action_incomplete,
            passive_voice_count=passive_voice,
            ambiguous_pronouns=ambiguous,
            modal_verbs=modal_counts,
            atomicity_score=atomicity_score,
            completeness_score=completeness_score
        )

    def _analyze_cognitive_complexity(self, text: str, requirements: List[str]) -> CognitiveComplexity:
        """Analyze cognitive load and complexity."""
        sentences = self._count_sentences(text)
        words_list = re.findall(r'\b\w+\b', text.lower())
        total_words = len(words_list)

        if sentences == 0 or total_words == 0:
            return CognitiveComplexity(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        # Basic statistics
        avg_words_per_sentence = total_words / sentences
        syllables = self._count_syllables(text)
        avg_syllables_per_word = syllables / total_words
        characters = sum(len(word) for word in words_list)
        avg_chars_per_word = characters / total_words

        # Unique concepts (nouns and named entities)
        nouns = self._extract_nouns(text)
        unique_concepts = len(set(nouns))
        concept_density = unique_concepts / total_words if total_words > 0 else 0

        # Coordination complexity (and, or, but)
        coordination = sum(words_list.count(conj) for conj in self.COORDINATING)

        # Subordination complexity (because, if, when)
        subordination = sum(words_list.count(sub) for sub in self.SUBORDINATING)

        # Negations (increase cognitive load)
        negations = sum(words_list.count(neg) for neg in self.NEGATIONS)

        # Conditionals
        conditionals = sum(words_list.count(cond) for cond in self.CONDITIONALS)

        # Cognitive load score (0-1, normalized)
        # Higher values = more complex
        complexity_factors = [
            min(avg_words_per_sentence / 30, 1.0),  # Sentence length
            min(avg_syllables_per_word / 2.5, 1.0),  # Word complexity
            min(concept_density / 0.3, 1.0),  # Concept density
            min(coordination / 10, 1.0),  # Coordination
            min(subordination / 10, 1.0),  # Subordination
            min(negations / 5, 1.0),  # Negations
        ]
        cognitive_load = sum(complexity_factors) / len(complexity_factors)

        return CognitiveComplexity(
            avg_words_per_sentence=avg_words_per_sentence,
            avg_syllables_per_word=avg_syllables_per_word,
            avg_chars_per_word=avg_chars_per_word,
            unique_concepts=unique_concepts,
            concept_density=concept_density,
            coordination_complexity=coordination,
            subordination_complexity=subordination,
            negation_count=negations,
            conditional_count=conditionals,
            cognitive_load_score=cognitive_load
        )

    def _calculate_overall_score(
        self,
        readability: ReadabilityScores,
        structure: StructuralAnalysis,
        cognitive: CognitiveComplexity
    ) -> float:
        """
        Calculate weighted overall quality score (0-100).

        Weights based on requirements engineering best practices:
        - Readability: 30% (must be understandable)
        - Structure: 40% (must be well-formed)
        - Cognitive: 30% (must not overload reader)
        """
        # Readability score (convert to 0-100)
        # Target: 60-70 Flesch Reading Ease (8th-9th grade)
        readability_target = 65
        readability_score = max(0, min(100, readability.flesch_reading_ease))
        readability_normalized = 100 - abs(readability_score - readability_target)

        # Structure score (0-100)
        structure_score = (
            (structure.atomicity_score * 40) +
            (structure.completeness_score * 40) +
            ((1 - structure.passive_voice_count / max(structure.total_requirements, 1)) * 10) +
            ((1 - structure.ambiguous_pronouns / max(structure.total_requirements, 1)) * 10)
        )
        structure_score = max(0, min(100, structure_score))

        # Cognitive score (0-100, lower cognitive load = higher score)
        cognitive_score = (1 - cognitive.cognitive_load_score) * 100

        # Weighted average
        overall = (
            readability_normalized * 0.30 +
            structure_score * 0.40 +
            cognitive_score * 0.30
        )

        return max(0, min(100, overall))

    def _determine_quality_level(self, overall_score: float) -> str:
        """Determine quality level based on overall score."""
        if overall_score >= 80:
            return "Excellent"
        elif overall_score >= 65:
            return "Good"
        elif overall_score >= 50:
            return "Fair"
        else:
            return "Poor"

    # Helper methods for text analysis

    def _count_sentences(self, text: str) -> int:
        """Count sentences in text."""
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])

    def _count_words(self, text: str) -> int:
        """Count words in text."""
        words = re.findall(r'\b\w+\b', text)
        return len(words)

    def _count_syllables(self, text: str) -> int:
        """
        Count syllables using simplified algorithm.
        Based on Flesch syllable counting method.
        """
        words = re.findall(r'\b\w+\b', text.lower())
        total_syllables = 0

        for word in words:
            # Count vowel groups
            vowels = "aeiouy"
            syllable_count = 0
            previous_was_vowel = False

            for char in word:
                is_vowel = char in vowels
                if is_vowel and not previous_was_vowel:
                    syllable_count += 1
                previous_was_vowel = is_vowel

            # Adjust for silent e
            if word.endswith('e'):
                syllable_count -= 1

            # Ensure at least one syllable
            if syllable_count == 0:
                syllable_count = 1

            total_syllables += syllable_count

        return total_syllables

    def _count_complex_words(self, text: str) -> int:
        """Count words with 3+ syllables (Gunning Fog definition)."""
        words = re.findall(r'\b\w+\b', text.lower())
        complex_count = 0

        for word in words:
            if self._count_word_syllables(word) >= 3:
                complex_count += 1

        return complex_count

    def _count_polysyllables(self, text: str) -> int:
        """Count words with 3+ syllables (SMOG definition)."""
        return self._count_complex_words(text)

    def _count_word_syllables(self, word: str) -> int:
        """Count syllables in a single word."""
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False

        for char in word.lower():
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        if word.endswith('e'):
            syllable_count -= 1

        return max(1, syllable_count)

    def _has_actor(self, requirement: str) -> bool:
        """Check if requirement has an actor/subject."""
        req_lower = requirement.lower()

        # Explicit actor keywords
        actor_pattern = (
            r'\b(user|system|application|administrator|customer|client|'
            r'operator|manager|developer|tester|service|module|component|'
            r'database|server|api|interface|browser|device|agent)\b'
        )
        if re.search(actor_pattern, req_lower):
            return True

        # "the/a/an <noun> shall/must/should/will/can" pattern
        subject_modal = r'\b(?:the|a|an)\s+(\w+)\s+(?:shall|must|should|will|can|may)\b'
        match = re.search(subject_modal, req_lower)
        if match:
            noun = match.group(1)
            # Exclude words that are not meaningful actors
            non_actors = {"time", "only", "also", "first", "last", "next", "then"}
            if noun not in non_actors and len(noun) > 2:
                return True

        return False

    def _has_action_verb(self, requirement: str) -> bool:
        """Check if requirement has an action verb (handles inflected forms)."""
        return bool(self._ACTION_VERB_RE.search(requirement))

    def _has_object(self, requirement: str) -> bool:
        """Check if requirement has an object (content word after action verb)."""
        _STOPWORDS = {
            "the", "a", "an", "to", "of", "in", "on", "at", "for", "with",
            "by", "is", "are", "was", "were", "be", "been", "being",
            "shall", "must", "should", "may", "might", "could", "would",
            "will", "can", "do", "does", "did", "not", "and", "or", "but",
            "that", "this", "their", "its", "also", "from", "into", "via",
            "as", "if", "when", "then", "so", "which", "who", "where",
        }
        words = re.findall(r'\b\w+\b', requirement.lower())

        # Find the first action verb position
        verb_pos = -1
        for i, word in enumerate(words):
            if self._ACTION_VERB_RE.match(word):
                verb_pos = i
                break

        if verb_pos == -1:
            # No action verb — look for content words beyond position 3
            content = [w for w in words[3:] if w not in _STOPWORDS and len(w) > 2]
            return len(content) > 0

        # Content words after the action verb are the object
        after_verb = words[verb_pos + 1:]
        content_after = [w for w in after_verb if w not in _STOPWORDS and len(w) > 2]
        return len(content_after) > 0

    def _is_passive_voice(self, requirement: str) -> bool:
        """Detect passive voice constructions."""
        # Look for "be" verb + past participle patterns
        for indicator in self.PASSIVE_INDICATORS:
            if indicator in requirement:
                # Simple heuristic: if "by" follows, likely passive
                if " by " in requirement:
                    return True
                # Check for past participle pattern (be + ed/en word)
                pattern = f"{indicator} \\w+(ed|en)\\b"
                if re.search(pattern, requirement):
                    return True
        return False

    def _extract_nouns(self, text: str) -> List[str]:
        """
        Extract likely nouns (simplified heuristic).
        In production, use spaCy or NLTK for better accuracy.
        """
        words = re.findall(r'\b[A-Z][a-z]+\b', text)  # Capitalized words
        words += re.findall(r'\b\w+(?:tion|ment|ness|ity|er|or|ist)\b', text.lower())  # Common noun suffixes
        return words


def analyze_requirements_text(text: str) -> Dict[str, Any]:
    """
    Convenience function to analyze requirements and return dict.

    Args:
        text: Requirements text to analyze

    Returns:
        Dictionary with all metrics
    """
    analyzer = RequirementsAnalyzer()
    metrics = analyzer.analyze_requirements(text)
    return metrics.to_dict()


if __name__ == "__main__":
    # Example usage
    sample_text = """
    FR-001: The system must allow users to create new accounts.
    FR-002: Users shall be able to reset their passwords via email.
    FR-003: The application should validate email addresses before registration.
    FR-004: System must store user preferences in the database.
    """

    result = analyze_requirements_text(sample_text)
    print("Requirements Quality Metrics:")
    print(f"Overall Score: {result['overall_score']}/100 ({result['quality_level']})")
    print(f"\nReadability:")
    print(f"  Flesch Reading Ease: {result['readability']['flesch_reading_ease']}")
    print(f"  Average Grade Level: {result['readability']['average_grade_level']}")
    print(f"\nStructure:")
    print(f"  Atomicity Score: {result['structure']['atomicity_score']}")
    print(f"  Completeness Score: {result['structure']['completeness_score']}")
    print(f"\nCognitive Complexity:")
    print(f"  Cognitive Load: {result['cognitive']['cognitive_load_score']}")
