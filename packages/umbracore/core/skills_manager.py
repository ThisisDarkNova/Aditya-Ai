import os
import threading
import json
import subprocess
import importlib
import traceback
import sys

SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skills"))
KNOWLEDGE_FILE = os.path.join(SKILLS_DIR, "skills_knowledge.json")
CUSTOM_SKILLS_FILE = os.path.join(SKILLS_DIR, "custom_skills.py")

# Ensure environment
os.makedirs(SKILLS_DIR, exist_ok=True)

if not os.path.exists(KNOWLEDGE_FILE):
    with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

if not os.path.exists(CUSTOM_SKILLS_FILE):
    with open(CUSTOM_SKILLS_FILE, "w", encoding="utf-8") as f:
        f.write("# This file stores all dynamically learned Python skills.\n")
        f.write("# Do not manually edit unless fixing critical errors.\n")
        f.write("import os\nimport time\nimport pyautogui\nimport ctypes\n\n")

def get_learned_skills_summary() -> str:
    """Returns a string describing all currently learned skills for the AI context."""
    if not os.path.exists(KNOWLEDGE_FILE):
        return ""
    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if not data:
               return ""
            lines = []
            for skill_name, info in data.items():
                lines.append(f"- '{skill_name}': Trigger -> '{info.get('trigger', '')}'")
            return "\n\n=== LEARNED SKILLS (You wrote these functions) ===\n" + "\n".join(lines) + "\nCall these using execute_skill('<name>')\n================================================="
        except:
            return ""

def test_python_code(code: str) -> str:
    """Executes a block of python code in a temporary sub-process to test for syntax and runtime errors."""
    print("[AI Meta-Programming] Testing dynamic python code...")
    sandbox_file = os.path.join(SKILLS_DIR, "_sandbox_temp.py")
    try:
        with open(sandbox_file, "w", encoding="utf-8") as f:
            f.write("import pyautogui, time, os, ctypes\n") # Safe standard imports
            f.write(code)
            
        result = subprocess.run(
            ["python", sandbox_file],
            capture_output=True,
            text=True,
            timeout=15 # Prevents infinite loops blocking AI
        )
        
        output = result.stdout
        if result.stderr:
            output += "\n[ERRORS]:\n" + result.stderr
            return f"Code Execution Failed! Fix errors and try again.\nOUTPUT:\n{output}"
            
        return "Code executed perfectly with NO ERRORS!\nOUTPUT:\n" + (output if output.strip() else "[None]")
    except subprocess.TimeoutExpired:
        return "[ERROR] Timeout: Code took longer than 15 seconds to execute (infinite loop?)"
    except Exception as e:
        return f"[ERROR] Sandbox crash: {e}"
    finally:
        try:
            if os.path.exists(sandbox_file):
                os.remove(sandbox_file)
        except Exception:
            pass

_skills_lock = threading.Lock()

def save_tested_skill(skill_name: str, trigger_phrase: str, final_code: str) -> str:
    """Appends successful code to custom_skills.py as a function."""
    print(f"[AI Meta-Programming] Saving strictly validated skill: {skill_name}")
    try:
        with _skills_lock:
            try:
                with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                data = {}
                
            data[skill_name] = {"trigger": trigger_phrase}
            
            with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
                
            # Append code
            with open(CUSTOM_SKILLS_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n# SKILL: {skill_name}\n")
                f.write(f"# TRIGGER PREFERENCE: {trigger_phrase}\n")
                f.write(final_code)
                f.write("\n\n")
            
        return f"SUCCESS: Skill '{skill_name}' natively saved. You can now use execute_skill('{skill_name}') permanently."
    except Exception as e:
        return f"Failed to save skill: {e}"

def execute_skill(skill_name: str) -> str:
    """Invokes a saved python function from custom_skills.py"""
    print(f"[AI Meta-Programming] Executing learned native skill: {skill_name}")
    try:
        # Dynamic reload of the module in case AI just updated it
        if "skills.custom_skills" in sys.modules:
            del sys.modules["skills.custom_skills"]
            
        import skills.custom_skills as cs
        importlib.reload(cs)
        
        func = getattr(cs, skill_name, None)
        if not func:
             return f"Error: Function {skill_name} not found in custom_skills.py. You may need to write and save it."
             
        result = func()
        return f"Skill {skill_name} executed gracefully. Result: {result}"
    except Exception as e:
        return f"RUNTIME CRASH in skill {skill_name}: {str(e)}\n\n{traceback.format_exc()}"
