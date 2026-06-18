# ADITYA OS Testing Guide

We maintain automated unit testing suites in the backend to ensure zero regression when updates are published.

## Python Backend Tests

All backend tests are located in `backend/tests/`.

### Prerequisites

First, install the development dependencies:
```bash
pip install -r backend/requirements-dev.txt
```

### Running the Tests

To run the full test suite, execute `pytest` inside the `backend/` directory:

```bash
cd backend
pytest
```

To run with coverage:
```bash
pytest --cov=core --cov=modules tests/
```

### Adding New Test Cases

When creating a new test file:
1. Name the file prefixing with `test_` (e.g. `test_my_feature.py`).
2. Add comprehensive assert statements.
3. Clean up any temporary files or test databases using pytest fixtures.
4. Ensure files are garbage-collected on Windows to prevent file locking issues:
   ```python
   import gc
   # Your test code
   gc.collect() # run gc before setup/teardown cleanups
   ```
