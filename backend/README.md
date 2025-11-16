# OmniVid Backend

## Testing

### Setup

1. Install test dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

### Running Tests

Run all tests with coverage:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_health.py -v
```

Generate coverage report:
```bash
pytest --cov=src --cov-report=html
```

### Test Structure

- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for component interactions
- `tests/e2e/` - End-to-end tests for complete workflows
- `tests/test_assets/` - Test data and fixtures

### Writing Tests

- Use `pytest` fixtures for test dependencies
- Follow the `test_` naming convention
- Place test files next to the code they test
- Use descriptive test names that explain the expected behavior
