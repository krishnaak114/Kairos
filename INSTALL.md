# Installation Guide - Kairos

## Quick Start (Recommended)

### Windows
```bat
# Simply run the setup script
setup.bat
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

## Manual Installation

### Prerequisites
- Python 3.11-3.13 (fully tested and supported)
- pip (Python package manager)

### Installation Options

#### Option 1: System-Wide Installation (Simplest)
```bash
# Install required packages globally
pip install pydantic pydantic-settings pytest pytest-cov fastapi uvicorn python-multipart python-dateutil

# Run the application
python -m app.main --file data/events.json --interval 60 --allowed-misses 3
```

#### Option 2: Virtual Environment (Isolated)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m app.main --file data/events.json --interval 60 --allowed-misses 3
```

## Troubleshooting

### Issue: pydantic-core compilation error (Rust required)

**Problem**: You see an error about Rust/Cargo not being installed when installing pydantic.

**Note**: This issue is resolved in Kairs v1.0.1+ which uses Pydantic 2.10+ with pre-built wheels for all platforms.

**Solution 1** (Recommended): Update to latest Pydantic:
```bash
pip install "pydantic>=2.10.0"
```

**Solution 2**: Use pre-built binaries only:
```bash
pip install --only-binary :all: pydantic
```

**Solution 3**: Use Python packages from your system (if already installed):
```bash
# Check if pydantic is already available
python -c "import pydantic; print(pydantic.__version__)"

# If yes, just use it directly without creating a venv
python -m app.main --file data/events.json
```

### Issue: Character encoding errors in batch files

**Problem**: You see garbled characters like  instead of [OK]

**Solution**: The batch files now use ASCII encoding. Run them using:
```bat
cmd /c setup.bat
```

Or simply double-click setup.bat from Windows Explorer.

### Issue: Module not found errors

**Problem**: ModuleNotFoundError: No module named 'pydantic'

**Solution**: Install the missing package:
```bash
pip install pydantic pydantic-settings
```

### Issue: pytest not found

**Problem**: No module named pytest

**Solution**:
```bash
pip install pytest pytest-cov
```

## Verification

After installation, verify everything works:

```bash
# Run tests
python -m pytest tests/ -v

# Run CLI
python -m app.main --file data/events.json --interval 60 --allowed-misses 3

# Get JSON output
python -m app.main --file data/events.json --interval 60 --allowed-misses 3 --json --quiet
```

Expected output: 7 alerts detected from the sample data.

## Docker Installation (Alternative)

If you prefer Docker:

```bash
# Build image
docker build -t kairos .

# Run with sample data
docker run --rm -v \C:\SAV_REPOS\kairos/data:/data kairos --file /data/events.json --interval 60 --allowed-misses 3

# Or use docker-compose
docker-compose up -d
```

## Need Help?

- Check [README.md](README.md) for usage examples
- See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
- Review [docs/API.md](docs/API.md) for API documentation
- Contact: kagrawalk510@gmail.com

**Author**: Krishna Agrawal  
**GitHub**: https://github.com/krishnaak114
