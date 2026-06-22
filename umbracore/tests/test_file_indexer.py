import os
import pytest
from V12Cylinders.file_indexer import FileIndexer

def test_workspace_indexer(temp_workspace):
    indexer = FileIndexer(temp_workspace)
    indexer.reindex()
    
    # Run a simple search
    results = indexer.search_and_sort("todo")
    assert len(results) > 0
    assert "todo.txt" in results[0]["path"]
    
    # Verify sorting
    all_files = indexer.search_and_sort("", sort_by="name")
    assert len(all_files) >= 3
    paths = [f["path"] for f in all_files]
    assert "index.js" in paths
    assert "styles.css" in paths
    
    # Safe preview test
    content_info = indexer.get_safe_content("todo.txt")
    assert "content" in content_info
    assert "Buy milk" in content_info["content"]
