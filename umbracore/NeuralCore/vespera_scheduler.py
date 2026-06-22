import threading
import time
from datetime import datetime, timedelta
import uuid

# Minimum seconds a reminder must exist before it can fire.
# This prevents the "fires instantly before timer completes" bug
# when the AI sets a reminder for a time very close to now.
MIN_GRACE_SECONDS = 5

class VesperaScheduler:
    def __init__(self):
        self.tasks = []
        self.alerts = []
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, name="reminder-bg-thread", daemon=True)
        self._thread.start()

    def add_reminder(self, text: str, time_str: str = "", delay_minutes: float = None) -> str:
        """
        Add a reminder. Flexibly parses many time formats or relative delay minutes.
        """
        try:
            now = datetime.now()
            target = None

            if delay_minutes is not None:
                target = now + timedelta(minutes=float(delay_minutes))
            elif time_str:
                import re
                # Strip any timezone suffix the AI might append (UTC, IST, EST, etc.)
                cleaned = re.sub(r'\s*(UTC|IST|EST|PST|CST|MST|GMT|[A-Z]{2,4})$', '', time_str.strip())
                # Also strip any trailing +05:30 style offset
                cleaned = re.sub(r'\s*[+-]\d{2}:\d{2}$', '', cleaned)

                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%d-%m-%Y %H:%M", "%d/%m/%Y %H:%M"):
                    try:
                        target = datetime.strptime(cleaned, fmt)
                        break
                    except ValueError:
                        continue

                if target is None:
                    return f"Could not parse time '{time_str}'. Use format: YYYY-MM-DD HH:MM"

            if target is None:
                return "Failed: You must provide either delay_minutes or a valid time_str."

            # If the target is already in the past or too close, push it forward
            # so the reminder doesn't fire instantly before the user even hears confirmation.
            earliest_fire = now + timedelta(seconds=MIN_GRACE_SECONDS)
            if target < earliest_fire:
                target = earliest_fire

            task_id = str(uuid.uuid4())[:8]
            self.tasks.append({
                "id": task_id,
                "text": text,
                "target": target,
                "created_at": now,
            })
            display_time = target.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[⏰ Reminder Set] Will remind you about '{text}' at {display_time} (ID: {task_id})")
            return f"Reminder successfully set for '{text}' at {display_time}. Task ID is {task_id}."
        except Exception as e:
            error_msg = f"Failed to set reminder: {e}"
            print(f"[ERROR] {error_msg}")
            return error_msg

    def get_reminders(self) -> str:
        """Return a formatted string of all active reminders."""
        if not self.tasks:
            return "You have no active reminders."
        result = "Current Active Reminders:\n"
        for task in self.tasks:
            result += f"- [ID: {task['id']}] {task['text']} at {task['target'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        return result

    def complete_reminder(self, task_id: str) -> str:
        """Mark a reminder as complete and remove it from the list."""
        for task in self.tasks:
            if task["id"] == task_id or task_id.lower() in task["text"].lower():
                self.tasks.remove(task)
                print(f"[✅ Task Completed] {task['text']}")
                return f"Successfully marked task '{task['text']}' as complete and removed the reminder."
        return f"Could not find any active reminder with ID or text matching '{task_id}'."

    def _run(self):
        while not self._stop_event.is_set():
            now = datetime.now()

            for task in self.tasks[:]:
                # Only fire if BOTH conditions are met:
                # 1. Current time is past the target time
                # 2. At least MIN_GRACE_SECONDS have passed since creation
                age = (now - task["created_at"]).total_seconds()
                if now >= task["target"] and age >= MIN_GRACE_SECONDS:
                    print(f"\n[🔔 ALERT] Reminder triggered: {task['text']}", flush=True)
                    self.alerts.append(task["text"])
                    self.tasks.remove(task)

            # Check every 1 second for better precision
            time.sleep(1)

# Global background instance
reminder_system = VesperaScheduler()
