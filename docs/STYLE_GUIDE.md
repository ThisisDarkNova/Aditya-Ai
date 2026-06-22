# VESPERA OS Style Guide

This document defines naming, formatting, styling, and design conventions across the repository.

---

## 1. Python Style Guide

We adhere to standard Python PEP 8 conventions enforced by Ruff.

### Code Formatting
- Line length: Limit all lines to a maximum of 100 characters.
- Indentation: Use 4 spaces per indentation level.
- Imports: Group imports in the following order:
  1. Standard library imports.
  2. Related third-party imports.
  3. Local application/library-specific imports.

### Naming Conventions
- Variable/Function names: `snake_case` (e.g. `set_ui_control`).
- Class names: `PascalCase` (e.g. `AppResolver`).
- Constants: `UPPER_CASE_SNAKE` (e.g. `UI_DIR`).

---

## 2. JavaScript / React Style Guide

Enforced by ESLint and Prettier configs.

### Code Formatting
- Indentation: Use 2 spaces per indentation level.
- Semicolons: Always use semicolons at the end of statements.
- Quotes: Use double quotes or single quotes consistently.

### Naming Conventions
- File names: `kebab-case` or `camelCase` for utilities, `PascalCase` for React components.
- State variables/React hooks: `camelCase`.
