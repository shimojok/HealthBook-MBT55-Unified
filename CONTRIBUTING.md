# 🤝 Contributing to HealthBook-MBT55-Unified

## How to Contribute

1. **Fork** the repository
2. **Create a feature branch**: `feature/your-feature-name`
3. **Commit** your changes with clear messages
4. **Push** to your fork
5. **Open a Pull Request** to `main` branch

## Development Setup

```bash
git clone https://github.com/shimojok/HealthBook-MBT55-Unified.git
cd HealthBook-MBT55-Unified
pip install -r requirements.txt
pip install -r requirements-dev.txt  # testing tools
```

## Code Style

- **Python**: PEP 8, type hints required
- **JSON**: 2-space indentation, UTF-8 encoding
- **Docstrings**: Google-style for all public functions

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_pathway_database.py -v

# Run with coverage
pytest --cov=src --cov-report=html
```

## Adding New Pathways

1. Add entry to `data/pathways/master_pathways.json`
2. Follow existing schema with `cascade_stage_1/2/3`
3. Add corresponding enzyme and key player data
4. Run `pytest tests/unit/test_pathway_database.py` to validate

## Adding New Meta-Strains

1. Add entry to `data/probiotics/probiotic_matrix.json`
2. Define `substrate_preference`, `enzyme_profile`, `optimal_conditions`
3. Update `META_STRAIN_DEFINITIONS` in `src/core/config.py`
4. Update i18n dictionaries in `dashboard/i18n/`

## Documentation

All new features must include:
- Code docstrings
- Updated API spec if applicable
- README updates if major feature

## Pull Request Checklist

- [ ] Tests pass (`pytest`)
- [ ] Type hints complete
- [ ] Documentation updated
- [ ] i18n dictionaries updated for both JA and EN
- [ ] No breaking changes to existing API