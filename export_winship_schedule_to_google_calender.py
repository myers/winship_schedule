#!/usr/bin/env python3
import datetime
import time

import rebalance2
import google_calender
import take2
import logging


WINSHIP_HOUSE_CALENDER_ID = (
    "maski.org_rphaqm5b55daqion1cubolqfpk@group.calendar.google.com"
)


def list_calenders():
    service = google_calender.get_calender_service()
    res = service.calendarList().list().execute()
    for item in res["items"]:
        print(item["summary"], item["id"])


def share_name_to_printable(share_name):
    return share_name.replace("_", " ").title()

def delete_event_for_week(week, service):
    # Calculate end date if not set (week runs for 7 days)
    end_date = week.end if week.end else (week.start + datetime.timedelta(days=7))
    
    # Search for events that match our start and end dates
    events_result = (
        service.events()
        .list(calendarId=WINSHIP_HOUSE_CALENDER_ID,
              timeMin=week.start.isoformat() + "T00:00:00Z",
              timeMax=end_date.isoformat() + "T23:59:59Z")
        .execute()
    )
    
    for event in events_result.get("items", []):
        if ('start' in event and 'date' in event['start'] and 
            'end' in event and 'date' in event['end']):
            event_start = event['start']['date']
            event_end = event['end']['date']
            
            # Check if this event matches our expected dates
            if (event_start == week.start.isoformat() and 
                event_end == end_date.isoformat()):
                print(f"Deleting event: {event.get('summary', 'No title')} from {event_start} to {event_end}")
                service.events().delete(
                    calendarId=WINSHIP_HOUSE_CALENDER_ID,
                    eventId=event["id"],
                    sendNotifications=False
                ).execute()
                return True  # Found and deleted the event
    
    return False  # Event not found


def delete_all_events(service):
    page_token = None
    while True:
        events_result = (
            service.events()
            .list(calendarId=WINSHIP_HOUSE_CALENDER_ID, pageToken=page_token)
            .execute()
        )
        for event in events_result.get("items", []):
            print("deleteing {}".format(event["id"]))
            kwargs = {
                "calendarId": WINSHIP_HOUSE_CALENDER_ID,
                "eventId": event["id"],
                "sendNotifications": False,
            }
            rq = service.events().delete(**kwargs)
            resp = rq.execute()
            print("sleeping for 30 seconds")
            time.sleep(30)
        page_token = events_result.get("nextPageToken")
        if not page_token:
            break


def delete_sunday_events_for_year(service, year):
    """Delete events that start on Sundays for the given year"""
    from datetime import date
    
    # Get events for the entire year
    time_min = f"{year}-01-01T00:00:00Z"
    time_max = f"{year + 1}-01-01T00:00:00Z"
    
    page_token = None
    deleted_count = 0
    
    while True:
        events_result = (
            service.events()
            .list(calendarId=WINSHIP_HOUSE_CALENDER_ID, 
                  timeMin=time_min, 
                  timeMax=time_max,
                  pageToken=page_token)
            .execute()
        )
        
        for event in events_result.get("items", []):
            # Check if event starts on a Sunday
            if 'start' in event and 'date' in event['start']:
                event_date = datetime.datetime.fromisoformat(event['start']['date']).date()
                if event_date.weekday() == 6:  # Sunday is 6
                    print(f"Deleting Sunday event: {event.get('summary', 'No title')} on {event_date}")
                    service.events().delete(
                        calendarId=WINSHIP_HOUSE_CALENDER_ID,
                        eventId=event["id"],
                        sendNotifications=False
                    ).execute()
                    deleted_count += 1
                    time.sleep(1)  # Rate limit
        
        page_token = events_result.get("nextPageToken")
        if not page_token:
            break
    
    print(f"Deleted {deleted_count} Sunday events for {year}")

def main(year=2026):
    # Set logging level to INFO to suppress debug messages
    logging.basicConfig(level=logging.INFO)
    
    service = google_calender.get_calender_service()
    
    # Generate the rebalanced schedule using rebalance2.py logic
    schedule = []
    for y in range(2025, 2045):
        house_year = take2.HouseYear(y, debug=False)
        house_year.compute_all()
        schedule.append(house_year)
    
    # Apply rebalancing
    rebalanced_schedule = rebalance2.rebalance_global(schedule, rebalance2.owner_percent)

    for house_year in rebalanced_schedule:
        if house_year.year != year:
            continue
        print(f"Deleting events for {house_year.year}")
        deleted_count = 0
        for week in house_year.weeks:
            if delete_event_for_week(week, service):
                deleted_count += 1
                print(".", end="", flush=True)
            else:
                print("x", end="", flush=True)  # Event not found
            time.sleep(0.5)  # Rate limiting

        print(f"\nDeleted {deleted_count} events for {year}")


if __name__ == "__main__":
    main()
