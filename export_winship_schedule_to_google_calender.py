#!/usr/bin/env python3
import datetime
import time

import winship_schedule
import google_calender


WINSHIP_HOUSE_CALENDER_ID = 'maski.org_rphaqm5b55daqion1cubolqfpk@group.calendar.google.com'

def list_calenders():
    service = google_calender.get_calender_service()
    res = service.calendarList().list().execute()
    for item in res["items"]:
        print(item['summary'], item['id'])


def create_event_for_week(week, service):
    event = {
      'summary': winship_schedule.share_name_to_name(week.share),
      'location': 'Winship House, 1083 Lake Sequoyah Road, Jasper, GA, 30143',
      'start': {
        'date': week.start.isoformat(),
        'timeZone': 'America/New_York',
      },
      'end': {
        'date': week.end.isoformat(),
        'timeZone': 'America/New_York',
      },
    }

    event = service.events().insert(calendarId=WINSHIP_HOUSE_CALENDER_ID, body=event).execute()

def delete_all_events(service):
    page_token = None
    while True:
        events_result = service.events().list(calendarId=WINSHIP_HOUSE_CALENDER_ID, pageToken=page_token).execute()
        for event in events_result.get('items', []):
            print("deleteing {}".format(event['id']))
            kwargs = {
                'calendarId': WINSHIP_HOUSE_CALENDER_ID,
                'eventId': event['id'],
                'sendNotifications': False
            }
            rq = service.events().delete(**kwargs)
            resp = rq.execute()
            print("sleeping for 30 seconds")
            time.sleep(30)
        page_token = events_result.get('nextPageToken')
        if not page_token:
            break


def main(year=2023):
    service = google_calender.get_calender_service()

    #delete_all_events(service)
    house_year = winship_schedule.HouseYear(year)

    for chunk in house_year.chunks():
        for week in chunk.weeks:
            create_event_for_week(week, service)

if __name__ == "__main__":
    main()
