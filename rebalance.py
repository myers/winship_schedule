#!/usr/bin/env python3


def count_weeks_by_share(schedule):
    """
    Given a list of HouseYear objects, each with a .weeks attribute (list of AllocatedWeek),
    count how many times each share has each week index.
    """
    share_counts = {}
    for y_idx, year in enumerate(schedule):
        for w_idx, aw in enumerate(year.weeks):
            if aw.share is not None:
                share = aw.share
                if share not in share_counts:
                    share_counts[share] = {}
                if w_idx not in share_counts[share]:
                    share_counts[share][w_idx] = 0
                share_counts[share][w_idx] += 1
    return share_counts

def check_10_percent_spacing(schedule, owner_percent, year_idx):
    """
    Check that for all 10% shares in the given year, no two allocated weeks are less than 8 weeks apart.
    Return True if spacing is valid, False if not.
    """
    year = schedule[year_idx]
    # Gather the weeks allocated to each share
    share_positions = {}
    for w_idx, aw in enumerate(year.weeks):
        if aw.share:
            s = aw.share
            if s not in share_positions:
                share_positions[s] = []
            share_positions[s].append(w_idx)
    
    # For each 10% share, check spacing
    for s, positions in share_positions.items():
        if owner_percent.get(s, 0) == 10:
            # Sort positions and check differences
            positions.sort()
            for i in range(len(positions)-1):
                if positions[i+1] - positions[i] < 8:
                    # Found two weeks less than 8 apart
                    return False
    return True

def rebalance_schedule(schedule, owner_percent):
    """
    Rebalance the schedule so that each share gets closer to the ideal allocation:
    - 10% owners: ideally 2 of each week index (0-39) over 20 years
    - 5% owners: ideally 1 of each week index (0-39) over 20 years

    Constraints:
    - Do not consider holiday weeks for swapping.
    - Only swap weeks of the same kind.
    - If either share is 10%, can only swap weeks that are ±1 week index apart,
      otherwise can swap weeks ±10 apart.
    - May not swap weeks between different years.
    - After a swap, if a 10% share ends up with two weeks less than 8 weeks apart in that year, the swap is not allowed.
    """

    # Add permanent set of swapped weeks at the start of the function
    permanently_swapped_weeks = set()

    # Determine the ideal distribution for each share
    ideal_allocation = {}
    for share, pct in owner_percent.items():
        if pct == 10:
            target = 2
        elif pct == 5:
            target = 1
        else:
            raise ValueError("Unexpected owner percentage, must be 5 or 10.")

        ideal_allocation[share] = {week_idx: target for week_idx in range(40)}

    def allowed_difference(s1, s2):
        # If either share is 10%, max diff = 1, else 10
        if owner_percent[s1] == 10 or owner_percent[s2] == 10:
            return 1
        return 10

    improved = True
    passes = 0
    max_passes = 100

    # Process years in reverse order
    for current_year_idx in range(len(schedule) - 1, -1, -1):
        improved = True
        passes = 0

        while improved and passes < max_passes:
            improved = False
            passes += 1

            # Calculate current surplus/deficit
            current_counts = count_weeks_by_share(schedule)
            surplus_deficit = {}
            for share in ideal_allocation:
                surplus_deficit[share] = {}
                for w_idx in range(40):
                    current = current_counts.get(share, {}).get(w_idx, 0)
                    ideal = ideal_allocation[share][w_idx]
                    surplus_deficit[share][w_idx] = current - ideal

            # Create lists of needs and excess, sorted by magnitude of imbalance
            share_needs = {}
            share_excess = {}
            for share in surplus_deficit:
                # Sort by deficit amount (largest deficit first)
                share_needs[share] = sorted(
                    [(w, -d) for w, d in surplus_deficit[share].items() if d < 0],
                    key=lambda x: x[1],
                    reverse=True
                )
                # Sort by excess amount (largest excess first)
                share_excess[share] = sorted(
                    [(w, d) for w, d in surplus_deficit[share].items() if d > 0],
                    key=lambda x: x[1],
                    reverse=True
                )

            # Track which weeks have been swapped in this pass
            swapped_weeks = set()

            # Sort shares by total imbalance to prioritize the most unbalanced shares
            share_total_imbalance = {
                share: sum(abs(d) for d in surplus_deficit[share].values())
                for share in surplus_deficit
            }
            sorted_shares = sorted(
                surplus_deficit.keys(),
                key=lambda s: share_total_imbalance[s],
                reverse=True
            )

            # Attempt swaps - but only within the current year
            for share_ex in sorted_shares:
                for (ex_widx, ex_amount) in share_excess[share_ex]:
                    if ex_amount <= 0:
                        continue
                    
                    # Only look at weeks in the current year
                    if ex_widx < len(schedule[current_year_idx].weeks):
                        aw = schedule[current_year_idx].weeks[ex_widx]
                        if (aw.share == share_ex and 
                            aw.holiday is None and 
                            (current_year_idx, ex_widx) not in permanently_swapped_weeks and 
                            (current_year_idx, ex_widx) not in swapped_weeks):
                            candidate_weeks_to_give = [(current_year_idx, ex_widx, aw)]
                        else:
                            candidate_weeks_to_give = []
                    else:
                        candidate_weeks_to_give = []

                    for (cy, cwidx, caw) in candidate_weeks_to_give:
                        kind_key = caw.kind
                        found_swap = False

                        for share_need in surplus_deficit:
                            if share_need == share_ex:
                                continue
                            for (nd_widx, nd_amount) in share_needs[share_need]:
                                if nd_amount <= 0:
                                    continue
                                # Only consider swaps within the current year
                                if (nd_widx >= len(schedule[current_year_idx].weeks) or
                                    (current_year_idx, nd_widx) in permanently_swapped_weeks or 
                                    (current_year_idx, nd_widx) in swapped_weeks):
                                    continue
                                    
                                diff_limit = allowed_difference(share_ex, share_need)
                                if abs(cwidx - nd_widx) <= diff_limit and nd_widx < len(schedule[cy].weeks):
                                    aw2 = schedule[cy].weeks[nd_widx]
                                    if (aw2.share == share_need and
                                        aw2.holiday is None and
                                        aw2.kind == kind_key):  # ensure same kind
                                        
                                        # Temporarily perform the swap in memory
                                        original_caw = schedule[cy].weeks[cwidx]
                                        original_aw2 = schedule[cy].weeks[nd_widx]
                                        
                                        schedule[cy].weeks[cwidx], schedule[cy].weeks[nd_widx] = aw2, caw
                                        schedule[cy].weeks[cwidx].share = share_need
                                        schedule[cy].weeks[nd_widx].share = share_ex

                                        # Check the spacing constraint for 10% shares
                                        if check_10_percent_spacing(schedule, owner_percent, cy):
                                            # If spacing is good, finalize the swap
                                            print(f"Swapping within year {cy}:\n  {caw}\n  {aw2}\n")
                                            improved = True
                                            found_swap = True
                                            # Add both weeks to both swap sets
                                            swapped_weeks.add((cy, cwidx))
                                            swapped_weeks.add((cy, nd_widx))
                                            permanently_swapped_weeks.add((cy, cwidx))
                                            permanently_swapped_weeks.add((cy, nd_widx))
                                        else:
                                            # Revert the swap if spacing failed
                                            schedule[cy].weeks[cwidx], schedule[cy].weeks[nd_widx] = original_caw, original_aw2

                                if found_swap:
                                    break
                            if found_swap:
                                break
                        if found_swap:
                            break

        print(f"Year {current_year_idx}: passes={passes}, improved={improved}")

    return schedule



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


    new_schedule = rebalance_schedule(schedule, owner_percent)

    # pprint.pprint(count_weeks_by_share(new_schedule))

    #pprint.pprint(new_schedule[0].weeks)
    take2.test_schedule_results(new_schedule)
