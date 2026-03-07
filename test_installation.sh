#!/bin/bash
# Test script to verify package installation

echo "=== Testing understanding-enhanced Installation ==="
echo

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Not in package directory (pyproject.toml not found)"
    exit 1
fi

# Test 1: Create virtual environment if needed
echo "Test 1: Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    uv venv || { echo "❌ Failed to create venv"; exit 1; }
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi
echo

# Test 2: Install in development mode
echo "Test 2: Installing package in development mode..."
uv pip install -e . || { echo "❌ Installation failed"; exit 1; }
echo "✓ Installation successful"
echo

# Test 3: Check command exists (using uv run to activate venv)
echo "Test 3: Checking if command is available..."
uv run which understanding || { echo "❌ Command not found"; exit 1; }
echo "✓ Command found: $(uv run which understanding)"
echo

# Test 4: Test version command
echo "Test 4: Testing version command..."
uv run understanding version || { echo "❌ Version command failed"; exit 1; }
echo "✓ Version command works"
echo

# Test 5: Test help
echo "Test 5: Testing help command..."
uv run understanding --help | grep -q "scientifically-proven" || { echo "❌ Help text incorrect"; exit 1; }
echo "✓ Help command works"
echo

# Test 6: Test scan on sample spec (if exists)
if [ -f "../specs/009-user-notifications/spec.md" ]; then
    echo "Test 6: Testing scan on actual spec..."
    uv run understanding scan ../specs/009-user-notifications/spec.md || { echo "❌ Scan failed"; exit 1; }
    echo "✓ Scan works on actual spec"
else
    echo "Test 6: Skipped (no test spec found at ../specs/009-user-notifications/spec.md)"
fi
echo

echo "=== All Tests Passed! ==="
echo
echo "Package is ready to use!"
echo
echo "Next steps:"
echo "1. Activate venv: source .venv/bin/activate"
echo "2. Try: understanding scan path/to/your/spec.md"
echo "3. Try: understanding validate path/to/your/spec.md"
echo "4. Build package: uv build"
echo "5. Push to GitHub"
