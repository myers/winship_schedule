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


holiday_shares = [
    "frank_may",
    "joe",
    "hankey",
    "lane",
    "eddie",
    "hayley",
    "richard",
    "david",
    "frank_latimer",
    "jim",
    "frank_may",
    "myers",
    "hankey",
    "jordan",
    "eddie",
    "becca",
    "richard",
    "hugh",
    "frank_latimer",
    "will",
]

def holiday_to_emoji(holiday):
    holiday_emojis = {
        "Memorial Day": "🎖️",
        "Independence Day": "🇺🇸",
        "Labor Day": "👷",
        "Thanksgiving": "🦃",
        "Christmas": "🎄",
        "Tate Annual": "🐻"
    }
    return holiday_emojis.get(holiday, "")

class AllocatedWeek:
    def __init__(self, start, kind, end=None, holiday=None, share=None):
        self.start = start
        self.end = end
        self.kind = kind
        self.holiday = holiday
        self.share = share

    def __repr__(self):
        return f"AllocatedWeek(start={self.start}, end={self.end}, share={self.share}, kind={self.kind}, holiday={self.holiday})"


# def alternating_shares_generator():
#     alternating_shares = []
#     five_percent_index = 0
#     ten_percent_index = 0

#     while True:
#       alternating_shares.append(ten_precent_shares[ten_percent_index])
#       ten_percent_index += 1
#       if ten_percent_index >= len(ten_precent_shares):
#           ten_percent_index = 0
#       alternating_shares.extend(five_percent_shares[five_percent_index:five_percent_index])
#       five_percent_index += 1
#       if five_percent_index >= len(five_percent_shares):
#           break

#     #assert ten_percent_index == len(ten_precent_shares)
#     #assert five_percent_index == len(five_percent_shares), f"five_percent_index: {five_percent_index}"
#     # # Add remaining entries if any
#     # if ten_percent_index < len(ten_precent_shares):
#     #     alternating_shares.extend(ten_precent_shares[ten_percent_index:])
#     # if five_percent_index < len(five_percent_shares):
#     #     alternating_shares.extend(five_percent_shares[five_percent_index:])
#     return alternating_shares

# alternating_shares = alternating_shares_generator()


def rotate_list(lst, n):
    """Rotate a list by n positions to the right (positive n) or left (negative n)

    >>> test_list = list(range(20))  # [0, 1, 2, ..., 19]
    >>> rotated = rotate_list(test_list, 11)
    >>> rotated[0]  # The 11th item (index 10) should now be first
    10
    >>> rotated == [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    True
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
        year_offset = self.year_offset()
        if self.debug:
            print(f"year_offset: {year_offset}")
        self.rotated_shares = rotate_list(holiday_shares, year_offset)
        if self.debug:
            print(f"rotated_shares: {self.rotated_shares}")
        self.weeks = []

    def year_offset(self):
        base_offset = self.year - 2025
        if self.year % 2 == 0:  # even years
            return 10 + base_offset
        else:  # odd years
            return base_offset

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
                self.allocate_week(index, self.rotated_shares[0])

            if week.start == independence_day_week_start(self.year):
                week.holiday = "Independence Day"
                self.allocate_week(index, self.rotated_shares[1])

            if week.start == labor_day_week_start(self.year):
                week.holiday = "Labor Day"
                self.allocate_week(index, self.rotated_shares[2])

            if week.start == thanksgiving_week_start(self.year):
                week.holiday = "Thanksgiving"
                self.allocate_week(index, self.rotated_shares[3])

            if week.start == christmas_week_start(self.year):
                week.holiday = "Christmas"
                self.allocate_week(index, self.rotated_shares[4])

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


def test_next_n_years(num_years=20):
    holiday_counts = {}
    kind_counts = {}
    total_holidays = 0
    previous_year_kinds = {}  # Track previous year's kinds for each 5% share
    
    for year in range(2025, 2025 + num_years):
        try:
            house_year = HouseYear(year, debug=False)
            house_year.compute_all()
            house_year.assert_share_count()
            
            # Track kinds for each 5% share this year
            current_year_kinds = {}
            for share in five_percent_shares:
                current_year_kinds[share] = set()
            
            # Count holidays and kinds for each share
            for week in house_year.weeks:
                # Count kinds
                if week.share:
                    if week.share not in kind_counts:
                        kind_counts[week.share] = {'hot': 0, 'warm': 0, 'cool': 0, 'cold': 0}
                    kind_counts[week.share][week.kind] += 1
                    
                    # Track kinds for 5% shares
                    if week.share in five_percent_shares:
                        current_year_kinds[week.share].add(week.kind)
                
                # Count holidays
                if week.holiday and week.holiday != "Tate Annual":
                    total_holidays += 1
                    if week.share not in holiday_counts:
                        holiday_counts[week.share] = {}
                    if week.holiday not in holiday_counts[week.share]:
                        holiday_counts[week.share][week.holiday] = 0
                    holiday_counts[week.share][week.holiday] += 1
            
            # Check alternating pattern for 5% shares
            if year > 2025:  # Skip first year as we need previous year to compare
                for share in five_percent_shares:
                    if share in previous_year_kinds:
                        prev_kinds = previous_year_kinds[share]
                        curr_kinds = current_year_kinds[share]
                        
                        # If last year was hot/cold, this year should be warm/cool
                        if {'hot', 'cold'}.issubset(prev_kinds):
                            assert {'warm', 'cool'}.issubset(curr_kinds), \
                                f"Share {share} in year {year} has {curr_kinds} after having hot/cold in previous year"
                        
                        # If last year was warm/cool, this year should be hot/cold
                        if {'warm', 'cool'}.issubset(prev_kinds):
                            assert {'hot', 'cold'}.issubset(curr_kinds), \
                                f"Share {share} in year {year} has {curr_kinds} after having warm/cool in previous year"
            
            # Store current year's kinds for next iteration
            previous_year_kinds = current_year_kinds
                    
        except Exception as e:
            print(f"Error in year {year}: {e}")
            raise e
    
    # Print the results
    print(f"\nDistribution over {num_years} years (Total holidays: {total_holidays}):")
    for share in sorted(holiday_counts.keys()):
        print(f"\n{share}:")
        print("  Holidays:")
        for holiday in sorted(holiday_counts[share].keys()):
            print(f"    {holiday}: {holiday_counts[share][holiday]}")
        print("  Week types:")
        for kind in ['hot', 'warm', 'cool', 'cold']:
            count = kind_counts[share][kind]
            print(f"    {kind}: {count}")


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

    test_next_n_years(20)
