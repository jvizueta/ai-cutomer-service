import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from ..config import settings

logger = logging.getLogger(__name__)

# Placeholder for Google Calendar integration. In production you would use
# googleapiclient.discovery.build and OAuth flows (credentials.json).
class CalendarScheduler:
    """Simple stub calendar scheduler. Provides availability checking and meeting scheduling."""

    def __init__(self):
        logger.debug("Initializing CalendarScheduler")
        self.calendar_id = settings.CALENDAR_ID
        self.default_duration = settings.DEFAULT_MEETING_DURATION_MINUTES
        self.timezone = settings.TIMEZONE
        # In-memory events store (start, end, summary)
        self._events: List[Dict[str, Any]] = []

    def list_events(self) -> List[Dict[str, Any]]:
        logger.debug("Listing calendar events")
        return self._events

    def is_available(self, start: datetime, end: datetime) -> bool:
        logger.debug(f"Checking availability from {start} to {end}")
        for evt in self._events:
            if not (end <= evt["start"] or start >= evt["end"]):
                return False
        return True

    def schedule_meeting(self, prospect_name: str, start: datetime) -> Dict[str, Any]:
        logger.debug(f"Scheduling meeting with {prospect_name} at {start}")
        end = start + timedelta(minutes=self.default_duration)
        if not self.is_available(start, end):
            return {"scheduled": False, "reason": "Time slot not available"}
        event = {
            "summary": f"Meeting with {prospect_name}",
            "start": start,
            "end": end,
            "calendar_id": self.calendar_id,
        }
        self._events.append(event)
        logger.info(f"Scheduled meeting: {event}")
        return {"scheduled": True, "event": event}

    async def run(self, query: str) -> str:
        """Very naive parser: if query contains 'schedule' and a name, schedule a meeting at next hour."""
        logger.debug(f"Running CalendarScheduler with query: {query[:50]}")
        now = datetime.utcnow()
        prospect = "prospect"
        if "schedule" in query.lower():
            # try extracting a name (very naive split)
            tokens = query.split()
            if len(tokens) > 1:
                prospect = tokens[-1].strip("?.!")
            start_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            result = self.schedule_meeting(prospect, start_time)
            if result.get("scheduled"):
                evt = result["event"]
                return (
                    f"Scheduled meeting with {prospect} on {evt['start'].isoformat()} for {self.default_duration} minutes."
                )
            else:
                return f"Unable to schedule meeting: {result.get('reason')}"
        else:
            return "No scheduling action detected. Ask me to schedule a meeting."

def calendar_scheduler_tool() -> Dict[str, Any]:
    async def _invoke(input_text: str) -> str:
        logger.debug(f"Invoking CalendarScheduler with input_text: {input_text[:50]}")
        scheduler = CalendarScheduler()
        return await scheduler.run(input_text)
    return {
        "name": "calendar_scheduler",
        "description": "Checks availability and schedules meetings in Google Calendar (stub).",
        "callable": _invoke,
    }
