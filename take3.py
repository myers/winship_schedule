#!/usr/bin/env python3
 
from datetime import date, timedelta

# Provided helper functions
def memorial_day_week_start(year):
    ret = memorial_day(year) - timedelta(days=8)
    assert_sunday(ret)
    return ret

def memorial_day(year):
    # last Monday of May
    ret = date(year, 5, 31)
    while ret.weekday() != 0:  # Monday
        ret = ret - timedelta(days=1)
    return ret

def labor_day_week_start(year):
    ret = labor_day(year) - timedelta(days=8)
    assert_sunday(ret)
    return ret

def labor_day(year):
    # first Monday of September
    ret = date(year, 9, 1)
    while ret.weekday() != 0:  # Monday
        ret = ret + timedelta(days=1)
    return ret

def independence_day(year):
    return date(year, 7, 4)

def independence_day_week_start(year):
    ind = independence_day(year)
    # week start on Sunday before independence day
    # We choose Sunday so that the week includes July 4.
    # Adjust so that we always land on a Sunday (weekday=6)
    offset = (ind.weekday() + 1)
    return ind - timedelta(days=offset)

def thanksgiving_week_start(year):
    ret = thanksgiving(year) - timedelta(days=4)
    assert_sunday(ret)
    return ret

def thanksgiving(year):
    # fourth Thursday in November.
    ret = date(year, 11, 1)
    while ret.weekday() != 3: # Thursday
        ret = ret + timedelta(days=1)
    # ret is first Thursday in November, add 21 days for the 4th Thursday
    return ret + timedelta(days=21)

def christmas_week_start(year):
    xmas = christmas(year)
    offset = (xmas.weekday() + 1)
    return xmas - timedelta(days=offset)

def christmas(year):
    return date(year, 12, 25)

def tate_annual_meeting(year):
    # first Saturday in August
    ret = date(year, 8, 1)
    while ret.weekday() != 5:
        ret = ret + timedelta(days=1)
    return ret

def tate_annual_week_start(year):
    return tate_annual_meeting(year) - timedelta(days=6)

def hot_weeks_before_tate_annual_week_start(year):
    # Special rule: in 2021, 9 hot weeks before. Otherwise 8.
    if year == 2021:
        return 9
    return 8

def hot_weeks_start(year):
    return tate_annual_week_start(year) - timedelta(days=7 * hot_weeks_before_tate_annual_week_start(year))

def early_warm_weeks_start(year):
    return hot_weeks_start(year) - timedelta(days=7 * 5)

def assert_sunday(dd):
    assert dd.weekday() == 6, dd.strftime("%a %x")

def early_cool_weeks_start(year):
    ret = early_warm_weeks_start(year) - timedelta(days=7*5)
    assert_sunday(ret)
    return ret

def early_cold_weeks_start(year):
    ret = early_cool_weeks_start(year) - timedelta(days=7)
    assert_sunday(ret)
    return ret

def late_warm_weeks_start(year):
    return tate_annual_week_start(year) + timedelta(days=7 * (10 - hot_weeks_before_tate_annual_week_start(year) + 1))

def late_cool_weeks_start(year):
    return late_warm_weeks_start(year) + timedelta(days=7 * 5)

def late_cold_weeks_start(year):
    return late_cool_weeks_start(year) + timedelta(days=7 * 5)

def cleanup_weekend_start(year):
    return early_cool_weeks_start(year) - timedelta(days=2+7)

def sunday_after(dd):
    while True:
        dd += timedelta(days=1)
        if dd.weekday() == 6:
            return dd

##############################################
# Owners and Shares
##############################################

owners = {
    "Richard K": 10,
    "Frank M": 10,
    "Hankey": 10,
    "Eddie L": 10,
    "Frank L": 10,
    "Joe K": 5,
    "Jim K": 5,
    "Will C": 5,
    "Becca C": 5,
    "Hayley": 5,
    "Jordan": 5,
    "David": 5,
    "Hugh & Ann Laurel": 5,
    "Lane C": 5
}

# Each 10% owner gets 4 weeks per year (since 10% of 40 weeks = 4 weeks).
# Each 5% owner gets 2 weeks per year.

# Confirm total weeks used: 5 owners *4 weeks =20 weeks, 
# 9 owners *2 weeks =18 weeks, total =38 weeks.
# That leaves 2 weeks unassigned or flexible.

##############################################
# Seasonal Partitioning of Weeks (Conceptual)
##############################################
# We have 40 weeks total. One approach:
# Divide the 40 weeks roughly into segments:
# - Early Cold
# - Early Cool
# - Early Warm
# - Hot
# - Late Warm
# - Late Cool
# - Late Cold
# We can try to distribute each owner's weeks among these categories.

# To simplify, let's define the year schedule from early_cold_weeks_start to just after Christmas.
# Then find 40 Sundays starting from early_cold_weeks_start as the 40 weeks.

def generate_weeks(year):
    # Start from early_cold_weeks_start
    start = early_cold_weeks_start(year)
    weeks = []
    current = start
    # We'll gather 40 weeks
    for i in range(40):
        weeks.append(current)
        current += timedelta(days=7)
    return weeks

##############################################
# Identify Special Weeks
##############################################
# We want to identify which week includes Memorial Day, Independence Day, Labor Day,
# Thanksgiving, Christmas, and the Tate Annual Meeting week (which should remain open).

def find_week_for_day(weeks, special_day):
    # Given a list of week-start Sundays and a special day, find which week contains it.
    for w in weeks:
        if w <= special_day < w + timedelta(days=7):
            return w
    return None

def is_special_week(week_start, special_weeks):
    return week_start in special_weeks.values()

##############################################
# Assigning Weeks
##############################################

def assign_weeks(year, owners, previous_year_assignments):
    # Basic heuristic assignment:
    # 1. Identify special weeks and leave Tate week open.
    # 2. Assign holiday weeks evenly among owners year to year.
    # 3. Attempt to enforce spacing and seasonal distribution.

    weeks = generate_weeks(year)

    # Compute special weeks
    special_weeks = {}
    special_weeks['Memorial Day'] = find_week_for_day(weeks, memorial_day(year))
    special_weeks['Independence Day'] = find_week_for_day(weeks, independence_day(year))
    special_weeks['Labor Day'] = find_week_for_day(weeks, labor_day(year))
    special_weeks['Thanksgiving'] = find_week_for_day(weeks, thanksgiving(year))
    special_weeks['Christmas'] = find_week_for_day(weeks, christmas(year))
    tate_week = tate_annual_week_start(year)
    # The Tate Annual Meeting week should remain open to all
    # So we mark it as special and assign no one to it.
    special_weeks['Tate'] = tate_week

    # Determine how many weeks each owner needs this year
    allocation = {}
    for o, p in owners.items():
        if p == 10:
            allocation[o] = 4
        else:
            allocation[o] = 2

    assignments = {w: None for w in weeks}

    # Mark Tate week as open
    if tate_week in assignments:
        assignments[tate_week] = 'TATE ANNUAL MEETING (Open)'

    # We have 38 weeks to assign to owners out of the 40 (excluding Tate week and maybe one more flexible)
    # Let's first deal with holiday weeks. Distribute them to ensure fairness over years.
    # A simple approach: cycle through owners for each holiday, ensuring no owner gets too many holidays in a single year.
    holiday_owners = list(owners.keys())
    holiday_owners.sort()
    # For fairness, rotate who gets the holiday each year:
    # We can base rotation on year offset
    year_offset = year % len(holiday_owners)

    def assign_holiday(holiday_name):
        hw = special_weeks.get(holiday_name, None)
        if hw and hw in assignments and assignments[hw] is None:
            # pick an owner based on rotation
            chosen_owner = holiday_owners[(year_offset + hash(holiday_name)) % len(holiday_owners)]
            # If chosen owner has no weeks left to assign, pick next:
            idx = (year_offset + hash(holiday_name)) % len(holiday_owners)
            for _ in range(len(holiday_owners)):
                if allocation[holiday_owners[idx]] > 0:
                    chosen_owner = holiday_owners[idx]
                    break
                idx = (idx + 1) % len(holiday_owners)
            assignments[hw] = chosen_owner + " (Holiday: " + holiday_name + ")"
            allocation[chosen_owner] -= 1

    # Assign each holiday
    for h in ['Memorial Day', 'Independence Day', 'Labor Day', 'Thanksgiving', 'Christmas']:
        assign_holiday(h)

    # Now assign remaining weeks:
    # We want spacing of about 8 weeks between an owner's assigned weeks if possible.
    # We'll try a simple greedy approach:
    remaining_weeks = [w for w in weeks if assignments[w] is None]
    # Owners with weeks left:
    owners_left = [(o, allocation[o]) for o in allocation if allocation[o] > 0]

    # We'll attempt a seasonal rotation for 5% owners:
    # For simplicity, let's define four "seasons" to ensure distribution:
    # early cold/cool, early warm, hot, late warm, late cool/cold
    # This is simplified due to complexity.

    # Sort weeks by date
    remaining_weeks.sort()

    # Assign in a round-robin fashion to try to achieve some spacing
    # For better results, a constraint solver would be ideal.

    # Flatten owners_left
    owner_list = []
    for o, count in owners_left:
        owner_list.extend([o]*count)

    # Just do a naive assignment: one owner per available week in order
    # and rely on year-over-year rotation.
    # (This should be improved for actual fairness and spacing.)
    i = 0
    for w in remaining_weeks:
        if i < len(owner_list):
            assignments[w] = owner_list[i]
            i += 1
        else:
            # If any weeks remain unassigned, leave them open or mark them as spare
            assignments[w] = 'UNASSIGNED/SPARE'

    return assignments, special_weeks

##############################################
# Main Program
##############################################

if __name__ == "__main__":
    start_year = 2025
    end_year = start_year + 20

    previous_year_assignments = None
    for y in range(start_year, end_year):
        assignments, special_weeks = assign_weeks(y, owners, previous_year_assignments)
        previous_year_assignments = assignments

        print("Year:", y)
        print("Assignments (week start -> owner):")
        for w in sorted(assignments.keys()):
            owner = assignments[w]
            print(f"{w.isoformat()} -> {owner}")
        print("Special Weeks:", special_weeks)
        print("------------------------------------------------------------")