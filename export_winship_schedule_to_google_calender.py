#!/usr/bin/env python3
import datetime

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
    events_result = service.events().list(
        calendarId=WINSHIP_HOUSE_CALENDER_ID).execute()
    print(events_result)
    events = events_result.get('items', [])
    for event in events:
        print("deleteing {}".format(event['id']))
        kwargs = {
            'calendarId': WINSHIP_HOUSE_CALENDER_ID,
            'eventId': event['id'],
            'sendNotifications': False
        }
        rq = service.events().delete(**kwargs)
        resp = rq.execute()

def main(year=2020):
    service = google_calender.get_calender_service()

    delete_all_events(service)

    house_year = winship_schedule.HouseYear(year)

    for chunk in house_year.chunks():
        for week in chunk.weeks:
            create_event_for_week(week, service)

if __name__ == "__main__":
    main()
