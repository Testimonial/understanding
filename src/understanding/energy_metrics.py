#!/usr/bin/env python3
"""
Energy-Based Understanding Metrics - Token-level perplexity analysis.

Uses a small local language model to compute per-token perplexity as a proxy
for the energy-based "understanding difficulty" described in:
- Hinton (1985): Boltzmann Machines - energy as compatibility score
- Friston (2010): Free Energy Principle - brain minimizes surprise
- Gladstone et al. (2025): Energy-Based Transformers - token-level energy

The core insight: high perplexity tokens are "surprising" to the model,
which correlates with ambiguity, unusual phrasing, or domain novelty.

Metrics produced (all 0-1 normalized):
1. M_mean: Mean energy per token (domain fit / plausibility)
2. M_max: Max energy token (localized ambiguity hotspot)
3. M_var: Energy dispersion (heterogeneous vs uniform difficulty)
4. M_anchor: Anchor token ratio (% of low-energy "easy" tokens)
5. M_tail: High-energy tail ratio (% of "hard" tokens)

Requires: pip install understanding[energy]
  (installs transformers + torch)
"""

import math
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# Optional imports — gracefully degrade if not installed
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    ENERGY_AVAILABLE = True
except ImportError:
    ENERGY_AVAILABLE = False


# Default model — small enough for CPU, good enough for relative scoring
DEFAULT_MODEL = "HuggingFaceTB/SmolLM2-135M"

# Singleton model cache to avoid reloading per-file
_model_cache: Dict[str, Tuple] = {}


@dataclass
class TokenEnergy:
    """Energy data for a single token."""

    token: str
    token_id: int
    energy: float  # negative log-prob (higher = more surprising)


@dataclass
class EnergyProfile:
    """Per-requirement energy profile."""

    tokens: List[TokenEnergy]
    mean_energy: float
    max_energy: float
    energy_variance: float
    anchor_ratio: float  # % tokens with energy < threshold (easy tokens)
    tail_ratio: float  # % tokens with energy > threshold (hard tokens)


@dataclass
class EnergyMetrics:
    """Normalized energy metrics (all 0-1, higher = better requirement quality)."""

    mean_energy_score: float  # 1 - normalized mean energy (lower energy = better)
    max_energy_score: float  # 1 - normalized max energy
    dispersion_score: float  # 1 - normalized variance (uniform = better)
    anchor_score: float  # high anchor ratio = mostly easy tokens = good
    tail_score: float  # low tail ratio = few hard tokens = good
    composite_score: float  # weighted average

    # Raw values for diagnostics
    raw_mean_energy: float
    raw_max_energy: float
    raw_variance: float
    raw_anchor_ratio: float
    raw_tail_ratio: float

    # Hotspot tokens (highest energy)
    hotspot_tokens: List[Tuple[str, float]]  # (token_text, energy)

    def to_dict(self) -> Dict:
        return {
            "mean_energy_score": round(self.mean_energy_score, 4),
            "max_energy_score": round(self.max_energy_score, 4),
            "dispersion_score": round(self.dispersion_score, 4),
            "anchor_score": round(self.anchor_score, 4),
            "tail_score": round(self.tail_score, 4),
            "composite_score": round(self.composite_score, 4),
            "raw": {
                "mean_energy": round(self.raw_mean_energy, 4),
                "max_energy": round(self.raw_max_energy, 4),
                "variance": round(self.raw_variance, 4),
                "anchor_ratio": round(self.raw_anchor_ratio, 4),
                "tail_ratio": round(self.raw_tail_ratio, 4),
            },
            "hotspot_tokens": [
                {"token": t, "energy": round(e, 4)} for t, e in self.hotspot_tokens
            ],
        }


def _load_model(model_name: str = DEFAULT_MODEL):
    """Load model and tokenizer (cached after first call)."""
    if not ENERGY_AVAILABLE:
        raise ImportError(
            "Energy metrics require transformers and torch. "
            "Install with: pip install understanding[energy]"
        )

    if model_name not in _model_cache:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
        )
        model.eval()

        # Set pad token if missing
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        _model_cache[model_name] = (model, tokenizer)

    return _model_cache[model_name]


def compute_token_energies(
    text: str,
    model_name: str = DEFAULT_MODEL,
) -> EnergyProfile:
    """
    Compute per-token energy (negative log-probability) for input text.

    Args:
        text: The requirement text to analyze.
        model_name: HuggingFace model identifier.

    Returns:
        EnergyProfile with per-token energy data.
    """
    model, tokenizer = _load_model(model_name)

    # Tokenize
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    input_ids = inputs["input_ids"]

    # Forward pass — get logits
    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits  # (1, seq_len, vocab_size)

    # Compute per-token negative log-likelihood
    # Shift: logits[t] predicts token[t+1]
    shift_logits = logits[:, :-1, :].contiguous()
    shift_labels = input_ids[:, 1:].contiguous()

    log_probs = torch.nn.functional.log_softmax(shift_logits, dim=-1)
    token_log_probs = log_probs.gather(
        dim=-1, index=shift_labels.unsqueeze(-1)
    ).squeeze(-1)

    # Energy = negative log-prob (higher = more surprising)
    token_energies = (-token_log_probs.squeeze(0)).tolist()

    # Build token list (skip first token — no prediction for it)
    tokens = []
    all_token_ids = input_ids.squeeze(0).tolist()
    for i, (tid, energy) in enumerate(zip(all_token_ids[1:], token_energies)):
        token_text = tokenizer.decode([tid])
        tokens.append(TokenEnergy(token=token_text, token_id=tid, energy=energy))

    if not tokens:
        return EnergyProfile(
            tokens=[],
            mean_energy=0.0,
            max_energy=0.0,
            energy_variance=0.0,
            anchor_ratio=1.0,
            tail_ratio=0.0,
        )

    # Compute summary statistics
    energies = [t.energy for t in tokens]
    n = len(energies)
    mean_e = sum(energies) / n
    max_e = max(energies)
    variance = sum((e - mean_e) ** 2 for e in energies) / n

    # Anchor tokens: energy < 2.0 (common, well-predicted tokens)
    # This threshold is based on typical LM behavior where
    # log-prob > -2.0 means > 13.5% probability
    anchor_threshold = 2.0
    anchor_count = sum(1 for e in energies if e < anchor_threshold)
    anchor_ratio = anchor_count / n

    # Tail tokens: energy > 8.0 (very surprising, potential ambiguity)
    # log-prob < -8.0 means < 0.03% probability
    tail_threshold = 8.0
    tail_count = sum(1 for e in energies if e > tail_threshold)
    tail_ratio = tail_count / n

    return EnergyProfile(
        tokens=tokens,
        mean_energy=mean_e,
        max_energy=max_e,
        energy_variance=variance,
        anchor_ratio=anchor_ratio,
        tail_ratio=tail_ratio,
    )


def _normalize_energy(value: float, low: float, high: float) -> float:
    """Normalize a value to 0-1 range using known bounds, then invert (lower energy = better)."""
    if high <= low:
        return 1.0
    clamped = max(low, min(high, value))
    normalized = (clamped - low) / (high - low)
    return 1.0 - normalized  # invert: low energy = high score


def analyze_energy(
    text: str,
    model_name: str = DEFAULT_MODEL,
) -> EnergyMetrics:
    """
    Analyze requirement text and produce normalized energy metrics.

    All scores are 0-1 where higher = better quality requirement.

    Args:
        text: Requirement text to analyze.
        model_name: HuggingFace model identifier.

    Returns:
        EnergyMetrics with 5 normalized scores + composite.
    """
    profile = compute_token_energies(text, model_name=model_name)

    if not profile.tokens:
        return EnergyMetrics(
            mean_energy_score=0.5,
            max_energy_score=0.5,
            dispersion_score=0.5,
            anchor_score=0.5,
            tail_score=0.5,
            composite_score=0.5,
            raw_mean_energy=0.0,
            raw_max_energy=0.0,
            raw_variance=0.0,
            raw_anchor_ratio=0.0,
            raw_tail_ratio=0.0,
            hotspot_tokens=[],
        )

    # Normalization ranges (empirically reasonable for small LMs on English text)
    # These may need calibration — see calibration section in docs
    mean_score = _normalize_energy(profile.mean_energy, low=1.0, high=8.0)
    max_score = _normalize_energy(profile.max_energy, low=2.0, high=15.0)
    dispersion_score = _normalize_energy(profile.energy_variance, low=0.5, high=20.0)

    # Anchor and tail are already ratios — just use directly
    anchor_score = min(1.0, profile.anchor_ratio)  # more anchors = better
    tail_score = 1.0 - min(1.0, profile.tail_ratio)  # fewer tails = better

    # Composite: weighted average
    # Mean and max energy are the strongest signals
    composite = (
        0.30 * mean_score
        + 0.25 * max_score
        + 0.15 * dispersion_score
        + 0.15 * anchor_score
        + 0.15 * tail_score
    )

    # Find hotspot tokens (top 5 highest energy)
    sorted_tokens = sorted(profile.tokens, key=lambda t: t.energy, reverse=True)
    hotspots = [(t.token.strip(), t.energy) for t in sorted_tokens[:5]]

    return EnergyMetrics(
        mean_energy_score=mean_score,
        max_energy_score=max_score,
        dispersion_score=dispersion_score,
        anchor_score=anchor_score,
        tail_score=tail_score,
        composite_score=composite,
        raw_mean_energy=profile.mean_energy,
        raw_max_energy=profile.max_energy,
        raw_variance=profile.energy_variance,
        raw_anchor_ratio=profile.anchor_ratio,
        raw_tail_ratio=profile.tail_ratio,
        hotspot_tokens=hotspots,
    )


def analyze_energy_batch(
    texts: List[str],
    model_name: str = DEFAULT_MODEL,
) -> List[EnergyMetrics]:
    """Analyze multiple requirements and return energy metrics for each."""
    # Load model once (cached)
    _load_model(model_name)
    return [analyze_energy(text, model_name=model_name) for text in texts]


def is_energy_available() -> bool:
    """Check if energy metrics dependencies are installed."""
    return ENERGY_AVAILABLE
