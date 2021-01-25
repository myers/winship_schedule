# winship_schedule


# Goals

The Winship House only has 40 weeks of the year that we schedule for.  A 5% share ownership should get you 2 weeks of time at the house.

We want to give everyone equal access to different parts of the year.  For those who have 4 weeks (10% owners) we can split their time over the four parts of the year. We also need to give those 5% equal time so they should have a week in the summer and a week in the coldest part of the year for one year, and the next year two weeks in the warm part of the year.

We also want to evenly split the Holidays:

 - Memorial Day (3 day weekend)
 - Independence Day
 - Labor Day (3 day weekend)
 - Thanksgiving
 - Christmas

We also want the week and weekend of the Tate Annual Meeting to be open to all.

We want to have a schedule that we can work with at least five years out.   Those with kids have to plan their summers far out in advance.
# How I solved this

I wanted to do this on a computer, because if we can get a computer to create this schedule it's easy to generate a list for as many years as we care to.
We define our seasons and when they happen (Cool Weeks, Warm Weeks, Hot Weeks, and Cold Weeks).  Everything is based around when Tate Annual Weekend happens:

 - Early Cool Weeks - starts 5 weeks before starts of Early Warm weeks
 - Early Warm Weeks - starts 5 weeks before start of hot weeks
 - Hot Weeks - starts 8 weeks before the Tate Annual Weekend, and 2 weeks after
 - Late Warm Weeks - starts after Hot Weeks
 - Late Cool Weeks - starts Late Warm weeks
 - Cold Weeks - the 10 weeks after Late Cool weeks

I chose to split the weeks up like this so that no one ended up with an early Spring week and a Late Fall week, both of which would be really cold.  Since some owners only have 5% it's important they get a usable week.

There is a starting list of who should get what week on odd and even years.  These lists are made with care so that everyone is evenly split over the different seasons.  Since everyone must have at least 5% we needed two lists, one for even years, one for odd years.  I made sure that those 5%ers were on Warm and Cool weeks one year, and Hot and Cold weeks the next.  I initially randomized the list and then made a few alterations as people asked (I only remember doing this for Frank May).  Since 2021 will be the first odd year we can shift things around for that year in the program.

After the first even and odd years, the lists are rotated down by one, making a whole new schedule.

BUT Holiday weekends shift around, we want to be sure we hand these out evenly.  Memorial Day always happens in the early warm weeks, Independence Day the hot weeks, Labor Day the late warm weeks, Thanksgiving the late cool weeks, and Christmas the cold weeks.  In light of that I made it so the first person on the list that season got the first holiday week for that season, second on the list got the second holiday week.

https://developers.google.com/calendar/quickstart/python