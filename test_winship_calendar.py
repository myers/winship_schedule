"""
Pytest tests for winship_calendar_core module.
Tests use functional style with fixtures for clean, readable tests.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock

from winship_calendar_core import (
    format_share_name,
    adapt_week_dates,
    week_to_event,
    find_conflicts,
    get_year_from_schedule,
    get_events_for_year,
    calendar_event_to_google_format,
    CalendarEvent
)


# Fixtures
@pytest.fixture
def mock_week():
    """Create a mock AllocatedWeek"""
    week = Mock()
    week.start = date(2027, 3, 7)  # A Sunday
    week.share = "frank_may"
    week.kind = "warm"
    week.holiday = None
    return week


@pytest.fixture
def mock_holiday_week():
    """Create a mock Memorial Day week"""
    week = Mock()
    week.start = date(2027, 5, 25)  # Sunday before Memorial Day
    week.share = "joe"
    week.kind = "warm"
    week.holiday = "Memorial Day"
    return week


@pytest.fixture
def mock_labor_day_week():
    """Create a mock Labor Day week"""
    week = Mock()
    week.start = date(2027, 8, 31)  # Sunday before Labor Day
    week.share = "eddie"
    week.kind = "warm"
    week.holiday = "Labor Day"
    return week


@pytest.fixture
def sample_events():
    """Sample existing events for conflict testing"""
    return [
        {
            'id': '1',
            'summary': 'Frank May',
            'start': {'date': '2027-03-08'},
            'end': {'date': '2027-03-15'}
        },
        {
            'id': '2',
            'summary': 'Joe',
            'start': {'date': '2027-03-15'},
            'end': {'date': '2027-03-22'}
        }
    ]


@pytest.fixture
def mock_schedule():
    """Create a mock schedule with multiple years"""
    week_2027 = Mock(start=date(2027, 3, 7), share="joe", kind="hot", holiday=None)
    year_2027 = Mock(year=2027, weeks=[week_2027])

    week_2028 = Mock(start=date(2028, 3, 5), share="frank_may", kind="cold", holiday=None)
    year_2028 = Mock(year=2028, weeks=[week_2028])

    return [year_2027, year_2028]


@pytest.fixture
def sample_calendar_event():
    """Sample CalendarEvent for testing"""
    return CalendarEvent(
        summary="Frank May",
        start_date=date(2027, 3, 8),
        end_date=date(2027, 3, 15),
        location="Winship House, 1083 Lake Sequoyah Road, Jasper, GA, 30143",
        description="Week type: warm"
    )


# Tests for format_share_name
def test_format_share_name_with_underscore():
    assert format_share_name("frank_may") == "Frank May"
    assert format_share_name("hugh_ann_laurel") == "Hugh Ann Laurel"


def test_format_share_name_simple():
    assert format_share_name("joe") == "Joe"
    assert format_share_name("eddie") == "Eddie"


def test_format_share_name_empty():
    assert format_share_name(None) == "No Owner"
    assert format_share_name("") == "No Owner"


# Tests for adapt_week_dates
def test_adapt_week_dates_monday_sunday():
    """Test Monday-Sunday week format"""
    sunday = date(2027, 3, 7)  # A Sunday
    start, end = adapt_week_dates(sunday, 'monday-sunday')

    assert start == date(2027, 3, 8)  # Monday
    assert end == date(2027, 3, 15)   # Next Monday
    assert start.weekday() == 0       # 0 = Monday
    assert (end - start).days == 7    # 7 days


def test_adapt_week_dates_sunday_saturday():
    """Test Sunday-Saturday week format"""
    sunday = date(2027, 3, 7)  # A Sunday
    start, end = adapt_week_dates(sunday, 'sunday-saturday')

    assert start == date(2027, 3, 7)   # Sunday
    assert end == date(2027, 3, 14)    # Next Sunday
    assert start.weekday() == 6        # 6 = Sunday
    assert (end - start).days == 7     # 7 days


def test_adapt_week_dates_memorial_day_sunday_saturday():
    """Test Memorial Day special handling in Sunday-Saturday format"""
    sunday = date(2027, 5, 25)  # Sunday before Memorial Day
    start, end = adapt_week_dates(sunday, 'sunday-saturday', holiday='Memorial Day')

    assert start == date(2027, 5, 25)  # Sunday
    assert (end - start).days == 8     # 8 days for holiday


def test_adapt_week_dates_labor_day_sunday_saturday():
    """Test Labor Day special handling in Sunday-Saturday format"""
    sunday = date(2027, 8, 31)  # Sunday before Labor Day
    start, end = adapt_week_dates(sunday, 'sunday-saturday', holiday='Labor Day')

    assert start == date(2027, 8, 31)  # Sunday
    assert (end - start).days == 8     # 8 days for holiday


def test_adapt_week_dates_memorial_day_monday_sunday():
    """Test Memorial Day handling in Monday-Sunday format"""
    sunday = date(2027, 5, 25)  # Sunday before Memorial Day
    start, end = adapt_week_dates(sunday, 'monday-sunday', holiday='Memorial Day')

    # In Monday-Sunday format, all weeks are 7 days
    assert start == date(2027, 5, 26)  # Monday (Memorial Day)
    assert end == date(2027, 6, 2)     # Next Monday
    assert (end - start).days == 7


def test_adapt_week_dates_invalid_format():
    """Test invalid week format raises error"""
    with pytest.raises(ValueError, match="Unknown week format"):
        adapt_week_dates(date(2027, 3, 7), 'invalid-format')


# Tests for week_to_event
def test_week_to_event_monday_sunday(mock_week):
    """Test converting AllocatedWeek to CalendarEvent"""
    event = week_to_event(mock_week, 'monday-sunday')

    assert event.summary == "Frank May"
    assert event.start_date == date(2027, 3, 8)  # Monday
    assert event.end_date == date(2027, 3, 15)   # Next Monday
    assert "Week type: warm" in event.description
    assert "Holiday" not in event.description
    assert "Winship House" in event.location


def test_week_to_event_with_holiday(mock_holiday_week):
    """Test converting holiday week to CalendarEvent"""
    event = week_to_event(mock_holiday_week, 'monday-sunday')

    assert event.summary == "Joe"
    assert "Holiday: Memorial Day" in event.description
    assert "Week type: warm" in event.description


def test_week_to_event_sunday_saturday(mock_week):
    """Test converting week with Sunday-Saturday format"""
    event = week_to_event(mock_week, 'sunday-saturday')

    assert event.summary == "Frank May"
    assert event.start_date == date(2027, 3, 7)  # Sunday
    assert event.end_date == date(2027, 3, 14)   # Next Sunday
    assert "Week type: warm" in event.description


# Tests for find_conflicts
def test_find_conflicts_with_overlap(sample_events):
    """Test finding overlapping events"""
    conflicts = find_conflicts(
        sample_events,
        date(2027, 3, 10),  # Wednesday
        date(2027, 3, 17)   # Next Wednesday
    )

    assert len(conflicts) == 2  # Should overlap with both events
    assert conflicts[0]['id'] == '1'
    assert conflicts[1]['id'] == '2'


def test_find_conflicts_no_overlap(sample_events):
    """Test no conflicts when dates don't overlap"""
    conflicts = find_conflicts(
        sample_events,
        date(2027, 3, 22),  # After both events
        date(2027, 3, 29)
    )

    assert len(conflicts) == 0


def test_find_conflicts_exact_boundary(sample_events):
    """Test events that touch but don't overlap"""
    conflicts = find_conflicts(
        sample_events,
        date(2027, 3, 1),   # Before first event
        date(2027, 3, 8)    # Exactly when first event starts
    )

    assert len(conflicts) == 0  # Should not overlap


def test_find_conflicts_missing_end_date():
    """Test handling events with missing end dates"""
    events_with_missing_end = [
        {
            'id': '1',
            'summary': 'Event without end',
            'start': {'date': '2027-03-08'},
            # Missing 'end' field
        }
    ]

    conflicts = find_conflicts(
        events_with_missing_end,
        date(2027, 3, 10),
        date(2027, 3, 17)
    )

    assert len(conflicts) == 0  # Should skip events without end dates


# Tests for schedule functions
def test_get_year_from_schedule(mock_schedule):
    """Test getting a specific year from schedule"""
    assert get_year_from_schedule(mock_schedule, 2027).year == 2027
    assert get_year_from_schedule(mock_schedule, 2028).year == 2028
    assert get_year_from_schedule(mock_schedule, 2029) is None


def test_get_events_for_year(mock_schedule):
    """Test converting a year's weeks to events"""
    events = get_events_for_year(mock_schedule, 2027, 'monday-sunday')

    assert len(events) == 1
    assert events[0].summary == "Joe"
    assert events[0].start_date == date(2027, 3, 8)  # Monday


def test_get_events_for_missing_year(mock_schedule):
    """Test getting events for non-existent year"""
    events = get_events_for_year(mock_schedule, 2030, 'monday-sunday')
    assert events == []


# Tests for calendar_event_to_google_format
def test_calendar_event_to_google_format(sample_calendar_event):
    """Test converting CalendarEvent to Google Calendar format"""
    google_event = calendar_event_to_google_format(sample_calendar_event)

    assert google_event['summary'] == "Frank May"
    assert google_event['start']['date'] == "2027-03-08"
    assert google_event['end']['date'] == "2027-03-15"
    assert google_event['start']['timeZone'] == "America/New_York"
    assert google_event['end']['timeZone'] == "America/New_York"
    assert "Week type: warm" in google_event['description']
    assert "Winship House" in google_event['location']


# Parametrized tests
@pytest.mark.parametrize("share,expected", [
    ("frank_may", "Frank May"),
    ("joe", "Joe"),
    ("hugh_ann_laurel", "Hugh Ann Laurel"),
    ("eddie", "Eddie"),
    (None, "No Owner"),
    ("", "No Owner"),
])
def test_format_share_name_parametrized(share, expected):
    """Test share name formatting with multiple inputs"""
    assert format_share_name(share) == expected


@pytest.mark.parametrize("week_format,expected_days", [
    ("monday-sunday", 7),
    ("sunday-saturday", 7),
])
def test_week_duration_no_holiday(week_format, expected_days):
    """Test that regular weeks are always 7 days"""
    sunday = date(2027, 3, 7)
    start, end = adapt_week_dates(sunday, week_format)
    assert (end - start).days == expected_days


@pytest.mark.parametrize("holiday", ["Memorial Day", "Labor Day"])
def test_monday_holidays_sunday_saturday_format(holiday):
    """Test that Monday holidays extend to 8 days in Sunday-Saturday format"""
    sunday = date(2027, 5, 25)  # Arbitrary Sunday
    start, end = adapt_week_dates(sunday, 'sunday-saturday', holiday=holiday)
    assert (end - start).days == 8


@pytest.mark.parametrize("holiday", ["Memorial Day", "Labor Day"])
def test_monday_holidays_monday_sunday_format(holiday):
    """Test that Monday holidays are still 7 days in Monday-Sunday format"""
    sunday = date(2027, 5, 25)  # Arbitrary Sunday
    start, end = adapt_week_dates(sunday, 'monday-sunday', holiday=holiday)
    assert (end - start).days == 7


@pytest.mark.parametrize("holiday", ["Independence Day", "Thanksgiving", "Christmas"])
def test_non_monday_holidays(holiday):
    """Test that non-Monday holidays don't get special treatment"""
    sunday = date(2027, 7, 4)  # Arbitrary Sunday

    # Should be same for both formats
    start1, end1 = adapt_week_dates(sunday, 'sunday-saturday', holiday=holiday)
    start2, end2 = adapt_week_dates(sunday, 'sunday-saturday')

    assert (end1 - start1).days == (end2 - start2).days == 7


# Edge cases and error handling
def test_adapt_week_dates_leap_year():
    """Test date adaptation works correctly in leap years"""
    # Feb 28, 2028 is a Sunday (2028 is a leap year)
    sunday = date(2028, 2, 27)  # Sunday
    start, end = adapt_week_dates(sunday, 'monday-sunday')

    assert start == date(2028, 2, 28)  # Monday (leap year)
    assert end == date(2028, 3, 6)     # Next Monday
    assert (end - start).days == 7


def test_week_to_event_empty_share():
    """Test week conversion with empty share name"""
    week = Mock()
    week.start = date(2027, 3, 7)
    week.share = None
    week.kind = "warm"
    week.holiday = None

    event = week_to_event(week)
    assert event.summary == "No Owner"


def test_find_conflicts_empty_events_list():
    """Test conflict detection with empty events list"""
    conflicts = find_conflicts(
        [],
        date(2027, 3, 10),
        date(2027, 3, 17)
    )
    assert len(conflicts) == 0


def test_find_conflicts_malformed_events():
    """Test conflict detection with malformed event data"""
    malformed_events = [
        {'id': '1', 'summary': 'No dates'},  # Missing start/end
        {'id': '2', 'start': {}},             # Empty start
        {'id': '3', 'start': {'date': 'invalid-date'}},  # Invalid date format
    ]

    # Should not raise exceptions, just skip malformed events
    conflicts = find_conflicts(
        malformed_events,
        date(2027, 3, 10),
        date(2027, 3, 17)
    )
    assert len(conflicts) == 0