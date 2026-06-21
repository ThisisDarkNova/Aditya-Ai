# skills/study_helper.py
"""
Notes & Quiz creator system tool for Aditya.
Provides capabilities to dynamically format study guides, write notes files, and print quizzes.
"""

import os
import json
import logging
from pathlib import Path
from core.paths import get_data_dir

logger = logging.getLogger("aditya-study-helper")
logger.setLevel(logging.INFO)

def generate_notes_file(subject: str, topic: str, content: str) -> str:
    """
    Saves generated study notes to a text file inside the user's workspace.
    """
    try:
        workspace_dir = Path("c:/Users/waste/Downloads/Aditya-Ai/Aditya/workspace")
        os.makedirs(workspace_dir, exist_ok=True)
        
        filename = f"{subject.replace(' ', '_')}_{topic.replace(' ', '_')}_Notes.txt"
        file_path = workspace_dir / filename
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"=== STUDY NOTES: {subject.upper()} - {topic.upper()} ===\n\n")
            f.write(content)
            
        logger.info(f"Notes file written to: {file_path}")
        return f"Successfully generated notes! Saved to: {filename}"
    except Exception as e:
        logger.error(f"Failed to generate study notes: {e}")
        return f"Error creating notes file: {e}"

def generate_quiz_file(subject: str, topic: str, questions: list) -> str:
    """
    Saves a formatted study quiz to a file inside the user's workspace.
    """
    try:
        workspace_dir = Path("c:/Users/waste/Downloads/Aditya-Ai/Aditya/workspace")
        os.makedirs(workspace_dir, exist_ok=True)
        
        filename = f"{subject.replace(' ', '_')}_{topic.replace(' ', '_')}_Quiz.txt"
        file_path = workspace_dir / filename
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"=== STUDY QUIZ: {subject.upper()} - {topic.upper()} ===\n\n")
            for idx, q in enumerate(questions, 1):
                f.write(f"Q{idx}. {q.get('question', '')}\n")
                for opt in q.get('options', []):
                    f.write(f"   - {opt}\n")
                f.write(f"\nAnswer: {q.get('answer', '')}\n\n")
                f.write("-" * 40 + "\n\n")
                
        logger.info(f"Quiz file written to: {file_path}")
        return f"Successfully created quiz! Saved to: {filename}"
    except Exception as e:
        logger.error(f"Failed to create quiz file: {e}")
        return f"Error creating quiz: {e}"
