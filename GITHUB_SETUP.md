# GitHub Setup Instructions

## Repository Ready to Push!

Your `understanding` package is ready to be pushed to GitHub.

---

## Quick Setup (5 minutes)

### Step 1: Create GitHub Repository

1. Go to: **https://github.com/new**
2. Set these options:
   - **Repository name**: `understanding`
   - **Description**: `31 scientifically-proven requirements quality metrics with optional energy-based analysis`
   - **Visibility**: Public (recommended) or Private
   - **DO NOT** initialize with README, license, or .gitignore (we have them)
3. Click **"Create repository"**

### Step 2: Push to GitHub

GitHub will show you commands. Use these:

```bash
cd /Users/ladislavbihari/myWork/qag-spec-kit/understanding

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/Testimonial/understanding.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Example** (if your username is `ladislavbihari`):
```bash
git remote add origin https://github.com/ladislavbihari/understanding.git
git branch -M main
git push -u origin main
```

---

## What's Already Done

- Git repository initialized
- All files staged and committed
- Comprehensive commit message with full details
- .gitignore configured (excludes venv, cache, etc.)
- README.md ready (will display on GitHub)

---

## Installing from GitHub

Once pushed, anyone (including you) can install it:

### Option 1: Install as Tool (Recommended)

```bash
# Install directly from GitHub
uv tool install git+https://github.com/Testimonial/understanding.git

# Now available system-wide
understanding scan specs/001-feature/spec.md
```

### Option 2: Install in Project

```bash
# Install in your project's virtual environment
cd /path/to/your/project
uv pip install git+https://github.com/Testimonial/understanding.git

# Use in that project
understanding scan specs/001-feature/spec.md
```

### Option 3: Install with Energy Metrics

```bash
# Install with optional energy-based analysis (requires ~270MB model download)
uv tool install "understanding[energy]" --from git+https://github.com/Testimonial/understanding.git
```

### Option 4: Install in Editable Mode (Development)

```bash
# Clone the repo
git clone https://github.com/Testimonial/understanding.git
cd understanding

# Install in editable mode
uv pip install -e .

# Make changes, they're immediately available
understanding scan test.md
```

---

## Using with Spec Kit

Both tools work together seamlessly:

```bash
# Install official Spec Kit
uv tool install git+https://github.com/github/spec-kit.git

# Install understanding metrics
uv tool install git+https://github.com/Testimonial/understanding.git

# Use together
specify init my-project --ai claude
cd my-project

# Create specification with Spec Kit
specify init . --ai claude
# ... write spec.md ...

# Validate quality with metrics
understanding scan specs/001-feature/spec.md
understanding validate specs/001-feature/spec.md

# If quality gates pass, continue with Spec Kit
specify plan
specify tasks
specify implement
```

---

## Repository Structure on GitHub

Once pushed, your repo will look like this:

```
github.com/Testimonial/understanding/
├── README.md                     # Displays as home page
├── LICENSE                       # MIT License badge
├── docs/                         # Documentation folder
│   ├── ENHANCED_METRICS_COMPLETE_REFERENCE.md
│   ├── METRICS_OUTPUT_REFERENCE.md
│   ├── METRICS_QUICK_REFERENCE.md
│   └── ...
├── src/understanding/            # Source code
│   ├── cli.py
│   ├── enhanced_metrics.py
│   ├── energy_metrics.py
│   └── ...
└── pyproject.toml                # Package config
```

---

## Add Topics/Tags (Optional)

After pushing, add topics to your GitHub repo for discoverability:

1. Go to your repo page
2. Click the gear icon or edit topics
3. Add these topics:
   - `requirements-engineering`
   - `quality-metrics`
   - `spec-kit`
   - `requirements-analysis`
   - `python`
   - `cli`
   - `validation`
   - `scientific`
   - `energy-metrics`

---

## Making Updates Later

When you make changes:

```bash
cd /Users/ladislavbihari/myWork/qag-spec-kit/understanding

# Make your changes to code/docs
vim src/understanding/cli.py

# Commit and push
git add .
git commit -m "Add new feature: X"
git push
```

Users can update by reinstalling:
```bash
uv tool uninstall understanding
uv tool install git+https://github.com/Testimonial/understanding.git
```

---

## Installation Example for Others

Once pushed, share these instructions:

**Quick Install:**
```bash
uv tool install git+https://github.com/Testimonial/understanding.git
```

**Verify:**
```bash
understanding version
```

**Use:**
```bash
understanding scan path/to/spec.md
understanding validate path/to/spec.md
```

---

## Troubleshooting

### Authentication Required
If GitHub asks for credentials when pushing:

```bash
# Use Personal Access Token (classic)
# 1. Go to: https://github.com/settings/tokens
# 2. Generate new token (classic)
# 3. Select scopes: repo (all)
# 4. Use token as password when prompted
```

Or use SSH:
```bash
# If you have SSH keys set up
git remote set-url origin git@github.com:Testimonial/understanding.git
git push -u origin main
```

### Push Rejected
If you get "rejected" error:
```bash
# Pull first (shouldn't happen on new repo, but just in case)
git pull origin main --rebase
git push -u origin main
```

---

## Verification Checklist

After pushing, verify:

- [ ] Repo is visible at github.com/Testimonial/understanding
- [ ] README.md displays correctly on home page
- [ ] All files are present (src/, docs/, etc.)
- [ ] Can install via: `uv tool install git+https://...`
- [ ] Command works: `understanding version`

---

## Done!

Once pushed to GitHub:
1. Package is publicly available
2. Anyone can install it
3. You can use it in any project
4. Ready to request official Spec Kit extension status

**Next**: Push to GitHub, then test installation from the URL!
