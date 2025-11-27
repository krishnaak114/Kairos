# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Database persistence for alert history
- Real-time WebSocket notifications
- Prometheus metrics endpoint
- Grafana dashboard templates
- Multi-tenancy support
- Custom alert rules engine
- Email/SMS notification integrations
- Historical trend analysis
- Anomaly detection with ML

---

## [1.0.0] - 2025-11-27

### Added
- ✨ Core Kair�sing engine
- ✨ CLI interface for processing JSON files
- ✨ Optional FastAPI server mode for production deployments
- ✨ Pydantic data models with runtime validation
- ✨ Comprehensive error handling and graceful degradation
- ✨ Support for multiple services with independent tracking
- ✨ Configurable thresholds (interval, allowed misses, tolerance)
- ✨ Detailed validation reporting for malformed events
- ✨ JSON output format for programmatic consumption
- ✨ Structured logging with configurable levels
- ✨ Docker and Docker Compose support
- ✨ Multi-stage Docker builds for production
- ✨ Health check endpoints for load balancers
- ✨ CORS support for cross-origin requests
- ✨ Environment variable configuration
- ✨ Optional PostgreSQL database integration
- ✨ Optional Redis caching support
- ✨ Comprehensive test suite (15 tests, 100% pass rate)
- ✨ Type hints throughout codebase (mypy compatible)
- ✨ CI/CD workflows (GitHub Actions)
- ✨ Automated testing across Python 3.11, 3.12, 3.13
- ✨ Multi-OS testing (Ubuntu, Windows, macOS)
- ✨ Docker image publishing workflow
- ✨ Security scanning with Bandit and Trivy
- ✨ Code quality checks (Black, Flake8, mypy)
- ✨ Coverage reporting with pytest-cov
- 📚 Comprehensive README with examples
- 📚 Architecture documentation (ARCHITECTURE.md)
- 📚 API documentation (API.md)
- 📚 Contributing guidelines (CONTRIBUTING.md)
- 📚 OpenAPI/Swagger documentation
- 📚 Docker deployment examples
- 📚 Kubernetes deployment manifests
- 🛠️ Setup scripts for Windows and Linux/Mac
- 🛠️ Example .env configuration file
- 🛠️ Sample events.json test data
- 🛠️ .gitignore for Python projects
- 🛠️ requirements.txt with pinned versions

### Features in Detail

#### Core Monitoring
- Detects consecutive missed heartbeats (configurable threshold)
- Handles unordered input (automatic sorting)
- Service-independent tracking (no cross-contamination)
- Tolerance window for late heartbeats
- Multiple alert detection in single run
- Reset mechanism for tracking new outage periods

#### Data Validation
- Pydantic-based validation with detailed error messages
- Graceful handling of malformed events
- Categorized error reporting (missing fields, invalid formats, etc.)
- Validation statistics in output
- Support for various timestamp formats (ISO 8601)
- Case-insensitive service names

#### CLI Features
- File input support
- Configurable monitoring parameters
- JSON output for automation
- Quiet mode for scripts
- Alert file export
- Verbose logging options
- Color-coded console output

#### API Features (Optional)
- RESTful endpoints
- File upload support (multipart/form-data)
- Interactive API documentation (Swagger UI)
- Health check endpoints
- Error handling middleware
- CORS configuration
- API key authentication
- Request validation
- JSON response formatting

#### DevOps
- Docker containerization
- Docker Compose orchestration
- Multi-stage builds (optimization)
- Health checks in containers
- Volume mounting for data
- Environment variable configuration
- Kubernetes manifests
- CI/CD pipelines
- Automated testing
- Security scanning
- Code quality gates

### Testing
- **15 test cases** covering:
  - Required assignment cases (alert triggered, near-miss, unordered input, malformed events)
  - Multi-service scenarios
  - Edge cases (empty input, single event, exact threshold, recovery)
  - Configuration variations (different intervals, allowed misses, tolerance)
  - Real-world data validation
- **100% test pass rate**
- **Coverage**: Comprehensive (90%+ code coverage)
- **pytest-based** with fixtures and parametrization
- **Continuous Integration** across multiple Python versions and OS platforms

### Documentation
- README with badges, quick start, examples
- Architecture documentation with diagrams
- API reference with code examples
- Contributing guidelines with workflows
- Docker deployment guide
- Kubernetes deployment examples
- Environment configuration reference
- FAQ and troubleshooting
- Code of conduct (implied in CONTRIBUTING.md)

### Security
- Input validation at every layer
- File upload size limits
- API key authentication support
- CORS configuration
- No hardcoded secrets
- Environment variable for sensitive data
- Dependency vulnerability scanning
- Container security scanning

### Performance
- O(n log n) time complexity
- Efficient grouping by service
- Minimal memory overhead
- Fast JSON parsing
- Processing time tracking
- Optimized Docker images
- Multi-worker support in API mode

---

## [0.1.0] - Development Phase

### Added
- Initial project scaffolding
- Basic algorithm implementation
- Test data generation
- Development environment setup

---

## Version History Summary

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2025-11-27 | Initial production release |
| 0.1.0 | Development | Development phase |

---

## Upgrade Guide

### From 0.x to 1.0

This is the initial release, so no migration is needed.

---

## Deprecation Notices

None currently.

---

## Breaking Changes

None in this release.

---

## Known Issues

None currently. Please report issues at: https://github.com/krishnaak114/kairos/issues

---

## Contributors

- **Krishna Agrawal** - *Initial work* - [@krishnaak114](https://github.com/krishnaak114)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Author**: Krishna Agrawal  
**Contact**: kagrawalk510@gmail.com  
**LinkedIn**: [Krishna Agrawal](https://www.linkedin.com/in/agrawal-krishna-aa11a61ba/)  
**GitHub**: [@krishnaak114](https://github.com/krishnaak114)
