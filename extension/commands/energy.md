---
description: "[Experimental] Detect ambiguity hotspots using token-level perplexity from a local language model. A second pair of eyes beyond the 31 rule-based metrics."
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Run experimental energy-based ambiguity detection on the spec. This uses a local language model (SmolLM2-135M) to find phrases that are "surprising" — correlating with vague, ambiguous, or oddly worded requirements that the 31 rule-based metrics might miss.

## Prerequisites

Energy metrics require additional dependencies:

```bash
pip install "understanding[energy]"
# or with uv:
uv tool install git+https://github.com/Testimonial/understanding.git \
  --with "spacy>=3.0.0" \
  --with "transformers>=4.30.0" \
  --with "torch>=2.0.0"
```

First run downloads ~270MB model. No API keys needed.

## Execution Steps

### 1. Locate Spec

```bash
SPEC_PATH="${ARGUMENTS:-}"

if [ -z "$SPEC_PATH" ]; then
  SPECS_DIR="specs"
  if [ -d "$SPECS_DIR" ]; then
    LATEST=$(ls -d "$SPECS_DIR"/[0-9]*/ 2>/dev/null | sort -r | head -1)
    SPEC_PATH="${LATEST}spec.md"
  fi
fi

if [ ! -f "$SPEC_PATH" ]; then
  echo "No spec.md found."
  exit 1
fi
```

### 2. Run Energy Analysis

```bash
understanding "$SPEC_PATH" --energy
```

### 3. Interpret Results

Energy metrics produce 5 scores (all 0-1, higher = clearer):

| Metric | What It Means |
|--------|--------------|
| **Mean Energy** | Overall — how well the text fits standard language patterns |
| **Max Energy** | Worst spot — the single most surprising/ambiguous token |
| **Dispersion** | Uniformity — is difficulty spread evenly or concentrated? |
| **Anchor Ratio** | Clarity — what % of tokens are easy and well-predicted? |
| **Tail Ratio** | Ambiguity — what % of tokens are highly surprising? |

**Score interpretation:**
- >= 80%: Clear — language model finds requirements predictable
- 60-79%: Some ambiguity — unusual phrasing in places
- < 60%: High ambiguity — many surprising phrases, likely vague wording

**Hotspot tokens** show the specific words/phrases the model found most surprising. These are candidates for rewriting.

### 4. Relationship to 31 Metrics

The 31 metrics are a rule-based inspector. Energy is a second pair of eyes.

A requirement can score 0.90 on the 31 metrics (good structure, readable, testable) but the energy model spots a phrase that's oddly worded or domain-novel. The 31 metrics tell you *what* is wrong. Energy tells you *where* the ambiguity hides.

Energy scores are NOT part of the 31-metric score or quality gates. They are a separate, experimental overlay.

## Notes

- This feature is **experimental** — scores may vary across model versions
- Energy analysis adds ~2-5 seconds per spec (model inference)
- No data leaves your machine — the model runs locally
