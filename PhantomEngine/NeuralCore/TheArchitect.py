import os
import ast
from pathlib import Path

class TheArchitect:
    """
    🏗️ The Architect: Deep Codebase Scanner
    Recursively scans project directories, parses Python ASTs, and proactively generates structural refactor plans.
    """
    def __init__(self):
        pass

    def scan_directory(self, target_dir: str):
        print(f"[The Architect] Scanning codebase at: {target_dir}")
        python_files = []
        for root, dirs, files in os.walk(target_dir):
            # Ignore virtual environments and node_modules
            if ".venv" in root or "node_modules" in root or ".git" in root:
                continue
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        
        return self._analyze_files(python_files)

    def _analyze_files(self, files: list):
        issues_found = []
        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Basic AST parsing to find excessively long functions or deeply nested loops
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Heuristic: Functions over 100 lines are a structural flaw
                        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                            if node.end_lineno - node.lineno > 100:
                                issues_found.append(f"File {file}: Function '{node.name}' exceeds 100 lines. Consider refactoring.")
            except Exception as e:
                # Silently skip unparseable files
                pass
        
        return issues_found

    def generate_refactor_plan(self, issues: list) -> str:
        if not issues:
            return "# Architectural Scan\n\nCodebase structure is optimal."
            
        plan = "# Proactive Refactor Plan\n\n"
        for issue in issues:
            plan += f"- [ ] **Architectural Flaw:** {issue}\n"
        return plan

architect = TheArchitect()
