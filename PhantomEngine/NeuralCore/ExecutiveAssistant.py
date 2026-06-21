import win32com.client
from datetime import datetime, timedelta

class ExecutiveAssistant:
    """
    👔 Aditya Executive Assistant
    Hooks directly into local Outlook via COM to read schedules and proactively manage your life.
    """
    def __init__(self):
        self.outlook = None
        self.namespace = None

    def connect(self):
        try:
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
        except Exception as e:
            print(f"[ExecutiveAssistant] Outlook COM failed: {e}")

    def get_upcoming_meetings(self, hours: int = 12):
        if not self.namespace:
            self.connect()
        if not self.namespace:
            return []

        try:
            calendar = self.namespace.GetDefaultFolder(9) # 9 is olFolderCalendar
            appointments = calendar.Items
            appointments.IncludeRecurrences = True
            appointments.Sort("[Start]")

            now = datetime.now()
            end_time = now + timedelta(hours=hours)

            # Outlook filter format requires specific date string
            restriction = f"[Start] >= '{now.strftime('%m/%d/%Y %H:%M %p')}' AND [Start] <= '{end_time.strftime('%m/%d/%Y %H:%M %p')}'"
            restricted_items = appointments.Restrict(restriction)

            meetings = []
            for item in restricted_items:
                meetings.append({
                    "subject": item.Subject,
                    "start": item.Start.Format("%Y-%m-%d %H:%M"),
                    "duration": item.Duration
                })
            return meetings
        except Exception as e:
            print(f"[ExecutiveAssistant] Failed to read calendar: {e}")
            return []

executive_assistant = ExecutiveAssistant()
