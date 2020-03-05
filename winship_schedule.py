#!/usr/bin/env python3

from datetime import date, timedelta

"""
Hot Weeks - 10 weeks before the Tate Annual Weekend
Early Warm Weeks - 5 weeks before start of hot weeks
Late Warm Weeks - 5 weeks after Tate Annual Weekend
Early Cool Weeks - 5 weeks before Early Warm weeks
Late Cool Weeks - 5 weeks after Late Warn weeks
Cold Weeks - 10 after Late Cool weeks

Tate Annual Weekend - 2nd Sat in Aug and the following Sunday
Tate Annual Week - week before Tate Annual Weekend

Each 5% share will have a different schedule on even and odd years.  One year they will have 1 Hot week and 1 Coldest week, the next they will have 1 Warm Week and 1 Cold Week.

The end result is that folks with 10% or greater will have 1 or more weeks spread out over all 4 types of weeks.
"""


"""
Richard K   10%
Joe K   5%
Jim K   5%
Frank M 10%
A, C, T Hankey  10%
Will C  5%
Becca C 5%
"Lane C
"   10%
Eddie L 10%
"D, H, AL L 
"   10%
Hayley & Jorden P   10%
Frank L 10%
"""



SHARE_WEEKS = [
  'becca-1',
  'becca-2',
  'dhal-1',
  'dhal-2',
  'dhal-3',
  'dhal-4',
  'eddie-1',
  'eddie-2',
  'eddie-3',
  'eddie-4',
  'frank_latimer-1',
  'frank_latimer-2',
  'frank_latimer-3',
  'frank_latimer-4',
  'frank_may-1',
  'frank_may-2',
  'frank_may-3',
  'frank_may-4',
  'hankey-1',
  'hankey-2',
  'hankey-3',
  'hankey-4',
  'jim-1',
  'jim-2',
  'joe-1',
  'joe-2',
  'lane-1',
  'lane-2',
  'lane-3',
  'lane-4',
  'prentiss-1',
  'prentiss-2',
  'prentiss-3',
  'prentiss-4',
  'richard-1',
  'richard-2',
  'richard-3',
  'richard-4',
  'will-1',
  'will-2',
]


SCHEDULE = {
    'odd' : {
        'cool': [
            'hankey-1',
            'prentiss-1',
            'frank_may-1',
            'jim-1',
            'eddie-1',
            'lane-1',
            'dhal-1',
            'richard-1',
            'frank_latimer-1',
            'becca-1',
        ],
        'warm': [
            'frank_latimer-2',
            'hankey-2',
            'frank_may-2',
            'jim-2',
            'eddie-2',
            'becca-2',
            'prentiss-2',
            'lane-2',
            'dhal-2',
            'richard-2',
        ],
        'hot': [
            'frank_latimer-3',
            'dhal-3',
            'joe-1',
            'hankey-3',
            'lane-3',
            'frank_may-3',
            'eddie-3',
            'prentiss-3',
            'will-1',
            'richard-3',

        ],
        'cold': [
            'dhal-4',
            'will-2',
            'eddie-4',
            'frank_may-4',
            'frank_latimer-4',
            'richard-4',
            'lane-4',
            'hankey-4',
            'prentiss-4',
            'joe-2',
        ],
    },
    'even': {
        'cool': [
            'hankey-1',
            'joe-1',
            'eddie-1',
            'dhal-1',
            'prentiss-1',
            'lane-1',
            'will-1',
            'frank_may-1',
            'frank_latimer-1',
            'richard-1',
        ],
        'warm': [
            'dhal-2',
            'hankey-2',
            'prentiss-2',
            'richard-2',
            'frank_latimer-2',
            'frank_may-2',
            'eddie-2',
            'joe-2',
            'will-2',
            'lane-2',
        ],
        'hot': [
            'frank_latimer-3',
            'hankey-3',
            'dhal-3',
            'eddie-3',
            'becca-1',
            'frank_may-3',
            'richard-3',
            'lane-3',
            'prentiss-3',
            'jim-1',
        ],
        'cold': [
            'richard-4',
            'eddie-4',
            'lane-4',
            'frank_may-4',
            'hankey-4',
            'dhal-4',
            'becca-2',
            'prentiss-4',
            'jim-2',
            'frank_latimer-4',
        ],
    }
}



def tate_annual_weekend_start(year):
    ret = date(year=year, month=8, day=14)
    while ret.weekday() != 5:
        ret = ret + timedelta(days=1)
    return ret

def tate_annual_week_start(year):
    return tate_annual_weekend_start(year) - timedelta(days=6)

def hot_weeks_start(year):
    return tate_annual_week_start(year) - timedelta(days=7*10)

def early_warm_weeks_start(year):
    return hot_weeks_start(year) - timedelta(days=7*5)

def early_cool_weeks_start(year):
    return early_warm_weeks_start(year) - timedelta(days=7*5)

def late_warm_weeks_start(year):
    return tate_annual_weekend_start(year) + timedelta(days=7)

def late_cool_weeks_start(year):
    return late_warm_weeks_start(year) + timedelta(days=7*5)

def cold_weeks_start(year):
    return late_warm_weeks_start(year) + timedelta(days=7*5)

def share_name_to_name(share):
    return share.split("-")[0].replace("_", " ")

def print_next_n_weeks(start, count, week_type=None, week_type_offset=0):
    schedule_offset = int((start.year - 2020)/2)
    year_type = 'even'
    if start.year % 2 == 1:
        year_type = 'odd'

    for ii in range(count):
        offset = (ii + schedule_offset + week_type_offset) % 10
        if week_type is None:
            share = "Party!"
        else:
            share = share_name_to_name(SCHEDULE[year_type][week_type][offset])
        print("\t{} - {}".format((start + timedelta(days=7*ii)).strftime("%x"), share))

def print_year_schedule(year):
    start = early_cool_weeks_start(year)
    print("Early Cool Weeks")
    print_next_n_weeks(start, 5, 'cool')
    print()

    start = early_warm_weeks_start(year)
    print("Early Warm Weeks")
    print_next_n_weeks(start, 5, 'warm')
    print()

    start = hot_weeks_start(year)
    print("Hot Weeks")
    print_next_n_weeks(start, 10, 'hot')
    print()

    print("Tate Annual Week")
    print_next_n_weeks(start, 1)
    print()

    start = late_warm_weeks_start(year)
    print("Late Warm Weeks")
    print_next_n_weeks(start, 5, 'warm', 4)

    print()

    start = late_cool_weeks_start(year)
    print("Late Cool Weeks")
    print_next_n_weeks(start, 5, 'cool', 4)
    print()

    start = cold_weeks_start(year)
    print("Cold Weeks")
    print_next_n_weeks(start, 10, 'cold')


def schedule_check():
    for year_type in SCHEDULE.keys():
        for week_type in SCHEDULE[year_type].keys():
            assert len(SCHEDULE[year_type][week_type]) == 10

if __name__ == "__main__":
    schedule_check()

    for year in range(2020, 2030):
        print(year)
        print()
        print_year_schedule(year)
        print()
        print("-"*80)

