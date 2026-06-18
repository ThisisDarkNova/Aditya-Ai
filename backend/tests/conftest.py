import os
import sys
import pytest
from pathlib import Path

# Add backend folder to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

@pytest.fixture
def temp_workspace(tmp_path):
    """Fixture to simulate a clean user workspace."""
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()
    
    # Create mock files
    (workspace_dir / "todo.txt").write_text("Buy milk\nCall John")
    (workspace_dir / "index.js").write_text("console.log('hello');")
    (workspace_dir / "styles.css").write_text("body { color: red; }")
    
    return workspace_dir

@pytest.fixture
def mock_db_file(tmp_path):
    """Fixture to provide a temporary SQLite DB path."""
    db_path = tmp_path / "test_aditya.db"
    return str(db_path)
