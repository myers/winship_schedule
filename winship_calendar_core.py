"""
Core business logic for Winship calendar scheduling.
This module contains pure functions with no external dependencies for easy testing.
"""

import datetime
from typing import List, Dict, Tuple, Optional, Protocol
from dataclasses import dataclass


@dataclass
class CalendarEvent:
    """Pure data structure for calendar events"""
    summary: str
    start_date: datetime.date
    end_date: datetime.date
    location: str
    description: str


class CalendarServiceProtocol(Protocol):
    """Protocol for calendar service - allows for mocking in tests"""

    def list_events(self, calendar_id: str, time_min: str, time_max: str,
                   page_token: Optional[str] = None, max_results: int = 100) -> Dict:
        ...

    def create_event(self, calendar_id: str, event: Dict) -> Dict:
        ...

    def update_event(self, calendar_id: str, event_id: str, event: Dict) -> Dict:
        ...

    def delete_event(self, calendar_id: str, event_id: str) -> None:
        ...


def format_share_name(share_name: Optional[str]) -> str:
    """Convert share name to printable format"""
    if not share_name:
        return "No Owner"
    return share_name.replace("_", " ").title()


def adapt_week_dates(week_start: datetime.date,
                     week_format: str = 'monday-sunday',
                     holiday: Optional[str] = None) -> Tuple[datetime.date, datetime.date]:
    """
    Convert Sunday-start week to requested format.

    Args:
        week_start: Start date (always a Sunday from the schedule)
        week_format: Either 'monday-sunday' or 'sunday-saturday'
        holiday: Holiday name if this is a holiday week

    Returns:
        Tuple of (start_date, end_date) for the calendar event
    """
    monday_holidays = ['Memorial Day', 'Labor Day']

    if week_format == 'sunday-saturday':
        start_date = week_start
        if holiday in monday_holidays:
            # Special case: Monday holidays need Sunday-Sunday (8 days)
            end_date = week_start + datetime.timedelta(days=8)
        else:
            end_date = week_start + datetime.timedelta(days=7)
    elif week_format == 'monday-sunday':
        # Convert to Monday-Sunday format - all weeks run Monday to Sunday (7 days)
        start_date = week_start + datetime.timedelta(days=1)  # Monday
        end_date = start_date + datetime.timedelta(days=7)    # Next Monday (exclusive end)
    else:
        raise ValueError(f"Unknown week format: {week_format}")

    return start_date, end_date


def week_to_event(week, week_format: str = 'monday-sunday') -> CalendarEvent:
    """
    Convert AllocatedWeek to CalendarEvent.

    Args:
        week: AllocatedWeek object with start, share, kind, holiday attributes
        week_format: Format for the week (monday-sunday or sunday-saturday)

    Returns:
        CalendarEvent object
    """
    start_date, end_date = adapt_week_dates(
        week.start, week_format, week.holiday
    )

    description = (f"Holiday: {week.holiday}\nWeek type: {week.kind}"
                  if week.holiday
                  else f"Week type: {week.kind}")

    return CalendarEvent(
        summary=format_share_name(week.share),
        start_date=start_date,
        end_date=end_date,
        location="Winship House, 1083 Lake Sequoyah Road, Jasper, GA, 30143",
        description=description
    )


def find_conflicts(existing_events: List[Dict],
                  start_date: datetime.date,
                  end_date: datetime.date) -> List[Dict]:
    """
    Find conflicting events in date range.

    Args:
        existing_events: List of event dictionaries from calendar API
        start_date: Start date to check for conflicts
        end_date: End date to check for conflicts

    Returns:
        List of conflicting events
    """
    conflicts = []
    for event in existing_events:
        if 'start' in event and 'date' in event['start']:
            try:
                event_start = datetime.date.fromisoformat(event['start']['date'])
                event_end_str = event.get('end', {}).get('date')
                if not event_end_str:
                    continue
                event_end = datetime.date.fromisoformat(event_end_str)

                # Check for overlap: events overlap if not (end1 <= start2 or start1 >= end2)
                if not (event_end <= start_date or event_start >= end_date):
                    conflicts.append({
                        'summary': event.get('summary', 'No title'),
                        'start': event['start']['date'],
                        'end': event.get('end', {}).get('date', 'N/A'),
                        'id': event.get('id')
                    })
            except (ValueError, KeyError):
                # Skip events with malformed dates
                continue
    return conflicts


def get_year_from_schedule(schedule: List, year: int):
    """
    Get schedule for a specific year.

    Args:
        schedule: List of HouseYear objects
        year: Year to find

    Returns:
        HouseYear object for the year, or None if not found
    """
    return next((hy for hy in schedule if hy.year == year), None)


def get_events_for_year(schedule: List, year: int, week_format: str = 'monday-sunday') -> List[CalendarEvent]:
    """
    Convert year's weeks to calendar events.

    Args:
        schedule: List of HouseYear objects
        year: Year to process
        week_format: Week format to use

    Returns:
        List of CalendarEvent objects
    """
    house_year = get_year_from_schedule(schedule, year)
    if not house_year:
        return []

    events = []
    for week in house_year.weeks:
        event = week_to_event(week, week_format)
        events.append(event)
    return events


def calendar_event_to_google_format(event: CalendarEvent) -> Dict:
    """
    Convert CalendarEvent to Google Calendar API format.

    Args:
        event: CalendarEvent object

    Returns:
        Dictionary in Google Calendar API format
    """
    return {
        "summary": event.summary,
        "location": event.location,
        "start": {"date": event.start_date.isoformat(), "timeZone": "America/New_York"},
        "end": {"date": event.end_date.isoformat(), "timeZone": "America/New_York"},
        "description": event.description
    }