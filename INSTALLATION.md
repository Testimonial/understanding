# Installation Guide

## Quick Install

### Using uv (Recommended)

```bash
uv tool install understanding
```

### Using pip

```bash
pip install understanding
```

### With NLP Enhancement (Optional)

```bash
# Better semantic analysis with spaCy
uv tool install "understanding[nlp]"

# Download spaCy model
python -m spacy download en_core_web_sm
```

### With Energy Dependencies (Optional)

```bash
pip install "understanding[energy]"
```

---

## Installation from Source

### For Users

```bash
# Clone repository
git clone https://github.com/Testimonial/understanding.git
cd understanding

# Install
uv pip install .

# Or with pip
pip install .
```

### For Developers

```bash
# Clone repository
git clone https://github.com/Testimonial/understanding.git
cd understanding

# Install in development mode
uv pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=understanding --cov-report=html
```

---

## Verify Installation

```bash
# Check version
understanding version

# Should output:
# understanding version 3.4.0
# 31 scientifically-proven requirements quality metrics

# Run help
understanding --help
```

---

## Usage with Spec Kit

Install both tools:

```bash
# Install Spec Kit (official)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Install Understanding
uv tool install understanding

# Verify both installed
specify --version
understanding version
```

Use together:

```bash
# Create project with Spec Kit
specify init my-project --ai claude
cd my-project

# Create specification
# ... (use Spec Kit workflow)

# Validate quality
understanding scan specs/001-feature/spec.md

# If quality gates pass, continue with Spec Kit
specify plan
specify tasks
specify implement
```

---

## Troubleshooting

### Command not found

If `understanding` is not found:

```bash
# Check if uv tool bin directory is in PATH
echo $PATH | grep .local/bin

# Add to PATH if needed (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
```

### Import errors

If you get import errors:

```bash
# Reinstall with force
uv tool uninstall understanding
uv tool install understanding

# Or check Python version
python --version  # Should be 3.11+
```

### spaCy model not found

If using NLP enhancement:

```bash
python -m spacy download en_core_web_sm
```

---

## Uninstall

```bash
# Using uv
uv tool uninstall understanding

# Using pip
pip uninstall understanding
```

---

## System Requirements

- **Python**: 3.11 or higher
- **OS**: Linux, macOS, Windows
- **Memory**: ~50MB
- **Dependencies**: typer, rich (installed automatically)
- **Optional**: spacy (for enhanced semantic analysis)
