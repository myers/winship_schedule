#!/usr/bin/env python3

import pprint

from date_finders import *


# build a schedule for the Winship House.  We only use 40 weeks of the year.  10% shares get 4 weeks,
# 5% shares get 2 weeks.

# We want to fairly distribute the hoildays over time.

# We want the 10% shares to have 10 weeks between each of their weeks.

# We want the 5% shares to have either a hot week and a cold week, or one warm week and one cool week.

# We want to make the schedule over 50 years.

"""
Richard K           10%
Frank M             10%
Hankey              10%
Eddie L             10%
Frank L             10%
Joe K               5%
Jim K               5%
Will C              5%
Becca C             5%
Hayley              5%
Jordan              5%
David               5%
Hugh & Ann Laurel   5%
Lane C              5%
"""

ten_precent_shares = [
    "frank_may",
    "hankey",
    "eddie",
    "richard",
    "frank_latimer",
]

five_percent_shares = [
    "joe",
    "lane",
    "hayley",
    "david",
    "jim",
    "myers",
    "jordan",
    "becca",
    "hugh",
    "will",
]

shares_pairs = [
    ("hankey", "hankey"),
    ("joe", "jim"),
    ("eddie", "eddie"),
    ("lane", "myers"),
    ("richard", "richard"),
    ("will", "becca"),
    ("frank_latimer", "frank_latimer"),
    ("hayley", "jordan"),
    ("frank_may", "frank_may"),
    ("david", "hugh"),
]

odd_holiday_shares = [
    [
        "frank_may",
        "jim",
        "hankey",
        "myers",
        "eddie",
        "jordan",
        "richard",
        "david",
        "frank_latimer",
        "becca",
    ],
    [
        "hankey",
        "lane",
        "frank_may",
        "joe",
        "eddie",
        "hayley",
        "richard",
        "hugh",
        "frank_latimer",
        "will",
    ],
]
even_holiday_shares = [
    [
        "richard",
        "lane",
        "frank_latimer",
        "joe",
        "frank_may",
        "hugh",
        "hankey",
        "hayley",
        "eddie",
        "will",
    ],
    [
        "richard",
        "jim",
        "frank_latimer",
        "becca",
        "frank_may",
        "david",
        "hankey",
        "jordan",
        "eddie",
        "myers",
    ],
]

class AllocatedWeek:
    def __init__(self, start, kind, end=None, holiday=None, share=None):
        # datetime.date this starts
        self.start = start
        # datetime.date this ends
        self.end = end
        # this could be "hot", "warm", "cool", "cold"
        self.kind = kind
        # name of the holiday, None if not a holiday
        self.holiday = holiday
        # name of the person this belongs to
        self.share = share

    def __repr__(self):
        return f"AllocatedWeek(start={self.start}, end={self.end}, share={self.share}, kind={self.kind}, holiday={self.holiday})"


def rotate_list(lst, n):
    """Rotate a list by n positions to the right (positive n) or left (negative n)

    >>> test_list = list(range(20))  # [0, 1, 2, ..., 19]
    >>> rotate_list(test_list, 9)
    [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 0, 1, 2, 3, 4, 5, 6, 7, 8]
    >>> rotate_list(test_list, 11)
    [11, 12, 13, 14, 15, 16, 17, 18, 19, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    """
    if not lst:
        return lst
    n = n % len(lst)  # Handle cases where n > len(lst)
    return lst[n:] + lst[:n]


def opposite_kind(kind):
    if kind == "cool":
        return "warm"
    if kind == "warm":
        return "cool"
    if kind == "hot":
        return "cold"
    if kind == "cold":
        return "hot"
    raise Exception(f"Unknown kind: {kind}")


def wrap_around(weeks, index):
    return index % len(weeks)


def uniq_list(lst):
    """Returns a new list with duplicate elements removed while preserving order"""
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]


class HouseYear:
    def __init__(self, year, debug=False):
        self.year = year
        self.debug = debug
        self.rotated_shares = self.get_holiday_shares()
        if self.debug:
            print(f"rotated_shares: {self.rotated_shares}")
        self.weeks = []

    def get_holiday_shares(self):
        year_offset = self.year_offset()
        if self.debug:
            print(f"year_offset: {year_offset}")
        if self.year % 2 == 0:
            return rotate_list(even_holiday_shares[0], year_offset) + rotate_list(
                even_holiday_shares[1], year_offset
            )
        else:
            return rotate_list(odd_holiday_shares[0], year_offset) + rotate_list(
                odd_holiday_shares[1], year_offset
            )
            # return rotate_list(odd_holiday_shares[0] + odd_holiday_shares[1], year_offset)

    def year_offset(self):
        return (self.year - 2025) // 2

    def compute_schedule(self):
        self.weeks.append(AllocatedWeek(early_cold_weeks_start(self.year), "cold"))
        for i in range(0, 5):
            self.weeks.append(
                AllocatedWeek(
                    early_cool_weeks_start(self.year) + timedelta(weeks=i), "cool"
                )
            )
        for i in range(0, 5):
            self.weeks.append(
                AllocatedWeek(
                    early_warm_weeks_start(self.year) + timedelta(weeks=i), "warm"
                )
            )
        for i in range(0, hot_weeks_before_tate_annual_week_start(self.year)):
            self.weeks.append(
                AllocatedWeek(hot_weeks_start(self.year) + timedelta(weeks=i), "hot")
            )
        self.weeks.append(
            AllocatedWeek(
                tate_annual_week_start(self.year),
                "hot",
                holiday="Tate Annual",
                share="everyone",
            )
        )
        for i in range(0, 10 - hot_weeks_before_tate_annual_week_start(self.year)):
            self.weeks.append(
                AllocatedWeek(
                    tate_annual_week_start(self.year) + timedelta(weeks=i + 1), "hot"
                )
            )
        for i in range(0, 5):
            self.weeks.append(
                AllocatedWeek(
                    late_warm_weeks_start(self.year) + timedelta(weeks=i), "warm"
                )
            )
        for i in range(0, 5):
            self.weeks.append(
                AllocatedWeek(
                    late_cool_weeks_start(self.year) + timedelta(weeks=i), "cool"
                )
            )
        for i in range(0, 9):
            self.weeks.append(
                AllocatedWeek(
                    late_cold_weeks_start(self.year) + timedelta(weeks=i), "cold"
                )
            )

    def is_ten_percent_share(self, share):
        return share in ten_precent_shares

    def is_five_percent_share(self, share):
        return share in five_percent_shares

    def holiday_weeks(self):
        return {
            memorial_day_week_start(self.year): "Memorial Day",
            independence_day_week_start(self.year): "Independence Day",
            labor_day_week_start(self.year): "Labor Day",
            thanksgiving_week_start(self.year): "Thanksgiving",
            christmas_week_start(self.year): "Christmas",
        }

    def compute_holidays(self):
        for index, week in enumerate(self.weeks):
            if week.start == memorial_day_week_start(self.year):
                week.holiday = "Memorial Day"
                self.allocate_week(index, self.rotated_shares[5])

            if week.start == independence_day_week_start(self.year):
                week.holiday = "Independence Day"
                self.allocate_week(index, self.rotated_shares[10])

            if week.start == labor_day_week_start(self.year):
                week.holiday = "Labor Day"
                self.allocate_week(index, self.rotated_shares[6])

            if week.start == thanksgiving_week_start(self.year):
                week.holiday = "Thanksgiving"
                self.allocate_week(index, self.rotated_shares[11])

            if week.start == christmas_week_start(self.year):
                week.holiday = "Christmas"
                self.allocate_week(index, self.rotated_shares[12])

        # now that we have the holidays allocated, let's give the 10 percenters their other weeks
        for index, week in enumerate(self.weeks):
            if week.start in self.holiday_weeks().keys():
                if self.is_ten_percent_share(week.share):
                    self.allocate_weeks_ten_percent(index)

        # now the 5 percenters their other weeks
        if self.debug:
            print(f"compute_remaining_five_percent_shares")
        skip_index = 20
        for index, week in enumerate(self.weeks):
            if index < skip_index:
                continue
            if week.start in self.holiday_weeks().keys():
                if self.is_five_percent_share(week.share):
                    self.allocate_weeks_five_percent(index)

    def compute_initial_shares(self):
        if self.debug:
            print(f"compute_initial_shares")
        allocated_shares = set(
            [
                share
                for share in [week.share for week in self.weeks]
                if share is not None
            ]
        )
        # print(f"allocated_shares: {allocated_shares}")

        remaining_shares = uniq_list(
            [share for share in self.rotated_shares if share not in allocated_shares]
        )
        if self.debug:
            print(f"remaining_shares: {remaining_shares}")

        for share in remaining_shares:
            if self.debug:
                print(f"share: {share}")
            for index, week in enumerate(self.weeks):
                if index == 0:
                    continue
                if week.share is not None:
                    continue
                week.share = share
                if self.is_ten_percent_share(share):
                    self.allocate_weeks(index)
                break
        # for share in remaining_shares:
        #     weeks = allocate_weeks(weeks, share)
        # remove all the people that have weeks already allocated
        # for week in weeks:

    def compute_remaining_five_percent_shares(self):
        if self.debug:
            print(f"compute_remaining_five_percent_shares")

        share_counts = self.get_share_count()

        # Find all 5% shares that only have one week
        for share in five_percent_shares:
            if share not in share_counts:
                continue
            if len(share_counts[share]) == 1:
                # Find the week with this share
                for index, week in enumerate(self.weeks):
                    if week.share == share:
                        self.allocate_weeks_five_percent(index)
                        break

    def allocate_weeks(self, index):
        share = self.weeks[index].share
        if share in ten_precent_shares:
            self.allocate_weeks_ten_percent(index)
            return
        elif share in five_percent_shares:
            self.allocate_weeks_five_percent(index)
            return
        raise Exception(f"Unknown share: {share}")

    def allocate_weeks_five_percent(self, index):
        assert (
            self.weeks[index].share is not None
        ), f"attempt to allocate weeks for an unassigned week: {self.weeks[index]}"
        if self.debug:
            print(f"allocate_weeks_five_percent: {self.weeks[index]}")
        share = self.weeks[index].share
        # idx = index
        # current_kind = weeks[idx].kind
        # while True:
        #     if weeks[idx-1].kind != current_kind:
        #         break
        #     idx = idx - 1

        looking_for = opposite_kind(self.weeks[index].kind)
        idx = wrap_around(self.weeks, index + 10)
        counter = 0
        while True:
            if self.debug:
                print(
                    f"share: {share}, looking_for: {looking_for}, idx: {idx}, kind: {self.weeks[idx].kind}"
                )
            if self.weeks[idx].kind == looking_for and self.weeks[idx].share is None:
                if self.debug:
                    print(f"found it {idx}")
                self.weeks[idx].share = share
                if self.debug:
                    print(f"weeks[{idx}]: {self.weeks[idx]}")
                break
            counter += 1
            if counter > 41:
                if self.debug:
                    pprint.pprint(self.weeks)
                    self.print_share_count()
                    print(f"couldn't find a week for {share}")
                # break
                raise Exception(f"counter: {counter}")
            idx = wrap_around(self.weeks, idx + 1)

    def allocate_week(self, index, share):
        self.assert_everyone_has_the_right_number_of_weeks_or_less()
        if self.debug:
            print(f"allocate_week: {self.weeks[index]}, {share}")
        assert self.weeks[index].share is None, f"weeks[{index}]: {self.weeks[index]}"
        self.weeks[index].share = share

    def skip_forward_ten_weeks(self, start_index):
        """Skip forward 10 weeks, not counting Tate annual week
        Returns the index after skipping"""
        next_index = start_index
        weeks_counted = 0
        weeks_actually_counted = 0
        while weeks_counted < 10:
            weeks_actually_counted += 1
            next_index = wrap_around(self.weeks, next_index + 1)
            if self.debug:
                print(f"next_index: {next_index} {self.weeks[next_index].holiday}")
            if self.weeks[next_index].holiday != "Tate Annual":
                weeks_counted += 1
            if self.debug:
                print(
                    f"weeks_counted: {weeks_counted} weeks_actually_counted: {weeks_actually_counted}"
                )
        return next_index

    def allocate_weeks_ten_percent(self, index):
        if self.debug:
            print(f"allocate_weeks_ten_percent: {self.weeks[index]}")
        share = self.weeks[index].share
        for i in range(0, 3):
            if self.debug:
                print(f"share: {share}, i: {i}")

            next_index = self.skip_forward_ten_weeks(index)

            if self.weeks[next_index].share is None:
                self.allocate_week(next_index, share)
            elif self.weeks[wrap_around(self.weeks, next_index + 1)].share is None:
                if self.debug:
                    print(f"nudged it forward a week")
                self.allocate_week(wrap_around(self.weeks, next_index + 1), share)
            elif self.weeks[next_index - 1].share is None:
                if self.debug:
                    print(f"nudged it back a week")
                self.allocate_week(next_index - 1, share)
            elif self.weeks[wrap_around(self.weeks, next_index + 2)].share is None:
                if self.debug:
                    print(f"nudged it forward two weeks")
                self.allocate_week(wrap_around(self.weeks, next_index + 2), share)
            elif self.weeks[next_index - 2].share is None:
                if self.debug:
                    print(f"nudged it back two weeks")
                self.allocate_week(next_index - 2, share)
            else:
                pprint.pprint(self.weeks)
                raise Exception(f"No share available for week {next_index} for {share}")
            index = next_index

    def get_share_count(self):
        share_counts = {}
        for week in self.weeks:
            if share_counts.get(week.share) is None:
                share_counts[week.share] = []

            share_counts[week.share].append(week.kind)
            share_counts[week.share].sort()
        return share_counts

    def assert_share_count(self):
        share_counts = self.get_share_count()
        for share in share_counts:
            if self.is_ten_percent_share(share):
                assert len(share_counts[share]) == 4
                assert share_counts[share] == [
                    "cold",
                    "cool",
                    "hot",
                    "warm",
                ], f"{share}: {share_counts[share]}"
            if self.debug:
                print(f"{share}: {len(share_counts[share])}")

    def print_share_count(self):
        share_counts = self.get_share_count()
        pprint.pprint(share_counts)

    def print_kind_count(self):
        kind_counts = {}
        for week in self.weeks:
            kind_counts[week.kind] = kind_counts.get(week.kind, 0) + 1
        pprint.pprint(kind_counts)

    def assert_everyone_has_the_right_number_of_weeks_or_less(self):
        for share in ten_precent_shares:
            assert len([week for week in self.weeks if week.share == share]) <= 4
        for share in five_percent_shares:
            assert len([week for week in self.weeks if week.share == share]) <= 2

    def compute_all(self):
        self.compute_schedule()
        self.compute_holidays()
        self.compute_initial_shares()
        self.compute_remaining_five_percent_shares()


def generate_schedule(year, debug=False):
    """Generate a single year's schedule and return it"""
    house_year = HouseYear(year, debug=debug)
    house_year.compute_all()
    house_year.assert_share_count()
    return house_year

def generate_multi_year_schedule(start_year=2025, num_years=20):
    """Generate a list of schedules for multiple years"""
    schedules = []
    for year in range(start_year, start_year + num_years):
        try:
            schedule = generate_schedule(year)
            schedules.append(schedule)
        except Exception as e:
            print(f"Error in year {year}: {e}")
            raise e
    return schedules

def test_schedule(schedules):
    """Test a multi-year schedule for validity"""
    holiday_counts = {}
    kind_counts = {}
    total_holidays = 0
    previous_year_kinds = {}
    spacing_counts = {}
    week_index_counts = {}

    for house_year in schedules:
        year = house_year.year
        
        # Track week index distribution
        for index, week in enumerate(house_year.weeks):
            if week.share and week.share != "everyone":
                if week.share not in week_index_counts:
                    week_index_counts[week.share] = {}
                week_index_counts[week.share][index] = week_index_counts[week.share].get(index, 0) + 1


        # Track kinds for 5% shares
        current_year_kinds = {share: set() for share in five_percent_shares}

        # Count holidays and kinds
        for week in house_year.weeks:
            if week.share:
                if week.share not in kind_counts:
                    kind_counts[week.share] = {"hot": 0, "warm": 0, "cool": 0, "cold": 0}
                kind_counts[week.share][week.kind] += 1

                if week.share in five_percent_shares:
                    current_year_kinds[week.share].add(week.kind)

            if week.holiday and week.holiday != "Tate Annual":
                total_holidays += 1
                if week.share not in holiday_counts:
                    holiday_counts[week.share] = {}
                if week.holiday not in holiday_counts[week.share]:
                    holiday_counts[week.share][week.holiday] = 0
                holiday_counts[week.share][week.holiday] += 1

        # Check alternating pattern for 5% shares
        if previous_year_kinds:
            for share in five_percent_shares:
                if share in previous_year_kinds:
                    prev_kinds = previous_year_kinds[share]
                    curr_kinds = current_year_kinds[share]

                    if {"hot", "cold"}.issubset(prev_kinds):
                        assert {"warm", "cool"}.issubset(curr_kinds), \
                            f"Share {share} in year {year} has {curr_kinds} after having hot/cold in previous year"

                    if {"warm", "cool"}.issubset(prev_kinds):
                        assert {"hot", "cold"}.issubset(curr_kinds), \
                            f"Share {share} in year {year} has {curr_kinds} after having warm/cool in previous year"

        # Verify spacing for 10% shares
        for share in ten_precent_shares:
            share_weeks = [
                i for i, week in enumerate(house_year.weeks)
                if week.share == share and week.holiday != "Tate Annual"
            ]

            for i in range(len(share_weeks) - 1):  # Only check consecutive weeks within the year
                spacing = share_weeks[i + 1] - share_weeks[i]
                spacing_counts[spacing] = spacing_counts.get(spacing, 0) + 1
                
                assert spacing >= 8, (
                    f"Year {year}: Share {share} has weeks too close together. "
                    f"Weeks at indices {share_weeks[i]} and {share_weeks[i + 1]} "
                    f"are only {spacing} weeks apart"
                )
        previous_year_kinds = current_year_kinds

    return {
        'holiday_counts': holiday_counts,
        'kind_counts': kind_counts,
        'total_holidays': total_holidays,
        'spacing_counts': spacing_counts,
        'week_index_counts': week_index_counts
    }

def test_schedule_results(schedule):
    """Main function to generate and test schedules"""
    results = test_schedule(schedule)
    num_years = len(schedule)
    print(f"\nDistribution over {num_years} years (Total holidays: {results['total_holidays']}):")
    
    # Print holiday distribution
    print("\nHoliday Distribution:")
    print("-" * 60)
    for share, holidays in results['holiday_counts'].items():
        if share:  # Skip None/empty shares
            print(f"{share}:")
            for holiday, count in holidays.items():
                emoji = holiday_to_emoji(holiday)
                print(f"  {emoji} {holiday}: {count}")
    
    # Print season distribution
    print("\nSeason Distribution:")
    print("-" * 60)
    for share, kinds in results['kind_counts'].items():
        if share and share != "everyone":  # Skip None/empty/everyone shares
            print(f"{share}:")
            for kind, count in kinds.items():
                print(f"  {kind}: {count}")
    
    # Print spacing statistics for 10% shares
    print("\nWeek Spacing Distribution (10% shares):")
    print("-" * 60)
    for spacing, count in sorted(results['spacing_counts'].items()):
        print(f"Spacing of {spacing} weeks: {count} occurrences")
    
    # Print week index distribution with unallocated weeks
    print("\nWeek Index Distribution:")
    print("-" * 60)
    total_weeks = len(schedule[0].weeks)  # Get number of weeks from first year
    
    for share, indices in results['week_index_counts'].items():
        if share and share != "everyone":  # Skip None/empty/everyone shares
            print(f"\n{share}:")
            for index in range(total_weeks):  # Iterate through all possible week indices
                count = indices.get(index, 0)
                status = "unallocated" if count == 0 else f"{count} times"
                print(f"  Week {index}: {status}")

    # After the existing week index distribution section, add:
    print("\nWeek Index Anomalies:")
    print("-" * 60)
    total_anomalies = 0
    total_weeks = len(schedule[0].weeks)  # Get number of weeks from first year
    
    for share, indices in results['week_index_counts'].items():
        if share and share != "everyone":
            expected_count = 2 if share in ten_precent_shares else 1
            # Count anomalies for all possible week indices
            anomalies = 0
            for week_index in range(total_weeks):
                count = indices.get(week_index, 0)  # Use 0 if index not found
                if count != expected_count:
                    if anomalies == 0:  # Print header only when first anomaly found
                        print(f"{share} (expected {expected_count}/week):")
                    print(f"  Week {week_index}: got {count} instead of {expected_count}")
                    anomalies += 1
            total_anomalies += anomalies
    
    print(f"\nTotal anomalies found: {total_anomalies}")


def show_year_offsets(num_years=20):
    print("\nYear Offsets:")
    print("Year\tOffset")
    print("-" * 16)
    for year in range(2025, 2025 + num_years):
        house_year = HouseYear(year)
        offset = house_year.year_offset()
        print(f"{year}\t{offset}")


if __name__ == "__main__":
    import doctest

    doctest.testmod()
    house_year_2025 = HouseYear(2025)
    print(house_year_2025.rotated_shares)
    house_year_2026 = HouseYear(2026)
    print(house_year_2026.rotated_shares)

    # house_year.compute_all()
    # house_year.compute_remaining_five_percent_shares()
    # house_year.print_share_count()
    # # house_year.print_kind_count()
    # for week in house_year.weeks:
    #     print(f"{week.start}: {week.kind} {week.holiday} {week.share}")

    # house_year = HouseYear(2027, debug=True)
    # house_year.compute_all()
    # house_year.compute_schedule()
    # house_year.compute_holidays()
    # house_year.compute_initial_shares()
    # for week in house_year.weeks:
    #     print(f"{week.start}: {week.kind} {week.holiday} {week.share}")
    # house_year.assert_share_count()
    # house_year.print_share_count()
    # house_year.print_kind_count()

    # house_year = HouseYear(2026, debug=True)
    # house_year.compute_all()

    schedule = generate_multi_year_schedule(num_years=20)

    test_schedule_results(schedule)
