# Contributing to AI Classifier Hub

Thank you for your interest in contributing to the AI Classifier Hub project! This document provides guidelines for contributing to the project.

## Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/fast_api_demo.git
   cd fast_api_demo
   ```

3. **Set up the development environment**:
   ```bash
   # Create virtual environment
   python3 -m venv fastapi_env
   source fastapi_env/bin/activate  # On Windows: fastapi_env\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Run the application** to ensure everything works:
   ```bash
   python server.py
   ```

## Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Write clean, well-documented code
- Follow existing code patterns and conventions
- Add tests for new functionality

### 3. Test Your Changes
```bash
# Run existing tests
python -m pytest

# Test the application manually
python server.py
```

### 4. Commit Your Changes
```bash
git add .
git commit -m "feat: add your feature description"
```

### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with a clear description of your changes.

## Code Guidelines

### Python Code Style
- Follow PEP 8 conventions
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions small and focused

### Testing
- Write tests for new features
- Ensure all tests pass before submitting
- Maintain good test coverage

### Documentation
- Update README.md for new features
- Add docstrings to new functions
- Update relevant documentation files

## Pull Request Guidelines

- **Clear Description**: Explain what changes you made and why
- **Link Issues**: Reference related GitHub issues
- **Small Changes**: Keep PRs focused and reasonably sized
- **Tests**: Include tests for new functionality
- **Documentation**: Update docs as needed

## Reporting Issues

When reporting bugs or requesting features:

1. **Search existing issues** first
2. **Use issue templates** when available
3. **Provide details**:
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - System information
   - Error messages

## Getting Help

- Check the [README.md](README.md) for basic setup
- Review [IMPROVEMENT_RECOMMENDATIONS.md](IMPROVEMENT_RECOMMENDATIONS.md) for project direction
- Open an issue for questions or discussions

## Code of Conduct

Please be respectful and inclusive in all interactions. We welcome contributors from all backgrounds and experience levels.

## Recognition

Contributors will be recognized in the project documentation and release notes.

Thank you for contributing to AI Classifier Hub!