#!/bin/bash

# Comprehensive Verification Script
# Validates the entire Kair�s setup

set -e

echo "=================================="
echo "🔍 Kair�s Verification"
echo "=================================="
echo ""

PASSED=0
FAILED=0

# Function to check command result
check_result() {
    if [ $? -eq 0 ]; then
        echo "✅ PASSED: $1"
        ((PASSED++))
    else
        echo "❌ FAILED: $1"
        ((FAILED++))
    fi
    echo ""
}

# 1. Check Python version
echo "1️⃣  Checking Python version..."
python3 --version
check_result "Python installation"

# 2. Check virtual environment
echo "2️⃣  Checking virtual environment..."
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists"
    ((PASSED++))
else
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
    check_result "Virtual environment creation"
fi
echo ""

# 3. Activate virtual environment
echo "3️⃣  Activating virtual environment..."
source venv/bin/activate
check_result "Virtual environment activation"

# 4. Check dependencies
echo "4️⃣  Checking dependencies..."
pip list | grep -E "pydantic|fastapi|pytest" > /dev/null
check_result "Required packages installed"

# 5. Check project structure
echo "5️⃣  Checking project structure..."
REQUIRED_DIRS=("app" "tests" "data" "docs" ".github/workflows")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir/"
    else
        echo "  ✗ $dir/ MISSING"
        ((FAILED++))
    fi
done
echo ""

# 6. Check required files
echo "6️⃣  Checking required files..."
REQUIRED_FILES=(
    "README.md"
    "LICENSE"
    "requirements.txt"
    "Dockerfile"
    "docker-compose.yml"
    "app/main.py"
    "app/models.py"
    "app/monitor.py"
    "app/config.py"
    "tests/test_monitor.py"
    "data/events.json"
)
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file MISSING"
        ((FAILED++))
    fi
done
echo ""

# 7. Run linting (if available)
echo "7️⃣  Checking code quality..."
if command -v black &> /dev/null; then
    black --check app/ tests/ > /dev/null 2>&1
    check_result "Black formatting"
else
    echo "⚠️  Black not installed (optional)"
    echo ""
fi

# 8. Run type checking (if available)
echo "8️⃣  Checking type hints..."
if command -v mypy &> /dev/null; then
    mypy app/ --ignore-missing-imports > /dev/null 2>&1
    check_result "Type checking"
else
    echo "⚠️  mypy not installed (optional)"
    echo ""
fi

# 9. Run tests
echo "9️⃣  Running test suite..."
python -m pytest tests/ -v --tb=short
check_result "Test suite"

# 10. Test CLI functionality
echo "🔟 Testing CLI functionality..."
python -m app.main --file data/events.json --interval 60 --allowed-misses 3 --quiet
check_result "CLI execution"

# 11. Test JSON output
echo "1️⃣1️⃣  Testing JSON output..."
python -m app.main --file data/events.json --interval 60 --allowed-misses 3 --json --quiet > /dev/null
check_result "JSON output"

# 12. Check Docker (if available)
echo "1️⃣2️⃣  Checking Docker setup..."
if command -v docker &> /dev/null; then
    docker build -t kairos:test . > /dev/null 2>&1
    check_result "Docker build"
else
    echo "⚠️  Docker not installed (optional)"
    echo ""
fi

# Summary
echo "=================================="
echo "📊 Verification Summary"
echo "=================================="
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All checks passed! Project is ready."
    echo ""
    echo "Next steps:"
    echo "  1. Run CLI: python -m app.main --file data/events.json"
    echo "  2. Run API: python -m app.main --api --port 8000"
    echo "  3. Run tests: pytest tests/ -v"
    echo "  4. Build Docker: docker build -t kairos ."
    echo "  5. Deploy: docker-compose up -d"
    echo ""
    exit 0
else
    echo "⚠️  Some checks failed. Please review the output above."
    echo ""
    exit 1
fi
