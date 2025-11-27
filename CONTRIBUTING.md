#  Contributing to Kairs

First off, thank you for considering contributing to Kairs! It's people like you that make this project a great tool for the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Documentation](#documentation)

---

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow:

- **Be respectful**: Treat everyone with respect and kindness
- **Be collaborative**: Work together constructively
- **Be patient**: Help newcomers learn and grow
- **Be inclusive**: Welcome diverse perspectives and backgrounds

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Virtual environment tool (venv, conda, etc.)
- Basic understanding of pytest and FastAPI (optional)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/krishnaak114/kairos.git
cd kairos

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (including dev dependencies)
pip install -r requirements.txt
pip install black flake8 mypy pytest-benchmark

# Run tests to verify setup
pytest tests/ -v

# Run the application
python -m app.main --file data/events.json --interval 60 --allowed-misses 3
```

---

## Development Workflow

### 1. Fork and Clone

```bash
# Fork the repo on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/kairos.git
cd kairos

# Add upstream remote
git remote add upstream https://github.com/krishnaak114/kairos.git
```

### 2. Create a Branch

```bash
# Always work on a feature branch
git checkout -b feature/your-feature-name
# Or for bug fixes
git checkout -b bugfix/issue-number-description
```

Branch naming conventions:
- `feature/add-webhook-notifications`
- `bugfix/fix-timezone-handling`
- `docs/update-api-documentation`
- `refactor/improve-validation-logic`

### 3. Make Changes

- Write clean, readable code
- Follow existing code style
- Add tests for new features
- Update documentation as needed

### 4. Test Your Changes

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term

# Run specific test file
pytest tests/test_monitor.py -v

# Run linting
black app/ tests/ --check
flake8 app/ tests/ --max-line-length=100
mypy app/ --ignore-missing-imports
```

### 5. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a clear message
git commit -m "feat: add webhook notification support"
```

**Commit message format** (following Conventional Commits):

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(monitor): add support for custom intervals per service
fix(validation): handle null timestamp values correctly
docs(readme): add docker deployment instructions
test(monitor): add edge case tests for timezone handling
```

### 6. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

---

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Quotes**: Use double quotes for strings
- **Formatting**: Use Black for automatic formatting
- **Imports**: Organize imports using isort

```python
# Good
from datetime import datetime, timedelta
from typing import List, Optional

from app.models import HeartbeatEvent
from app.utils import logger


class HeartbeatMonitor:
    """Monitor for detecting missed heartbeats."""
    
    def __init__(self, config: MonitorConfig) -> None:
        self.config = config
```

### Type Hints

**Always use type hints** for function signatures:

```python
#  Good
def detect_alerts(self, events: List[HeartbeatEvent]) -> List[Alert]:
    """Detect alerts from events."""
    pass

#  Bad
def detect_alerts(self, events):
    pass
```

### Documentation

Use docstrings for all public functions and classes:

```python
def validate_events(self, raw_events: List[dict]) -> Tuple[List[HeartbeatEvent], ValidationResult]:
    """
    Validate and filter events.
    
    Args:
        raw_events: List of raw event dictionaries
        
    Returns:
        Tuple of (valid_events, validation_result)
        
    Raises:
        ValidationError: If critical validation fails
        
    Example:
        >>> events = [{"service": "email", "timestamp": "2025-08-04T10:00:00Z"}]
        >>> valid, result = monitor.validate_events(events)
    """
    pass
```

### Error Handling

```python
#  Good - Specific exception handling
try:
    event = HeartbeatEvent(**raw_event)
except ValidationError as e:
    logger.warning(f"Invalid event: {e}")
    continue
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise

#  Bad - Bare except
try:
    event = HeartbeatEvent(**raw_event)
except:
    pass
```

---

## Testing Guidelines

### Test Structure

```python
class TestFeatureName:
    """Tests for feature X."""
    
    def test_basic_case(self):
        """Test the basic/happy path."""
        pass
    
    def test_edge_case_empty_input(self):
        """Test with empty input."""
        pass
    
    def test_error_handling(self):
        """Test error conditions."""
        pass
```

### Test Coverage

- Aim for **>90% code coverage**
- Write tests for:
  - Happy path cases
  - Edge cases
  - Error conditions
  - Integration scenarios

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_monitor.py::TestRequiredCases::test_alert_triggered -v

# Run tests matching pattern
pytest tests/ -k "alert" -v
```

### Test Fixtures

Use pytest fixtures for common setup:

```python
@pytest.fixture
def monitor_config():
    """Default monitor configuration."""
    return MonitorConfig(
        expected_interval_seconds=60,
        allowed_misses=3
    )

@pytest.fixture
def sample_events():
    """Sample heartbeat events."""
    return [
        {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
        {"service": "email", "timestamp": "2025-08-04T10:01:00Z"}
    ]
```

---

## Pull Request Process

### Before Submitting

1.  Run all tests: `pytest tests/ -v`
2.  Check code style: `black app/ tests/ --check`
3.  Run linting: `flake8 app/ tests/`
4.  Type check: `mypy app/`
5.  Update documentation
6.  Add tests for new features
7.  Update CHANGELOG.md

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of the change

## Motivation and Context
Why is this change needed? What problem does it solve?

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that breaks existing functionality)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran

## Checklist
- [ ] My code follows the code style of this project
- [ ] I have updated the documentation
- [ ] I have added tests to cover my changes
- [ ] All new and existing tests passed
- [ ] My changes generate no new warnings
```

### Review Process

1. CI checks must pass
2. At least one maintainer approval required
3. All comments addressed
4. Documentation updated
5. Tests added/updated

---

## Reporting Bugs

### Before Reporting

1. Check if the bug has already been reported in [Issues](https://github.com/krishnaak114/kairos/issues)
2. Ensure you're using the latest version
3. Verify the bug occurs with minimal code

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## To Reproduce
Steps to reproduce:
1. Run command '...'
2. With input '...'
3. See error

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Environment
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11.5]
- Package version: [e.g., 1.0.0]

## Additional Context
Logs, screenshots, etc.
```

---

## Suggesting Enhancements

### Feature Request Template

```markdown
## Problem Statement
What problem does this feature solve?

## Proposed Solution
How should this feature work?

## Alternatives Considered
What other solutions did you consider?

## Additional Context
Examples, mockups, etc.
```

---

## Documentation

### Types of Documentation

1. **Code comments**: Explain *why*, not *what*
2. **Docstrings**: Explain *what* functions/classes do
3. **README**: Getting started guide
4. **Architecture docs**: System design
5. **API docs**: Endpoint reference

### Documentation Standards

```python
#  Good comment - explains WHY
# Reset counter after alert to detect subsequent outage periods
consecutive_misses = 0

#  Bad comment - explains WHAT (obvious from code)
# Set consecutive_misses to 0
consecutive_misses = 0
```

---

## Development Tips

### Running in Development Mode

```bash
# Use debug logging
export LOG_LEVEL=DEBUG
python -m app.main --file data/events.json

# Run with auto-reload (API mode)
uvicorn app.main:app --reload --port 8000
```

### Debugging

```python
# Use breakpoint() for debugging
def detect_alerts(self, events):
    breakpoint()  # Debugger will stop here
    sorted_events = sorted(events, key=lambda e: e.timestamp)
```

### Performance Testing

```bash
# Run benchmarks
pytest tests/ -m benchmark -v

# Profile code
python -m cProfile -o profile.stats app/main.py
```

---

## Questions?

-  Email: kagrawalk510@gmail.com
-  LinkedIn: [Krishna Agrawal](https://www.linkedin.com/in/agrawal-krishna-aa11a61ba/)
-  GitHub: [@krishnaak114](https://github.com/krishnaak114)

---

Thank you for contributing! 

**Author**: Krishna Agrawal  
**Version**: 1.0.0  
**Last Updated**: November 27, 2025
