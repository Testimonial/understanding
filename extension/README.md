# Understanding — Spec Kit Extension

Requirements quality metrics as a [Spec Kit](https://github.com/github/spec-kit) extension.

## What It Does

Adds three slash commands to your AI agent:

| Command | Description |
|---------|-------------|
| `/speckit.understanding.scan` | Scan spec for 31 quality metrics with entity analysis |
| `/speckit.understanding.validate` | Enforce quality gates (ISO 29148, IEEE 830) |
| `/speckit.understanding.energy` | [Experimental] Token-level ambiguity detection |

## Installation

### 1. Install the understanding CLI tool

```bash
uv tool install git+https://github.com/Testimonial/understanding.git \
  --with "spacy>=3.0.0" \
  --with "graphviz>=0.20.0"

# Download spaCy model
uv pip install --python ~/.local/share/uv/tools/understanding/bin/python \
  en-core-web-sm@https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

### 2. Install the extension

```bash
# From local clone
specify extension add --dev /path/to/understanding/extension

# Or from GitHub (after release)
specify extension add --from https://github.com/Testimonial/understanding/archive/refs/tags/v3.4.0.zip
```

### 3. Verify

```bash
specify extension list
# Should show: Understanding (v3.4.0)
```

## Usage

In your AI agent (Claude, Copilot, etc.):

```
/speckit.understanding.scan
/speckit.understanding.scan specs/001-feature/spec.md
/speckit.understanding.validate
/speckit.understanding.energy
```

## Hook

After `/speckit.tasks` completes, you'll be prompted:

> Run requirements quality validation on the spec?

This runs `/speckit.understanding.validate` to check quality gates before you proceed to implementation.

## Standalone Usage

Understanding also works as a standalone CLI tool without Spec Kit:

```bash
understanding spec.md
understanding spec.md --validate
understanding specs/ --energy
```

See the [main README](../README.md) for full standalone documentation.

## Quality Gates

| Gate | Threshold | Standard |
|------|-----------|----------|
| Overall | >= 0.70 | ISO 29148:2018 |
| Structure | >= 0.70 | ISO 29148 S5.2.5 |
| Testability | >= 0.70 | ISO 29148 (mandatory) |
| Semantic | >= 0.60 | Lucassen 2017 |
| Cognitive | >= 0.60 | Sweller 1988 |
| Readability | >= 0.50 | Flesch 1948 |

## License

MIT
