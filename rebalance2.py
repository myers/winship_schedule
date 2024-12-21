#!/usr/bin/env python3

def count_weeks_by_share_global(schedule):
    """
    Count how many times each share has each week index over the entire schedule.
    Returns {share: {week_index: count}}
    """
    share_counts = {}
    for year in schedule:
        for w_idx, aw in enumerate(year.weeks):
            if aw.share is not None:
                share = aw.share
                if share not in share_counts:
                    share_counts[share] = {}
                if w_idx not in share_counts[share]:
                    share_counts[share][w_idx] = 0
                share_counts[share][w_idx] += 1
    return share_counts

def check_10_percent_spacing_in_year(year, owner_percent):
    """
    Check that for all 10% shares in this year, no two allocated weeks are less than 8 weeks apart.
    Return True if spacing is valid, False if not.
    """
    share_positions = {}
    for w_idx, aw in enumerate(year.weeks):
        if aw.share is not None:
            s = aw.share
            if s not in share_positions:
                share_positions[s] = []
            share_positions[s].append(w_idx)
    
    for s, positions in share_positions.items():
        if owner_percent.get(s, 0) == 10:
            positions.sort()
            for i in range(len(positions)-1):
                if positions[i+1] - positions[i] < 8:
                    return False
    return True

def allowed_week_difference(s1, s2, owner_percent):
    # If either share is 10%, max diff = 1, else 10
    if owner_percent[s1] == 10 or owner_percent[s2] == 10:
        return 1
    return 10

def compute_ideal_allocation(owner_percent):
    ideal_allocation = {}
    # For the entire 20-year horizon:
    # - 10% owners: ideally 2 occurrences per week index total over 20 years
    # - 5% owners: ideally 1 occurrence per week index total over 20 years
    for share, pct in owner_percent.items():
        if pct == 10:
            target = 2
        elif pct == 5:
            target = 1
        else:
            raise ValueError("Unexpected owner percentage.")
        ideal_allocation[share] = {w: target for w in range(40)}
    return ideal_allocation

def find_global_imbalance(surplus_deficit):
    """
    Given surplus_deficit {share: {week_index: diff}}, find a list of (share, week_index, diff) 
    sorted by the magnitude of imbalance.
    """
    imbalances = []
    for s, sd in surplus_deficit.items():
        for w, d in sd.items():
            if d != 0:
                imbalances.append((s, w, d))
    # sort by absolute imbalance, descending
    imbalances.sort(key=lambda x: abs(x[2]), reverse=True)
    return imbalances

def attempt_swap_for_global_imbalance(schedule, owner_percent, surplus_deficit, s, w_idx, diff, ideal_allocation):
    """
    Attempt to reduce global imbalance for share s at week index w_idx.
    If diff > 0, share s has surplus of w_idx; try to swap out one occurrence of w_idx 
    for a needed week index where s has deficit.
    If diff < 0, share s has deficit of w_idx; try to swap in one occurrence of w_idx 
    from another share, giving them something s has in surplus.

    We'll try a simple approach:
    - If diff > 0 (surplus), find a week index w_need where s has deficit, and try to swap a week w_idx (owned by s) 
      with a week w_need (owned by another share) in the same year.
    - If diff < 0 (deficit), similarly try the reverse: we want to bring in a w_idx from another share and give them 
      something s has in surplus.

    Return True if a swap was made, False otherwise.
    """
    # Identify a complementary week index from s to fix the imbalance:
    # If s is surplus in w_idx, find a w_need where s is deficit
    # If s is deficit in w_idx, find a w_have where s is surplus
    s_deficit = [(w, -d) for w, d in surplus_deficit[s].items() if d < 0]
    s_surplus = [(w, d) for w, d in surplus_deficit[s].items() if d > 0]

    improved = False

    if diff > 0:
        # s has surplus at w_idx, try to find a w_need from s_deficit
        if not s_deficit:
            return False
        # Sort deficits by largest deficit
        s_deficit.sort(key=lambda x: x[1], reverse=True)
        for (w_need, needed_amount) in s_deficit:
            if needed_amount <= 0:
                continue
            # Try to swap one instance of w_idx (s owns) with one instance of w_need (other share owns)
            if try_swap(schedule, s, w_idx, w_need, owner_percent):
                improved = True
                break
    else:
        # diff < 0, s has deficit at w_idx, try to find a w_have from s_surplus
        s_surplus.sort(key=lambda x: x[1], reverse=True)
        for (w_have, have_amount) in s_surplus:
            if have_amount <= 0:
                continue
            # Try to swap one instance of w_have (s owns) with one instance of w_idx (other share owns)
            if try_swap(schedule, s, w_have, w_idx, owner_percent):
                improved = True
                break

    return improved


def rebalance_global(schedule, owner_percent):
    ideal_allocation = compute_ideal_allocation(owner_percent)
    max_passes = 5000
    improved = True
    pass_count = 0

    # Keep track of recent swaps (using a set of tuples)
    recent_swaps = set()

    while improved and pass_count < max_passes:
        pass_count += 1
        improved = False

        # Compute global surplus/deficit
        current_counts = count_weeks_by_share_global(schedule)
        surplus_deficit = {}
        for share in ideal_allocation:
            surplus_deficit[share] = {}
            for w_idx in range(40):
                current = current_counts.get(share, {}).get(w_idx, 0)
                ideal = ideal_allocation[share][w_idx]
                surplus_deficit[share][w_idx] = current - ideal

        imbalances = find_global_imbalance(surplus_deficit)
        if not imbalances:
            # Perfect distribution globally
            break

        for (s, w_idx, diff) in imbalances:
            if diff == 0:
                continue

            # Attempt to fix this imbalance
            # Modify attempt_swap_for_global_imbalance to take recent_swaps as a parameter
            if attempt_swap_for_global_imbalance(schedule, owner_percent, surplus_deficit, s, w_idx, diff, ideal_allocation, recent_swaps):
                improved = True
                # Break to re-check surpluses after a single improvement
                break

    return schedule

def attempt_swap_for_global_imbalance(schedule, owner_percent, surplus_deficit, s, w_idx, diff, ideal_allocation, recent_swaps):
    s_deficit = [(w, -d) for w, d in surplus_deficit[s].items() if d < 0]
    s_surplus = [(w, d) for w, d in surplus_deficit[s].items() if d > 0]

    if diff > 0:
        # Surplus at w_idx, need a deficit
        s_deficit.sort(key=lambda x: x[1], reverse=True)
        for (w_need, needed_amount) in s_deficit:
            if needed_amount <= 0:
                continue
            if try_swap(schedule, s, w_idx, w_need, owner_percent, recent_swaps):
                return True
    else:
        # Deficit at w_idx, need a surplus
        s_surplus.sort(key=lambda x: x[1], reverse=True)
        for (w_have, have_amount) in s_surplus:
            if have_amount <= 0:
                continue
            if try_swap(schedule, s, w_have, w_idx, owner_percent, recent_swaps):
                return True

    return False

def try_swap(schedule, s, w_give, w_get, owner_percent, recent_swaps):
    for y_idx, year in enumerate(schedule):
        if w_give < len(year.weeks) and w_get < len(year.weeks):
            caw = year.weeks[w_give]
            aw2 = year.weeks[w_get]
            if (caw.share == s and caw.holiday is None and
                aw2.share != s and aw2.holiday is None and
                aw2.kind == caw.kind):

                # Compute circular difference
                raw_diff = abs(w_give - w_get)
                circular_diff = min(raw_diff, 40 - raw_diff)

                diff_limit = allowed_week_difference(s, aw2.share, owner_percent)
                if circular_diff <= diff_limit:
                    # Check if we recently did this swap (or its inverse)
                    swap_key = (y_idx, w_give, w_get, caw.share, aw2.share)
                    inverse_swap_key = (y_idx, w_get, w_give, aw2.share, caw.share)
                    if swap_key in recent_swaps or inverse_swap_key in recent_swaps:
                        # Already tried this swap recently
                        continue

                    # Only swap the share attributes
                    original_share_give = year.weeks[w_give].share
                    original_share_get = year.weeks[w_get].share

                    # Perform the share swap
                    year.weeks[w_give].share = aw2.share
                    year.weeks[w_get].share = s

                    # Check spacing for 10% shares
                    if check_10_percent_spacing_in_year(year, owner_percent):
                        print(f"Swapping shares in year {y_idx}:\n"
                              f"  Week {w_give}: {caw} now owned by {aw2.share}\n"
                              f"  Week {w_get}: {aw2} now owned by {s}\n")

                        # Record this swap so we don't undo it immediately
                        recent_swaps.add(swap_key)
                        return True
                    else:
                        # Revert if spacing check fails
                        year.weeks[w_give].share = original_share_give
                        year.weeks[w_get].share = original_share_get
    return False

# Example usage:
# schedule: list of HouseYear instances (20 years)
# owner_percent: dictionary of share -> percentage (5 or 10)
# new_schedule = rebalance_global(schedule, owner_percent)

owner_percent = {
    # 10% owners
    "frank_may": 10,
    "hankey": 10,
    "eddie": 10,
    "richard": 10,
    "frank_latimer": 10,
    
    # 5% owners
    "joe": 5,
    "lane": 5,
    "hayley": 5,
    "david": 5,
    "jim": 5,
    "myers": 5,
    "jordan": 5,
    "becca": 5,
    "hugh": 5,
    "will": 5
}

if __name__ == "__main__":
    import take2
    import pprint

    schedule = []

    for year in range(2025, 2045):
        house_year = take2.HouseYear(year, debug=False)
        house_year.compute_all()
        schedule.append(house_year)
    assert len(schedule) == 20
    # pprint.pprint(schedule[0].weeks)
    # pprint.pprint(count_weeks_by_share(schedule))


    new_schedule = rebalance_global(schedule, owner_percent)

    # pprint.pprint(count_weeks_by_share(new_schedule))

    #pprint.pprint(new_schedule[0].weeks)
    take2.test_schedule_results(new_schedule)

    pprint.pprint(new_schedule[0].weeks)
    import export_to_excel
    export_to_excel.export_to_excel("winship_schedule_2025_2045_balanced2.xlsx", new_schedule)
