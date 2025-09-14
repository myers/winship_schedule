"""
Google Calendar service wrapper.
Implements the CalendarServiceProtocol for dependency injection and testing.
"""

from typing import Dict, Optional
import time


class GoogleCalendarService:
    """Wrapper around Google Calendar API - implements CalendarServiceProtocol"""

    def __init__(self, service, rate_limit_delay: float = 0.3):
        """
        Initialize the wrapper.

        Args:
            service: Google Calendar API service object
            rate_limit_delay: Delay between API calls to avoid rate limits
        """
        self.service = service
        self.rate_limit_delay = rate_limit_delay

    def list_events(self, calendar_id: str, time_min: str, time_max: str,
                   page_token: Optional[str] = None, max_results: int = 100) -> Dict:
        """
        List events with pagination support.

        Args:
            calendar_id: Google Calendar ID
            time_min: RFC3339 timestamp for start of time range
            time_max: RFC3339 timestamp for end of time range
            page_token: Token for pagination
            max_results: Maximum number of events to return

        Returns:
            Dictionary containing events and pagination info
        """
        return self.service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            pageToken=page_token,
            maxResults=max_results
        ).execute()

    def create_event(self, calendar_id: str, event: Dict) -> Dict:
        """
        Create a new event.

        Args:
            calendar_id: Google Calendar ID
            event: Event data in Google Calendar format

        Returns:
            Created event data
        """
        result = self.service.events().insert(
            calendarId=calendar_id,
            body=event
        ).execute()
        time.sleep(self.rate_limit_delay)
        return result

    def update_event(self, calendar_id: str, event_id: str, event: Dict) -> Dict:
        """
        Update an existing event.

        Args:
            calendar_id: Google Calendar ID
            event_id: ID of event to update
            event: Updated event data

        Returns:
            Updated event data
        """
        result = self.service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event
        ).execute()
        time.sleep(self.rate_limit_delay)
        return result

    def delete_event(self, calendar_id: str, event_id: str) -> None:
        """
        Delete an event.

        Args:
            calendar_id: Google Calendar ID
            event_id: ID of event to delete
        """
        self.service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
            sendNotifications=False
        ).execute()
        time.sleep(self.rate_limit_delay)

    def delete_all_events_for_year(self, calendar_id: str, year: int) -> int:
        """
        Delete all events in the calendar for a specific year.

        Args:
            calendar_id: Google Calendar ID
            year: Year to delete events for

        Returns:
            Number of deleted events
        """
        print(f"Deleting all events for {year}...")

        # Get all events for the year
        time_min = f"{year}-01-01T00:00:00Z"
        time_max = f"{year + 1}-01-01T00:00:00Z"

        deleted_count = 0
        page_token = None

        while True:
            events_result = self.list_events(
                calendar_id=calendar_id,
                time_min=time_min,
                time_max=time_max,
                page_token=page_token,
                max_results=250
            )

            events = events_result.get("items", [])
            if not events:
                break

            for event in events:
                try:
                    print(f"  Deleting: {event.get('summary', 'No title')} "
                          f"({event.get('start', {}).get('date', 'No date')})")
                    self.delete_event(calendar_id, event["id"])
                    deleted_count += 1
                except Exception as e:
                    print(f"    Error deleting event {event.get('id', 'unknown')}: {e}")

            page_token = events_result.get("nextPageToken")
            if not page_token:
                break

        print(f"Deleted {deleted_count} events for {year}")
        return deleted_count