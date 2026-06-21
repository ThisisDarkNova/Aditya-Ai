import os
import shutil
import re
from pathlib import Path

springboard_dir = Path(r"c:\Users\DarkNova\Code\Aether-1.0.0\BespokeCanvas\src\SpringBoard")
app_dir = Path(r"c:\Users\DarkNova\Code\Aether-1.0.0\BespokeCanvas\src")

atoms = ["Tooltip.jsx"]
molecules = ["BootSequence.jsx", "StatusBar.jsx", "BottomControls.jsx", "ErrorBoundary.jsx"]
organisms = ["AmbientCanvas.jsx", "Sidebar.jsx", "Startup.jsx", "Visualizer.jsx"]

# Create directories
(springboard_dir / "Atoms").mkdir(exist_ok=True)
(springboard_dir / "Molecules").mkdir(exist_ok=True)
(springboard_dir / "Organisms").mkdir(exist_ok=True)

# Move files
for f in atoms:
    src = springboard_dir / f
    if src.exists(): shutil.move(str(src), str(springboard_dir / "Atoms" / f))
for f in molecules:
    src = springboard_dir / f
    if src.exists(): shutil.move(str(src), str(springboard_dir / "Molecules" / f))
for f in organisms:
    src = springboard_dir / f
    if src.exists(): shutil.move(str(src), str(springboard_dir / "Organisms" / f))

# Update imports everywhere
def update_imports(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for a in atoms:
        base = a.replace(".jsx", "")
        # replace './SpringBoard/Tooltip' -> './SpringBoard/Atoms/Tooltip'
        # replace './Tooltip' -> '../Atoms/Tooltip' or similar depending on where
        new_content = re.sub(rf"(['\"])\./SpringBoard/{base}(['\"])", rf"\g<1>./SpringBoard/Atoms/{base}\g<2>", new_content)
        new_content = re.sub(rf"(['\"])\./{base}(['\"])", rf"\g<1>./Atoms/{base}\g<2>", new_content)
    
    for m in molecules:
        base = m.replace(".jsx", "")
        new_content = re.sub(rf"(['\"])\./SpringBoard/{base}(['\"])", rf"\g<1>./SpringBoard/Molecules/{base}\g<2>", new_content)
        new_content = re.sub(rf"(['\"])\./{base}(['\"])", rf"\g<1>./Molecules/{base}\g<2>", new_content)
        
    for o in organisms:
        base = o.replace(".jsx", "")
        new_content = re.sub(rf"(['\"])\./SpringBoard/{base}(['\"])", rf"\g<1>./SpringBoard/Organisms/{base}\g<2>", new_content)
        new_content = re.sub(rf"(['\"])\./{base}(['\"])", rf"\g<1>./Organisms/{base}\g<2>", new_content)

    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Refactored: {file_path}")

for root, _, files in os.walk(app_dir):
    for file in files:
        if file.endswith(".js") or file.endswith(".jsx"):
            update_imports(Path(root) / file)

print("Atomic UI Refactoring complete.")
