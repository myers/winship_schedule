#!/usr/bin/env python3

from collections import namedtuple, deque
import sys
import pprint
from datetime import date, timedelta
from date_finders import *

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
Hayley & Jordan P   10%
Frank L             10%
"""


SHARE_WEEKS = [
    "becca-1",
    "becca-2",
    "david-1",
    "david-2",
    "hugh_ann_laurel-1",
    "hugh_ann_laurel-2",
    "eddie-1",
    "eddie-2",
    "eddie-3",
    "eddie-4",
    "frank_latimer-1",
    "frank_latimer-2",
    "frank_latimer-3",
    "frank_latimer-4",
    "frank_may-1",
    "frank_may-2",
    "frank_may-3",
    "frank_may-4",
    "hankey-1",
    "hankey-2",
    "hankey-3",
    "hankey-4",
    "jim-1",
    "jim-2",
    "joe-1",
    "joe-2",
    "myers-1",
    "myers-2",
    "lane-1",
    "lane-2",
    "hayley-1",
    "hayley-2",
    "jordan-2",
    "jordan-1",
    "richard-1",
    "richard-2",
    "richard-3",
    "richard-4",
    "will-1",
    "will-2",
]

# 'hankey-1',
# 'hayley-1',
# 'frank_may-1',
# '',
# 'eddie-1',
# 'myers-1',
# 'david-1',
# 'richard-1',
# 'frank_latimer-1',
# '',

#             "hayley-1",
#             "myers-1",
#             "becca-1",
#            "david-1",
#             "jim-1",


SCHEDULE = {
    "odd": {
        "cool": [
            "richard-3",
            "frank_latimer-3",
            "hayley-1",
            "hankey-3",
            "myers-1",
            "frank_may-3",
            "eddie-3",
            "becca-1",
            "david-1",
            "jim-1",
        ],
        "hot": [
            "richard-3",
            "frank_latimer-3",
            "joe-1",
            "hankey-3",
            "lane-1",
            "frank_may-3",
            "eddie-3",
            "jordan-2",
            "will-1",
            "hugh_ann_laurel-1",
        ],
    },
    "even": {
        "cool": [
            "will-1",
            "hugh_ann_laurel-1",
            "lane-1",
            "hankey-1",
            "frank_latimer-1",
            "eddie-1",
            "richard-1",
            "hayley-1",
            "frank_may-1",
            "joe-1",
        ],
        "hot": [
            "myers-1",
            "jordan-2",
            "hankey-3",
            "becca-1",
            "frank_may-3",
            "eddie-3",
            "richard-3",
            "frank_latimer-3",
            "david-1",
            "jim-1",
        ],
    },
}

SCHEDULE["odd"]["warm"] = list(reversed(SCHEDULE["odd"]["cool"]))
SCHEDULE["odd"]["cold"] = list(reversed(SCHEDULE["odd"]["hot"]))

SCHEDULE["even"]["warm"] = list(reversed(SCHEDULE["even"]["cool"]))
SCHEDULE["even"]["cold"] = list(reversed(SCHEDULE["even"]["hot"]))

def share_name_to_name(share):
    ret = share.split("-")[0].replace("_", " ").title()
    if ret == "Hankey":
        return "Charlie"
    if ret == "Hugh Ann Laurel":
        return "Hugh & Ann Laurel"
    return ret



class Week:
    def __init__(self, start, share):
        self.start = start
        self.share = share


class WeeksChunk:
    def __init__(self, name, weeks):
        self.name = name
        self.weeks = weeks


AllocatedWeek = namedtuple(
    "AllocatedWeek", ("start", "end", "share", "holiday"), defaults=(None,)
)


# how many weeks should we test to make sure someone doesn't have another week after (e.g. I shouldn't have two weeks at date only 6 weeks apart)
MIN_WEEKS_BETWEEN_ALLOCATED = 7

MAX_WEEKS_BETWEEN_ALLOCATED = 15


def check_house_year(year):
    """
    check all the time is claimed  (week_end = next_week_start + 1 day)
    """

    problems = []

    # k: name, val: last iso week they were in the house
    last_weeks = {}
    hy = HouseYear(year)
    last_week = None
    for chunk in hy.chunks():
        # print(chunk.name)
        for week in chunk.weeks:
            # make sure
            name = week.share.split("-")[0]
            week_number = week.start.isocalendar()[1]
            if name in last_weeks:
                n_weeks_ago = week_number - last_weeks[name]
                if n_weeks_ago < MIN_WEEKS_BETWEEN_ALLOCATED:
                    problems.append(
                        f"{week.start!r} {name} had their allocated week only {n_weeks_ago} weeks ago"
                    )
                if n_weeks_ago > MAX_WEEKS_BETWEEN_ALLOCATED:
                    problems.append(
                        f"{week.start!r} {name} had their allocated week {n_weeks_ago} weeks ago"
                    )

            last_weeks[name] = week_number

            # print(f"\t{week!r}")
            if last_week is None:
                last_week = week
            else:
                assert (
                    last_week.end == week.start
                ), f"{last_week.end!r} should equal {week.start!r}"
                last_week = week
    if problems:
        pprint.pprint(problems)
        return False
    return True


class HouseYear:
    def __init__(self, year):
        self.year = year
        self.cool_weeks = CoolWeeks(year)
        self.warm_weeks = WarmWeeks(year)
        self.hot_weeks = HotWeeks(year)
        self.cold_weeks = ColdWeeks(year)

    def chunks(self):
        cleanup = AllocatedWeek(
            start=cleanup_weekend_start(self.year),
            end=sunday_after(cleanup_weekend_start(self.year)),
            share="Everyone!",
        )
        yield WeeksChunk("Cleanup Weekend", [cleanup])
        yield WeeksChunk("Early Cold Weeks", list(self.cold_weeks.weeks())[:1])
        yield WeeksChunk("Early Cool Weeks", list(self.cool_weeks.weeks())[:5])
        yield WeeksChunk("Early Warm Weeks", list(self.warm_weeks.weeks())[:5])

        yield WeeksChunk(
            "Hot Weeks",
            list(self.hot_weeks.weeks())[
                : hot_weeks_before_tate_annual_week_start(self.year)
            ],
        )
        tam = AllocatedWeek(
            start=tate_annual_week_start(self.year),
            end=tate_annual_week_start(self.year) + timedelta(days=7),
            share="Party!",
        )
        yield WeeksChunk("Tate Annual Week", [tam])
        yield WeeksChunk(
            "Hot Weeks (continued)",
            list(self.hot_weeks.weeks())[
                hot_weeks_before_tate_annual_week_start(self.year) :
            ],
        )
        yield WeeksChunk("Late Warm Weeks", list(self.warm_weeks.weeks())[5:])
        yield WeeksChunk("Late Cool Weeks", list(self.cool_weeks.weeks())[5:])
        yield WeeksChunk("Cold Weeks", list(self.cold_weeks.weeks())[1:])


class HouseWeeks:
    def __init__(self, year):
        self.year = year

    def year_type(self):
        year_type = "even"
        if self.year % 2 == 1:
            year_type = "odd"
        return year_type

    def schedule_offset(self):
        return int((self.year - 2020) / 2)

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
        self.week_type = "cold"

    def week_starts(self):
        ret = []
        ret.extend(self.add_n_weeks(early_cold_weeks_start(self.year), 1))
        ret.extend(self.add_n_weeks(late_cold_weeks_start(self.year), 9))
        return ret

    def weeks(self):
        shares = self.shares()
        week_starts = self.week_starts()

        ret = []

        thxgiving = thanksgiving_week_start(self.year)
        week_starts = [x for x in week_starts if x != thxgiving]
        assert len(week_starts) == 9
        ret.append(
            AllocatedWeek(
                start=thxgiving,
                end=sunday_after(thxgiving),
                share=shares.pop(0),
                holiday="Thanksgiving",
            )
        )

        xmas = christmas_week_start(self.year)
        week_starts = [x for x in week_starts if x != xmas]
        assert len(week_starts) == 8
        ret.append(
            AllocatedWeek(
                start=xmas,
                end=sunday_after(xmas),
                share=shares.pop(0),
                holiday="Christmas",
            )
        )

        for start in week_starts:
            ret.append(
                AllocatedWeek(start=start, end=sunday_after(start), share=shares.pop(0))
            )

        ret.sort(key=lambda x: x.start)
        return ret


class WarmWeeks(HouseWeeks):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.week_type = "warm"

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
        ret.append(
            AllocatedWeek(
                start=md,
                end=md + timedelta(days=9),
                share=shares.pop(0),
                holiday="Memorial Day",
            )
        )

        # Get 10th in the list of shares for labor day
        ld = labor_day_week_start(self.year)
        week_starts = [x for x in week_starts if x != ld]
        assert len(week_starts) == 8
        ret.append(
            AllocatedWeek(
                start=ld,
                end=ld + timedelta(days=9),
                share=shares.pop(4),
                holiday="Labor Day",
            )
        )

        for start in week_starts:
            if start == md + timedelta(days=7):
                start = start + timedelta(days=2)
            if start == ld + timedelta(days=7):
                start = start + timedelta(days=2)
            ret.append(
                AllocatedWeek(start=start, end=sunday_after(start), share=shares.pop(0))
            )

        ret.sort(key=lambda x: x.start)
        return ret


class HotWeeks(HouseWeeks):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.week_type = "hot"

    def week_starts(self):
        ret = []
        ret.extend(
            self.add_n_weeks(
                hot_weeks_start(self.year),
                hot_weeks_before_tate_annual_week_start(self.year),
            )
        )
        ret.extend(
            self.add_n_weeks(
                tate_annual_week_start(self.year) + timedelta(days=7),
                10 - hot_weeks_before_tate_annual_week_start(self.year),
            )
        )
        return ret

    def weeks(self):
        shares = self.shares()
        week_starts = self.week_starts()

        ret = []

        ind = independence_day_week_start(self.year)
        week_starts = [x for x in week_starts if x != ind]
        assert len(week_starts) == 9
        ret.append(
            AllocatedWeek(
                start=ind,
                end=sunday_after(ind),
                share=shares.pop(0),
                holiday="Independence Day",
            )
        )

        for start in week_starts:
            if start == memorial_day(self.year) - timedelta(days=1):
                start = start + timedelta(days=2)
            ret.append(
                AllocatedWeek(start=start, end=sunday_after(start), share=shares.pop(0))
            )

        ret.sort(key=lambda x: x.start)
        return ret


class CoolWeeks(HouseWeeks):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.week_type = "cool"

    def week_starts(self):
        ret = []
        ret.extend(self.add_n_weeks(early_cool_weeks_start(self.year), 5))
        ret.extend(self.add_n_weeks(late_cool_weeks_start(self.year), 5))
        return ret

    def weeks(self):
        for idx, start in enumerate(self.week_starts()):
            offset = (idx + self.schedule_offset()) % 10
            share = SCHEDULE[self.year_type()][self.week_type][offset]
            yield AllocatedWeek(start=start, end=start + timedelta(days=7), share=share)


if __name__ == "__main__":
    import doctest

    ret = doctest.testmod()
    if ret.failed > 0:
        sys.exit(1)

    check_house_year(2025)
