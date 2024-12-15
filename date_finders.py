from datetime import date, timedelta

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
    while ret.weekday() != 0:  # while it's not monday
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
    while ret.weekday() != 0:  # while it's not monday
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
    return ind - timedelta(days=ind.weekday() + 1)


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
    while ret.weekday() != 3:  # while it's not thursday
        ret = ret + timedelta(days=1)
    return ret + timedelta(days=21)


def christmas_week_start(year):
    """
    >>> christmas_week_start(2020)
    datetime.date(2020, 12, 20)
    """
    xmas = christmas(year)
    return xmas - timedelta(days=xmas.weekday() + 1)


def christmas(year):
    return date(year, 12, 25)


def tate_annual_meeting(year):
    """
    first Saturday in Aug (see `By-laws- current (2017).pdf`)
    >>> tate_annual_meeting(2021)
    datetime.date(2021, 8, 7)
    """
    ret = date(year=year, month=8, day=1)
    while ret.weekday() != 5:
        ret = ret + timedelta(days=1)
    return ret


def tate_annual_week_start(year):
    """
    >>> tate_annual_week_start(2021)
    datetime.date(2021, 8, 1)
    """
    return tate_annual_meeting(year) - timedelta(days=6)


def hot_weeks_start(year):
    return tate_annual_week_start(year) - timedelta(
        days=7 * hot_weeks_before_tate_annual_week_start(year)
    )


def early_warm_weeks_start(year):
    return hot_weeks_start(year) - timedelta(days=7 * 5)


def assert_sunday(date):
    assert date.weekday() == 6, date.strftime("%a %x")


def early_cool_weeks_start(year):
    ret = early_warm_weeks_start(year) - timedelta(days=7 * 5)
    assert_sunday(ret)
    return ret


def early_cold_weeks_start(year):
    ret = early_cool_weeks_start(year) - timedelta(days=7)
    assert_sunday(ret)
    return ret


def late_warm_weeks_start(year):
    return tate_annual_week_start(year) + timedelta(
        days=7 * (10 - hot_weeks_before_tate_annual_week_start(year) + 1)
    )


def late_cool_weeks_start(year):
    return late_warm_weeks_start(year) + timedelta(days=7 * 5)


def late_cold_weeks_start(year):
    return late_cool_weeks_start(year) + timedelta(days=7 * 5)


def cleanup_weekend_start(year):
    return early_cool_weeks_start(year) - timedelta(days=2 + 7)


def hot_weeks_before_tate_annual_week_start(year):
    # TODO: what's special about 2021?  Can I find other years like this?
    if year == 2021:
        return 9
    return 8


def sunday_after(dd):
    """
    >>> sunday_after(date(2021,4,25))
    datetime.date(2021, 5, 2)
    """
    while True:
        dd += timedelta(days=1)
        if dd.weekday() == 6:
            break
    return dd

