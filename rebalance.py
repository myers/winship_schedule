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

def rebalance_schedule(schedule, owner_percent):
    """
    Rebalance the schedule so that each share gets closer to the ideal allocation:
    - 10% owners: ideally 2 of each week index (0-39) over 20 years
    - 5% owners: ideally 1 of each week index (0-39) over 20 years

    Constraints:
    - Do not consider holiday weeks for swapping.
    - Only swap weeks of the same kind.
    - Normally, weeks must not be swapped if they are more than 10 weeks apart.
    - If a week belongs to a 10% share, that week can only be swapped with another week that is at most 1 week apart in index.
    """
    # Determine the ideal distribution for each share
    ideal_allocation = {}
    for share, pct in owner_percent.items():
        if pct == 10:
            target = 2
        elif pct == 5:
            target = 1
        else:
            raise ValueError("Unexpected owner percentage, must be 5 or 10.")
        
        # Each share should have a target occurrences per week index
        ideal_allocation[share] = {week_idx: target for week_idx in range(40)}

    # Current counts
    current_counts = count_weeks_by_share(schedule)

    # Compute surplus/deficit for each share and week index
    surplus_deficit = {}
    for share in ideal_allocation:
        surplus_deficit[share] = {}
        for w_idx in range(40):
            current = current_counts.get(share, {}).get(w_idx, 0)
            ideal = ideal_allocation[share][w_idx]
            surplus_deficit[share][w_idx] = current - ideal

    # We'll do multiple passes attempting to improve distribution
    from collections import defaultdict
    kind_map = defaultdict(list)
    for y_idx, year in enumerate(schedule):
        for w_idx, aw in enumerate(year.weeks):
            if aw.holiday is None:
                kind_map[aw.kind].append((y_idx, w_idx, aw))

    improved = True
    passes = 0
    max_passes = 200

    while improved and passes < max_passes:
        improved = False
        passes += 1

        # Recalculate surplus/deficit
        current_counts = count_weeks_by_share(schedule)
        for share in surplus_deficit:
            for w in range(40):
                current = current_counts.get(share, {}).get(w, 0)
                ideal = ideal_allocation[share][w]
                surplus_deficit[share][w] = current - ideal

        # Create lists of needs and excess
        share_needs = {}
        share_excess = {}
        for share in surplus_deficit:
            share_needs[share] = [(w, -d) for w, d in surplus_deficit[share].items() if d < 0]
            share_excess[share] = [(w, d) for w, d in surplus_deficit[share].items() if d > 0]

        # Function to determine max allowed week difference based on owners
        def allowed_difference(share1, share2):
            # If either share is a 10% owner, max difference = 1
            if owner_percent[share1] == 10 or owner_percent[share2] == 10:
                return 1
            # Otherwise (both are 5%), max difference = 10
            return 10

        # Attempt swaps
        for share_ex in surplus_deficit:
            for (ex_widx, ex_amount) in share_excess[share_ex]:
                if ex_amount <= 0:
                    continue
                # Find candidate weeks that share_ex holds at ex_widx (holiday=None)
                candidate_weeks_to_give = []
                for y_idx, year in enumerate(schedule):
                    aw = year.weeks[ex_widx]
                    if aw.share == share_ex and aw.holiday is None:
                        candidate_weeks_to_give.append((y_idx, ex_widx, aw))

                for (cy, cwidx, caw) in candidate_weeks_to_give:
                    kind_key = caw.kind
                    found_swap = False
                    # Now find a share that needs a week near cwidx
                    for share_need in surplus_deficit:
                        if share_need == share_ex:
                            continue
                        # Try deficits for share_need
                        for (nd_widx, nd_amount) in share_needs[share_need]:
                            if nd_amount <= 0:
                                continue
                            # Check allowed difference
                            max_diff = allowed_difference(share_ex, share_need)
                            if abs(cwidx - nd_widx) <= max_diff:
                                # Find a suitable week from share_need at nd_widx
                                for y2, year2 in enumerate(schedule):
                                    aw2 = year2.weeks[nd_widx]
                                    if aw2.share == share_need and aw2.holiday is None and aw2.kind == kind_key:
                                        # Potential swap found
                                        # Perform the swap
                                        schedule[cy].weeks[cwidx], schedule[y2].weeks[nd_widx] = aw2, caw
                                        # Update shares
                                        schedule[cy].weeks[cwidx].share = share_need
                                        schedule[y2].weeks[nd_widx].share = share_ex

                                        improved = True
                                        found_swap = True
                                        break
                                if found_swap:
                                    break
                        if found_swap:
                            break
                    if found_swap:
                        break
    print(f"Passes: {passes}")
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

    for year in range(2025, 2046):
        house_year = take2.HouseYear(year, debug=False)
        house_year.compute_all()
        schedule.append(house_year)
    pprint.pprint(schedule[0].weeks)


    new_schedule = rebalance_schedule(schedule, owner_percent)

    #pprint.pprint(count_weeks_by_share(new_schedule))

    pprint.pprint(new_schedule[0].weeks)
    take2.test_schedule_results(new_schedule)
