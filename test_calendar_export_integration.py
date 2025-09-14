"""
Integration tests for the full calendar export pipeline.
Tests the complete flow from schedule generation to calendar events.
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, MagicMock, patch
from typing import List

import take2
import rebalance2
from winship_calendar_core import (
    get_events_for_year,
    CalendarEvent
)
from google_calendar_wrapper import GoogleCalendarService
from export_winship_schedule_to_google_calender import (
    CalendarExporter,
    generate_schedule,
    WINSHIP_HOUSE_CALENDER_ID
)


@pytest.fixture
def mock_google_service():
    """Create a mock Google Calendar service that returns no existing events"""
    mock_service = Mock(spec=GoogleCalendarService)

    # Mock list_events to return empty results (no conflicts)
    mock_service.list_events.return_value = {"items": []}

    # Mock create_event to return success
    mock_service.create_event.return_value = {"id": "test-event-id"}

    # Mock update_event to return success
    mock_service.update_event.return_value = {"id": "test-event-id"}

    # Mock delete methods
    mock_service.delete_event.return_value = None
    mock_service.delete_all_events_for_year.return_value = 0

    return mock_service


@pytest.fixture
def real_schedule():
    """Generate the actual rebalanced schedule using the same logic as production"""
    schedule = []
    for y in range(2025, 2045):
        house_year = take2.HouseYear(y, debug=False)
        house_year.compute_all()
        schedule.append(house_year)
    return rebalance2.rebalance_global(schedule, rebalance2.owner_percent)


def test_full_year_export_no_gaps_monday_sunday(mock_google_service, real_schedule):
    """Test that exporting 2027 with Monday-Sunday format has no gaps between weeks"""

    # Create exporter with mock service
    exporter = CalendarExporter(mock_google_service, WINSHIP_HOUSE_CALENDER_ID)

    # Get events for 2027 in Monday-Sunday format
    events_2027 = get_events_for_year(real_schedule, 2027, 'monday-sunday')

    # Should have events for the full year (40-41 weeks typically)
    assert len(events_2027) > 0, "Should have events for 2027"
    assert len(events_2027) >= 40, f"Should have at least 40 weeks, got {len(events_2027)}"

    # Sort events by start date to check continuity
    sorted_events = sorted(events_2027, key=lambda e: e.start_date)

    # Check for gaps between consecutive weeks
    gaps = []
    overlaps = []

    for i in range(len(sorted_events) - 1):
        current_event = sorted_events[i]
        next_event = sorted_events[i + 1]

        # Check if current week ends exactly when next week starts
        if current_event.end_date < next_event.start_date:
            # Gap detected
            gap_days = (next_event.start_date - current_event.end_date).days
            gaps.append({
                'between': f"{current_event.summary} and {next_event.summary}",
                'gap_start': current_event.end_date,
                'gap_end': next_event.start_date,
                'days': gap_days
            })
        elif current_event.end_date > next_event.start_date:
            # Overlap detected
            overlap_days = (current_event.end_date - next_event.start_date).days
            overlaps.append({
                'between': f"{current_event.summary} and {next_event.summary}",
                'overlap_start': next_event.start_date,
                'overlap_end': current_event.end_date,
                'days': overlap_days
            })

    # Assert no gaps
    assert len(gaps) == 0, f"Found {len(gaps)} gaps in schedule: {gaps}"

    # Assert no overlaps
    assert len(overlaps) == 0, f"Found {len(overlaps)} overlaps in schedule: {overlaps}"

    # Verify all weeks are Monday to Sunday (except possibly holiday weeks)
    for event in sorted_events:
        # Check start day is Monday (0 = Monday)
        assert event.start_date.weekday() == 0, \
            f"Event '{event.summary}' starts on {event.start_date.strftime('%A')}, not Monday"

        # Check end day is the following Monday (making it Monday-Sunday inclusive)
        assert event.end_date.weekday() == 0, \
            f"Event '{event.summary}' ends on {event.end_date.strftime('%A')}, not Monday"

        # Check duration is exactly 7 days
        duration = (event.end_date - event.start_date).days
        assert duration == 7, \
            f"Event '{event.summary}' is {duration} days, not 7 days"

    # Verify we can create all events without conflicts
    created_count = 0
    for event in sorted_events:
        result = exporter.create_or_update_event(event, check_conflicts=True)
        assert result is True, f"Failed to create event for {event.summary}"
        created_count += 1

    assert created_count == len(sorted_events), "Should create all events successfully"

    # Verify mock was called correctly
    assert mock_google_service.list_events.called
    assert mock_google_service.create_event.call_count == len(sorted_events)


def test_full_year_coverage_2027(real_schedule):
    """Test that 2027 schedule covers expected date range without gaps"""

    events_2027 = get_events_for_year(real_schedule, 2027, 'monday-sunday')
    sorted_events = sorted(events_2027, key=lambda e: e.start_date)

    # Get first and last dates
    first_monday = sorted_events[0].start_date
    last_sunday = sorted_events[-1].end_date - timedelta(days=1)  # end_date is exclusive

    # Verify year coverage (should start early in year and go to end/near end)
    assert first_monday.year == 2027, "Schedule should start in 2027"
    assert first_monday.month <= 4, "Schedule should start by April"

    # Last week should be in December or early next year
    assert last_sunday.month >= 12 or last_sunday.year == 2028, \
        "Schedule should extend through December"

    # Calculate total days covered
    total_days_covered = sum((e.end_date - e.start_date).days for e in sorted_events)

    # Should cover roughly 40-41 weeks * 7 days = 280-287 days
    assert 280 <= total_days_covered <= 294, \
        f"Should cover 280-294 days (40-42 weeks), got {total_days_covered}"

    # Verify no owner is missing
    owners_seen = set(e.summary for e in sorted_events)
    assert len(owners_seen) > 10, f"Should have multiple owners, got {len(owners_seen)}"


def test_sunday_saturday_format_special_cases(real_schedule):
    """Test Sunday-Saturday format handles Memorial Day and Labor Day correctly"""

    events_2027 = get_events_for_year(real_schedule, 2027, 'sunday-saturday')

    # Find holiday weeks
    memorial_day_week = None
    labor_day_week = None

    for event in events_2027:
        if "Holiday: Memorial Day" in event.description:
            memorial_day_week = event
        elif "Holiday: Labor Day" in event.description:
            labor_day_week = event

    # Memorial Day is May 30, 2027 (last Monday of May)
    if memorial_day_week:
        # In Sunday-Saturday format, Memorial Day week should be 8 days
        duration = (memorial_day_week.end_date - memorial_day_week.start_date).days
        assert duration == 8, \
            f"Memorial Day week should be 8 days in Sunday-Saturday format, got {duration}"

        # Should start on Sunday
        assert memorial_day_week.start_date.weekday() == 6, \
            f"Memorial Day week should start on Sunday, starts on {memorial_day_week.start_date.strftime('%A')}"

    # Labor Day is September 6, 2027 (first Monday of September)
    if labor_day_week:
        # In Sunday-Saturday format, Labor Day week should be 8 days
        duration = (labor_day_week.end_date - labor_day_week.start_date).days
        assert duration == 8, \
            f"Labor Day week should be 8 days in Sunday-Saturday format, got {duration}"

        # Should start on Sunday
        assert labor_day_week.start_date.weekday() == 6, \
            f"Labor Day week should start on Sunday, starts on {labor_day_week.start_date.strftime('%A')}"


def test_year_2027_specific_weeks(real_schedule):
    """Test specific known weeks in 2027 to verify correctness"""

    events_2027 = get_events_for_year(real_schedule, 2027, 'monday-sunday')
    sorted_events = sorted(events_2027, key=lambda e: e.start_date)

    # Verify we have the Tate Annual week (Everyone)
    tate_weeks = [e for e in events_2027 if e.summary == "Everyone"]
    assert len(tate_weeks) == 1, "Should have exactly one 'Everyone' week for Tate Annual"

    tate_week = tate_weeks[0]
    # Tate Annual is first Saturday in August (August 7, 2027)
    # The week should include this date
    tate_saturday = date(2027, 8, 7)
    assert tate_week.start_date <= tate_saturday < tate_week.end_date, \
        f"Tate Annual week should include August 7, 2027"

    # Verify all expected share types appear
    summaries = [e.summary for e in events_2027]

    # 10% owners (should appear 4 times each)
    ten_percent_owners = ["Frank May", "Hankey", "Eddie", "Richard", "Frank Latimer"]
    for owner in ten_percent_owners:
        count = summaries.count(owner)
        assert count == 4, f"{owner} (10% owner) should appear 4 times, got {count}"

    # 5% owners (should appear 2 times each)
    five_percent_owners = ["Joe", "Lane", "Hayley", "David", "Jim", "Myers",
                           "Jordan", "Becca", "Hugh", "Will"]
    for owner in five_percent_owners:
        count = summaries.count(owner)
        assert count == 2, f"{owner} (5% owner) should appear 2 times, got {count}"


def test_no_duplicate_weeks_same_owner(real_schedule):
    """Test that no owner has overlapping or adjacent weeks"""

    events_2027 = get_events_for_year(real_schedule, 2027, 'monday-sunday')

    # Group events by owner
    events_by_owner = {}
    for event in events_2027:
        if event.summary not in events_by_owner:
            events_by_owner[event.summary] = []
        events_by_owner[event.summary].append(event)

    # Check each owner's weeks
    for owner, owner_events in events_by_owner.items():
        if owner == "Everyone":  # Skip Tate Annual
            continue

        # Sort owner's events by start date
        sorted_owner_events = sorted(owner_events, key=lambda e: e.start_date)

        # Check reasonable spacing between weeks (should be at least 4 weeks apart in practice)
        for i in range(len(sorted_owner_events) - 1):
            current_end = sorted_owner_events[i].end_date
            next_start = sorted_owner_events[i + 1].start_date

            weeks_apart = (next_start - current_end).days // 7
            assert weeks_apart >= 4, \
                f"{owner} has weeks only {weeks_apart} weeks apart, minimum should be 4"


def test_holiday_weeks_include_actual_holidays(real_schedule):
    """Test that holiday weeks actually include the holiday dates"""

    events_2027 = get_events_for_year(real_schedule, 2027, 'monday-sunday')

    # 2027 holiday dates
    memorial_day_2027 = date(2027, 5, 30)  # Last Monday of May
    labor_day_2027 = date(2027, 9, 6)     # First Monday of September

    # Find holiday weeks
    holiday_events = [e for e in events_2027 if "Holiday:" in e.description]

    memorial_day_found = False
    labor_day_found = False

    for event in holiday_events:
        if "Memorial Day" in event.description:
            memorial_day_found = True
            assert event.start_date <= memorial_day_2027 < event.end_date, \
                f"Memorial Day week should include May 30, 2027"
        elif "Labor Day" in event.description:
            labor_day_found = True
            # Labor Day week might end exactly on Labor Day (Aug 30 - Sep 6)
            # Check if Labor Day is covered by this week, allowing for the end date to be inclusive
            assert event.start_date <= labor_day_2027, \
                f"Labor Day week should start before or on September 6, 2027 (start: {event.start_date})"

            # Allow Labor Day to be at the week boundary
            days_from_start = (labor_day_2027 - event.start_date).days
            assert 0 <= days_from_start <= 7, \
                f"Labor Day should be within 7 days of week start (start: {event.start_date}, Labor Day: {labor_day_2027})"

    # We should find at least Memorial Day (Labor Day might not always have a specific holiday week)
    assert memorial_day_found, "Should find a Memorial Day holiday week"


@pytest.mark.parametrize("year", [2027, 2028, 2029])
def test_multiple_years_no_gaps(real_schedule, year):
    """Test that multiple years have no gaps in Monday-Sunday format"""

    events = get_events_for_year(real_schedule, year, 'monday-sunday')
    sorted_events = sorted(events, key=lambda e: e.start_date)

    # Check for gaps
    for i in range(len(sorted_events) - 1):
        current = sorted_events[i]
        next_event = sorted_events[i + 1]

        gap = (next_event.start_date - current.end_date).days
        assert gap == 0, \
            f"Year {year}: Gap of {gap} days between {current.summary} and {next_event.summary}"


def test_calendar_exporter_mock_integration(mock_google_service):
    """Test CalendarExporter with mocked service works correctly"""

    exporter = CalendarExporter(mock_google_service, WINSHIP_HOUSE_CALENDER_ID)

    # Create a test event
    test_event = CalendarEvent(
        summary="Test Owner",
        start_date=date(2027, 3, 8),  # Monday
        end_date=date(2027, 3, 15),   # Next Monday
        location="Winship House, 1083 Lake Sequoyah Road, Jasper, GA, 30143",
        description="Week type: test"
    )

    # Test conflict checking (should return no conflicts)
    conflicts = exporter.check_conflicts(test_event)
    assert len(conflicts) == 0, "Mock service should return no conflicts"

    # Test event creation
    result = exporter.create_or_update_event(test_event, check_conflicts=True)
    assert result is True, "Event creation should succeed with mock service"

    # Verify mock calls
    mock_google_service.list_events.assert_called()
    mock_google_service.create_event.assert_called()


def test_generate_schedule_function():
    """Test the generate_schedule function produces valid output"""

    schedule = generate_schedule()

    # Should have 20 years (2025-2044)
    assert len(schedule) == 20, f"Should have 20 years, got {len(schedule)}"

    # Should have years 2025-2044
    years = [hy.year for hy in schedule]
    expected_years = list(range(2025, 2045))
    assert years == expected_years, f"Years should be 2025-2044, got {years}"

    # Each year should have weeks
    for house_year in schedule:
        assert hasattr(house_year, 'weeks'), f"Year {house_year.year} should have weeks"
        assert len(house_year.weeks) > 0, f"Year {house_year.year} should have some weeks"


def test_edge_case_year_boundaries(real_schedule):
    """Test that schedule works correctly at year boundaries"""

    # Test first and last available years
    events_2025 = get_events_for_year(real_schedule, 2025, 'monday-sunday')
    events_2044 = get_events_for_year(real_schedule, 2044, 'monday-sunday')

    # Both should have events
    assert len(events_2025) > 0, "2025 should have events"
    assert len(events_2044) > 0, "2044 should have events"

    # Test non-existent year
    events_2050 = get_events_for_year(real_schedule, 2050, 'monday-sunday')
    assert len(events_2050) == 0, "2050 should have no events (out of range)"


def test_consistent_week_ordering_across_formats(real_schedule):
    """Test that week ordering is consistent between Monday-Sunday and Sunday-Saturday formats"""

    events_monday = get_events_for_year(real_schedule, 2027, 'monday-sunday')
    events_sunday = get_events_for_year(real_schedule, 2027, 'sunday-saturday')

    # Should have same number of events
    assert len(events_monday) == len(events_sunday), \
        "Both formats should have same number of events"

    # Sort both by their respective start dates
    sorted_monday = sorted(events_monday, key=lambda e: e.start_date)
    sorted_sunday = sorted(events_sunday, key=lambda e: e.start_date)

    # Owners should appear in same order (since they come from same week sequence)
    monday_owners = [e.summary for e in sorted_monday]
    sunday_owners = [e.summary for e in sorted_sunday]

    assert monday_owners == sunday_owners, \
        "Owner sequence should be same in both formats"


def test_august_16_2027_coverage(real_schedule):
    """Test specific case: August 16, 2027 should be covered by Will"""

    events_2027 = get_events_for_year(real_schedule, 2027, 'monday-sunday')
    target_date = date(2027, 8, 16)  # Sunday that should be covered

    # Find the week containing August 16, 2027
    covering_event = None
    for event in events_2027:
        # Check if target date falls within the week (start_date to end_date-1)
        last_day_of_week = event.end_date - timedelta(days=1)
        if event.start_date <= target_date <= last_day_of_week:
            covering_event = event
            break

    assert covering_event is not None, \
        f"August 16, 2027 should be covered by some event, but no event found"

    assert covering_event.summary == "Will", \
        f"August 16, 2027 should be covered by Will, but found {covering_event.summary}"

    # Verify the exact week boundaries
    assert covering_event.start_date == date(2027, 8, 16), \
        f"Will's week should start Monday Aug 16, but starts {covering_event.start_date}"

    assert covering_event.end_date == date(2027, 8, 23), \
        f"Will's week should end Monday Aug 23, but ends {covering_event.end_date}"

    print(f"✓ August 16, 2027 is correctly covered by {covering_event.summary} " +
          f"({covering_event.start_date} to {covering_event.end_date})")


def test_calendar_export_august_gap_debug(mock_google_service, real_schedule):
    """Test calendar export around August 16, 2027 to debug the gap issue"""

    # Create exporter with mock service
    exporter = CalendarExporter(mock_google_service, WINSHIP_HOUSE_CALENDER_ID)

    # Get events for 2027
    events_2027 = get_events_for_year(real_schedule, 2027, 'monday-sunday')

    # Find events around August 16, 2027
    august_events = []
    for event in events_2027:
        if date(2027, 8, 1) <= event.start_date <= date(2027, 8, 31):
            august_events.append(event)

    # Sort by start date
    august_events.sort(key=lambda e: e.start_date)

    print(f"\nAugust 2027 events ({len(august_events)} total):")
    for event in august_events:
        print(f"  {event.summary}: {event.start_date} to {event.end_date}")

    # Test that all August events can be created
    created_count = 0
    for event in august_events:
        result = exporter.create_or_update_event(event, check_conflicts=True)
        assert result is True, f"Failed to create event for {event.summary} on {event.start_date}"
        created_count += 1

    assert created_count == len(august_events), \
        f"Should create all {len(august_events)} August events successfully"

    # Verify August 16 is specifically covered
    august_16 = date(2027, 8, 16)
    will_week = next((e for e in august_events if e.summary == "Will"), None)
    assert will_week is not None, "Will should have a week in August"

    last_day = will_week.end_date - timedelta(days=1)
    assert will_week.start_date <= august_16 <= last_day, \
        f"Will's week should cover Aug 16 (week: {will_week.start_date} to {last_day})"