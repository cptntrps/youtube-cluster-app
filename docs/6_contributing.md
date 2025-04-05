# Contributing Guidelines

## Development Setup

### 1. Fork and Clone
1. Fork the repository on GitHub
2. Clone your fork locally:
```bash
git clone git@github.com:your-username/youtube-cluster-app.git
cd youtube-cluster-app
```

### 2. Create Development Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install development dependencies
pip install -r requirements-dev.txt
```

### 3. Set Up Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install
```

## Code Style

### 1. Python Style Guide
- Follow PEP 8 guidelines
- Use type hints for function arguments and return values
- Maximum line length: 88 characters (Black formatter)
- Use docstrings for all public functions and classes

### 2. Documentation
- Keep docstrings up to date
- Follow Google docstring format
- Include examples in docstrings where appropriate
- Update relevant documentation files when making changes

### 3. Commit Messages
- Use clear and descriptive commit messages
- Follow conventional commits format:
  * feat: New feature
  * fix: Bug fix
  * docs: Documentation changes
  * style: Code style changes
  * refactor: Code refactoring
  * test: Test changes
  * chore: Maintenance tasks

## Testing

### 1. Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_clustering.py

# Run with coverage
pytest --cov=src tests/
```

### 2. Writing Tests
- Write tests for all new features
- Maintain test coverage above 80%
- Use meaningful test names
- Follow arrange-act-assert pattern
- Mock external API calls

### 3. Test Organization
```
tests/
├── unit/
│   ├── test_clustering.py
│   ├── test_embedding.py
│   └── test_visualization.py
├── integration/
│   ├── test_api_integration.py
│   └── test_end_to_end.py
└── conftest.py
```

## Pull Request Process

### 1. Before Submitting
- Run all tests locally
- Update documentation
- Add test cases
- Run linters and formatters
- Rebase on main branch

### 2. PR Template
```markdown
## Description
[Description of the changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Other (please specify)

## Testing
- [ ] Added new tests
- [ ] All tests passing
- [ ] No coverage decrease

## Documentation
- [ ] Updated relevant documentation
- [ ] Added docstrings
- [ ] Updated README if needed

## Additional Notes
[Any additional information]
```

### 3. Review Process
- At least one approval required
- All CI checks must pass
- No merge conflicts
- Documentation updated
- Tests added and passing

## Development Workflow

### 1. Branch Strategy
- main: Production-ready code
- develop: Integration branch
- feature/*: New features
- fix/*: Bug fixes
- docs/*: Documentation updates

### 2. Version Control
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: Add new feature"

# Push changes
git push origin feature/new-feature
```

### 3. Code Review
- Review comments should be constructive
- Address all review comments
- Request re-review after changes
- Squash commits before merging

## Release Process

### 1. Version Numbering
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update version in setup.py
- Create release notes

### 2. Release Checklist
```markdown
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Version bumped
- [ ] Release notes written
- [ ] Dependencies updated
- [ ] Security checks passed
```

### 3. Release Steps
```bash
# Create release branch
git checkout -b release/v1.0.0

# Update version
# Update CHANGELOG.md
# Run final tests

# Create tag
git tag -a v1.0.0 -m "Release v1.0.0"

# Push release
git push origin release/v1.0.0 --tags
```

## Code of Conduct

### 1. Our Pledge
We are committed to making participation in our project a harassment-free experience for everyone, regardless of:
- Age
- Body size
- Disability
- Ethnicity
- Gender identity
- Experience level
- Nationality
- Personal appearance
- Race
- Religion
- Sexual identity/orientation

### 2. Our Standards
Positive behavior:
- Using welcoming language
- Being respectful of differing viewpoints
- Accepting constructive criticism
- Focusing on what's best for the community
- Showing empathy towards others

Unacceptable behavior:
- Harassment of any kind
- Discriminatory jokes and language
- Personal or political attacks
- Publishing others' private information
- Other conduct which could be considered inappropriate

### 3. Enforcement
- Violations may be reported to project maintainers
- All complaints will be reviewed and investigated
- Maintainers will maintain confidentiality
- Appropriate and fair corrective action will be taken

## Support

### 1. Getting Help
- Check existing documentation
- Search issues for similar problems
- Ask questions in discussions
- Join community chat

### 2. Reporting Issues
- Use issue templates
- Provide clear reproduction steps
- Include relevant logs
- Specify environment details

### 3. Community Resources
- Project wiki
- Discussion forums
- Community chat
- Regular community calls 