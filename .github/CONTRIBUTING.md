# 🌌 Contributing to VESPERA OS

Thank you for helping to improve VESPERA OS! We welcome all contributions, especially those focusing on **stability, performance, and premium animations**.

---

## 🎨 Visual Styling & Animation Standards

To maintain our premium dark-glassmorphism aesthetic, all frontend modifications should adhere to the following rules:
- **Framer Motion**: Use physics-based springs (`type: "spring"`) for micro-interactions (e.g., hover, button clicks, panels) to create an organic, responsive interface.
- **Glassmorphism Panels**: Always apply the `.glass-panel` or `.glass-button` utility classes from `index.css` for consistent blurs, translucent borders, and focus glows.
- **Dynamic Themes**: Ensure that UI colors resolve to the active persona state (`--color-accent`).

---

## 🛠️ Code Contribution Guidelines

### 1. Bug Reporting & Troubleshooting
- Use the **Bug Report** template to submit issues.
- Please attach the relevant logs from `%APPDATA%/VESPERA/logs/electron.log` or `launcher.log` to make debugging easier.

### 2. Linting & Formatting Checks
Before opening a Pull Request, run formatting scripts locally to prevent workflow failures:
- **Backend Quality**: Check python format and syntax rules using Ruff:
  ```bash
  ruff check .
  ruff format --check .
  ```
- **Frontend Quality**: Run ESLint validation:
  ```bash
  cd client
  npm run lint
  ```

### 3. Verification & Local Testing
We run rigorous check suites on every pull request. Test your work locally:
- **Run Pytest**: Verify that all 17 backend unit tests execute successfully:
  ```bash
  backend\.venv\Scripts\python.exe -m pytest backend
  ```
- **Build Client**: Ensure Vite compiles the React project into stable production assets:
  ```bash
  cd client
  npm run build
  ```

---

## 🚀 Branching Strategy
1. Fork the repo and create your branch (`feature/your-feature-name`).
2. Make your additions, keeping files cleanly documented.
3. Open a Pull Request using our premium PR template.

