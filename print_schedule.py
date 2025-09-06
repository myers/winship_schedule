#!/usr/bin/env python3

import sys

import winship_schedule


def print_year_schedule(year):
    print(year)
    print()
    house_year = winship_schedule.HouseYear(year)
    for chunk in house_year.chunks():
        print(chunk.name)
        for week in chunk.weeks:
            name = winship_schedule.share_name_to_name(week.share)
            holiday = ""
            if week.holiday:
                holiday = f" ({week.holiday})"
            print(f"\t{week.start.strftime('%A, %x')} - {name}{holiday}")
        print()
    print("-" * 80)


def print_holiday(year):
    house_year = winship_schedule.HouseYear(year)
    for chunk in house_year.chunks():
        for week in chunk.weeks:
            name = winship_schedule.share_name_to_name(week.share)
            holiday = ""
            if week.holiday:
                holiday = " *"
            if week.start != winship_schedule.christmas_week_start(year):
                continue
            print(
                "{} - {} - {}{}".format(year, week.start.strftime("%x"), name, holiday)
            )


if __name__ == "__main__":
    import doctest

    ret = doctest.testmod()
    if ret.failed > 0:
        sys.exit(1)

    for year in range(2026, 2027):
        print_year_schedule(year)
