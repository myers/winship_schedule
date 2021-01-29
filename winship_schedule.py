#!/usr/bin/env python3

import sys, pprint
from datetime import date, timedelta

"""
Hot Weeks - 8 weeks before the Tate Annual Weekend, and 2 weeks after
Early Warm Weeks - 5 weeks before start of hot weeks
Late Warm Weeks - 5 weeks after Tate Annual Weekend
Early Cool Weeks - 5 weeks before Early Warm weeks
Late Cool Weeks - 5 weeks after Late Warn weeks
Cold Weeks - 10 after Late Cool weeks

Tate Annual Weekend - 1nd Sat in Aug and the following Sunday
Tate Annual Week - week before Tate Annual Weekend

Each 5% share will have a different schedule on even and odd years.  One
year they will have 1 Hot week and 1 Coldest week, the next they will have 1
Warm Week and 1 Cold Week.

The end result is that folks with 10% or greater will have 1 or more weeks
spread out over all 4 types of weeks.
"""


"""
Richard K           10%
Joe K               5%
Jim K               5%
Frank M             10%
A, C, T Hankey      10%
Will C              5%
Becca C             5%
"Lane C"            10%
Eddie L             10%
"D, H, AL L"        10%
Hayley & Jorden P   10%
Frank L             10%
"""



SHARE_WEEKS = [
  'becca-1',
  'becca-2',
  'david_hugh_ann_laurel-1',
  'david_hugh_ann_laurel-2',
  'david_hugh_ann_laurel-3',
  'david_hugh_ann_laurel-4',
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
  'myers-1',
  'myers-2',
  'lane-1',
  'lane-2',
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


            # 'hankey-1',
            # 'prentiss-1',
            # 'frank_may-1',
            # '',
            # 'eddie-1',
            # 'myers-1',
            # 'david_hugh_ann_laurel-1',
            # 'richard-1',
            # 'frank_latimer-1',
            # '',


SCHEDULE = {
    'odd' : {
        'cool': [
            'prentiss-1',
            'myers-1',
            'eddie-1',
            'richard-1',
            'hankey-1',
            'frank_latimer-1',
            'becca-1',
            'david_hugh_ann_laurel-1',
            'frank_may-1',
            'jim-1',
        ],
        'warm': [
            'david_hugh_ann_laurel-2',
            'hankey-2',
            'frank_latimer-2',
            'frank_may-2',
            'jim-2',
            'becca-2',
            'prentiss-2',
            'myers-2',
            'eddie-2',
            'richard-2',
        ],
        'hot': [
            'frank_latimer-3',
            'joe-1',
            'hankey-3',
            'lane-1',
            'frank_may-3',
            'eddie-3',
            'prentiss-3',
            'will-1',
            'david_hugh_ann_laurel-3',
            'richard-3',
        ],
        'cold': [
            'will-2',
            'eddie-4',
            'frank_may-4',
            'frank_latimer-4',
            'richard-4',
            'lane-2',
            'hankey-4',
            'prentiss-4',
            'joe-2',
            'david_hugh_ann_laurel-4',
        ],
    },
    'even': {
        'cool': [
            'lane-1',
            'david_hugh_ann_laurel-1',
            'richard-1',
            'frank_latimer-1',
            'will-1',
            'hankey-1',
            'prentiss-1',
            'frank_may-1',
            'joe-1',
            'eddie-1',
        ],
        'warm': [
            'eddie-2',
            'will-2',
            'prentiss-2',
            'lane-2',
            'richard-2',
            'david_hugh_ann_laurel-2',
            'frank_latimer-2',
            'hankey-2',
            'frank_may-2',
            'joe-2',
        ],
        'hot': [
            'prentiss-3',
            'becca-1',
            'frank_may-3',
            'eddie-3',
            'richard-3',
            'frank_latimer-3',
            'david_hugh_ann_laurel-3',
            'jim-1',
            'hankey-3',
            'myers-1',
        ],
        'cold': [
            'richard-4',
            'myers-2',
            'hankey-4',
            'prentiss-4',
            'jim-2',
            'david_hugh_ann_laurel-4',
            'becca-2',
            'eddie-4',
            'frank_may-4',
            'frank_latimer-4',
        ],
    }
}

def memorial_day_week_start(year):
    """
    >>> memorial_day_week_start(2020)
    datetime.date(2020, 5, 17)
    """
    ret = memorial_day(year) - timedelta(days=8)
    assert_sunday(ret)
    return ret

def memorial_day(year):
    """
    last Monday of May
    """
    ret = date(year, 5, 31)
    while ret.weekday() != 0: # while it's not monday
        ret = ret - timedelta(days=1)
    return ret


def labor_day_week_start(year):
    """
    >>> labor_day_week_start(2020)
    datetime.date(2020, 8, 30)
    """
    ret = labor_day(year) - timedelta(days=8)
    assert_sunday(ret)
    return ret

def labor_day(year):
    """
    first Monday of September

    >>> labor_day(2020)
    datetime.date(2020, 9, 7)
    """
    ret = date(year, 9, 1)
    while ret.weekday() != 0: # while it's not monday
        ret = ret + timedelta(days=1)
    return ret

def independence_day(year):
    return date(year, 7, 4)

def independence_day_week_start(year):
    """
    >>> independence_day_week_start(2020)
    datetime.date(2020, 6, 28)
    """
    ind = independence_day(year)
    return ind - timedelta(days=ind.weekday()+1)

def thanksgiving_week_start(year):
    """
    >>> thanksgiving_week_start(2020)
    datetime.date(2020, 11, 22)
    """
    ret = thanksgiving(year) - timedelta(days=4)
    assert_sunday(ret)
    return ret

def thanksgiving(year):
    """
    the fourth Thursday of November.
    """
    ret = date(year, 11, 1)
    while ret.weekday() != 3: # while it's not thursday
        ret = ret + timedelta(days=1)
    return ret + timedelta(days=21)

def christmas_week_start(year):
    """
    >>> christmas_week_start(2020)
    datetime.date(2020, 12, 20)
    """
    xmas = christmas(year)
    return xmas - timedelta(days=xmas.weekday()+1)

def christmas(year):
    return date(year, 12, 25)

def tate_annual_meeting(year):
    """
    first Saturday in aug
    """
    ret = date(year=year, month=8, day=1)
    while ret.weekday() != 5:
        ret = ret + timedelta(days=1)
    return ret

def tate_annual_week_start(year):
    return tate_annual_meeting(year) - timedelta(days=6)

def hot_weeks_start(year):
    return tate_annual_week_start(year) - timedelta(days=7*8)

def early_warm_weeks_start(year):
    return hot_weeks_start(year) - timedelta(days=7*5)

def assert_sunday(date):
    assert date.weekday() == 6, date.strftime("%a %x")

def early_cool_weeks_start(year):
    ret = early_warm_weeks_start(year) - timedelta(days=7*5)
    assert_sunday(ret)
    return ret

def late_warm_weeks_start(year):
    return tate_annual_week_start(year) + timedelta(days=7*3)

def late_cool_weeks_start(year):
    return late_warm_weeks_start(year) + timedelta(days=7*5)

def cold_weeks_start(year):
    return late_cool_weeks_start(year) + timedelta(days=7*5)

def share_name_to_name(share):
    return share.split("-")[0].replace("_", " ").title()

class Week:
    def __init__(self, start, share):
        self.start = start
        self.share = share

class WeeksChunk:
    def __init__(self, name, weeks):
        self.name = name
        self.weeks = weeks

from collections import namedtuple, deque

AllocatedWeek = namedtuple('AllocatedWeek', ('start', 'end', 'share', 'holiday'), defaults=(None,))

class HouseYear:
    def __init__(self, year):
        self.year = year
        self.cool_weeks = CoolWeeks(year)
        self.warm_weeks = WarmWeeks(year)
        self.hot_weeks = HotWeeks(year)
        self.cold_weeks = ColdWeeks(year)

    def chunks(self):
        yield WeeksChunk("Early Cool Weeks", list(self.cool_weeks.weeks())[:5])
        yield WeeksChunk("Early Warm Weeks", list(self.warm_weeks.weeks())[:5])

        yield WeeksChunk("Hot Weeks", list(self.hot_weeks.weeks())[:8])
        tam = AllocatedWeek(start=tate_annual_week_start(self.year), end=tate_annual_week_start(self.year)+timedelta(days=7), share="Party!")
        yield WeeksChunk("Tate Annual Week", [tam])
        yield WeeksChunk("Hot Weeks (continued)", list(self.hot_weeks.weeks())[8:])
        yield WeeksChunk("Late Warm Weeks", list(self.warm_weeks.weeks())[5:])
        yield WeeksChunk("Late Cool Weeks", list(self.cool_weeks.weeks())[5:])
        yield WeeksChunk("Cold Weeks", list(self.cold_weeks.weeks()))

class HouseWeeks:
    def __init__(self, year):
        self.year = year

    def year_type(self):
        year_type = 'even'
        if self.year % 2 == 1:
            year_type = 'odd'
        return year_type

    def schedule_offset(self):
        return int((self.year - 2020)/2)

    def add_n_weeks(self, start, count):
        assert_sunday(start)
        current = start
        ret = []
        for ii in range(count):
            ret.append(current)
            current = current + timedelta(days=7)
        return ret

    def shares(self):
        shares = SCHEDULE[self.year_type()][self.week_type][:]
        shares = deque(shares)
        shares.rotate(self.schedule_offset())
        shares = list(shares)
        return shares

class ColdWeeks(HouseWeeks):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.week_type = 'cold'

    def week_starts(self):
        ret = []
        ret.extend(self.add_n_weeks(cold_weeks_start(self.year), 10))
        return ret

    def weeks(self):
        shares = self.shares()
        week_starts = self.week_starts()

        ret = []

        thxgiving = thanksgiving_week_start(self.year)
        week_starts = [x for x in week_starts if x != thxgiving]
        assert len(week_starts) == 9
        ret.append(AllocatedWeek(start=thxgiving, end=thxgiving+timedelta(days=6), share=shares.pop(0), holiday="Thanksgiving"))

        xmas = christmas_week_start(self.year)
        week_starts = [x for x in week_starts if x != xmas]
        assert len(week_starts) == 8
        ret.append(AllocatedWeek(start=xmas, end=xmas+timedelta(days=6), share=shares.pop(0), holiday="Christmas"))

        for start in week_starts:
            ret.append(AllocatedWeek(start=start, end=start+timedelta(days=6), share=shares.pop(0)))

        ret.sort(key=lambda x: x.start)
        return ret

class WarmWeeks(HouseWeeks):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.week_type = 'warm'

    def week_starts(self):
        ret = []
        ret.extend(self.add_n_weeks(early_warm_weeks_start(self.year), 5))
        ret.extend(self.add_n_weeks(late_warm_weeks_start(self.year), 5))
        return ret

    def weeks(self):
        shares = self.shares()
        week_starts = self.week_starts()

        ret = []

        md = memorial_day_week_start(self.year)
        week_starts = [x for x in week_starts if x != md]
        assert len(week_starts) == 9
        ret.append(AllocatedWeek(start=md, end=md+timedelta(days=9), share=shares.pop(0), holiday="Memorial Day"))

        ld = labor_day_week_start(self.year)
        week_starts = [x for x in week_starts if x != ld]
        assert len(week_starts) == 8
        ret.append(AllocatedWeek(start=ld, end=ld+timedelta(days=9), share=shares.pop(0), holiday="Labor Day"))

        for start in week_starts:
            if start == md + timedelta(days=7) or start == ld + timedelta(days=7):
                ret.append(AllocatedWeek(start=start+timedelta(days=2), end=start+timedelta(days=7), share=shares.pop(0)))
            else:
                ret.append(AllocatedWeek(start=start, end=start+timedelta(days=7), share=shares.pop(0)))

        ret.sort(key=lambda x: x.start)
        return ret

class HotWeeks(HouseWeeks):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.week_type = 'hot'

    def week_starts(self):
        ret = []
        ret.extend(self.add_n_weeks(hot_weeks_start(self.year), 8))
        ret.extend(self.add_n_weeks(tate_annual_week_start(self.year) + timedelta(days=7), 2))
        return ret

    def weeks(self):
        shares = self.shares()
        week_starts = self.week_starts()

        ret = []

        ind = independence_day_week_start(self.year)
        week_starts = [x for x in week_starts if x != ind]
        assert len(week_starts) == 9
        ret.append(AllocatedWeek(start=ind, end=ind+timedelta(days=7), share=shares.pop(0), holiday="Independence Day"))

        for start in week_starts:
            ret.append(AllocatedWeek(start=start, end=start+timedelta(days=7), share=shares.pop(0)))

        ret.sort(key=lambda x: x.start)
        return ret

class CoolWeeks(HouseWeeks):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.week_type = 'cool'

    def week_starts(self):
        ret = []
        ret.extend(self.add_n_weeks(early_cool_weeks_start(self.year), 5))
        ret.extend(self.add_n_weeks(late_cool_weeks_start(self.year), 5))
        return ret

    def weeks(self):
        for idx, start in enumerate(self.week_starts()):
            offset = (idx + self.schedule_offset()) % 10
            share = SCHEDULE[self.year_type()][self.week_type][offset]
            yield AllocatedWeek(start=start, end=start+timedelta(days=7), share=share)


if __name__ == "__main__":
    import doctest
    ret = doctest.testmod()
    if ret.failed > 0:
        sys.exit(1)


    for year in range(2020, 2051):
        print(year, cold_weeks_end(year))
        if memorial_day_week_start(year) >= hot_weeks_start(year):
            print(f"In {year} memorial_day is in the hot weeks")

    # for year in range(2021, 2025):
    #     print("-"*20)
    #     print(year)
    #     print("-"*20)
    #     l = [
    #         (early_cool_weeks_start(year), "Early Cool Weeks Start",),
    #         (memorial_day_week_start(year), "Memorial Day Week Start",),
    #         (labor_day_week_start(year), "Labor Day Week Start",),
    #         (independence_day_week_start(year), "Independence Day Week Start",),
    #         (tate_annual_week_start(year), "Tate Annual Meeting Week Start",),
    #         (early_warm_weeks_start(year), "Early Warm Weeks Start",),
    #         (hot_weeks_start(year), "Hot Weeks Start",),
    #         (late_warm_weeks_start(year), "Late Warm Weeks Start",),
    #         (late_cool_weeks_start(year), "Late Cool Weeks Start",),
    #         (cold_weeks_start(year), "Cold Weeks Start",),
    #     ]
    #     l.sort()

    #     pprint.pprint(l)
