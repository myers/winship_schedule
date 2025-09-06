# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses Poetry for dependency management:
- `poetry install` - Install dependencies
- `poetry run python <script>` - Run Python scripts
- `poetry run black .` - Format code with Black

## Code Architecture

This is a Python-based vacation house scheduling system for the Winship House that generates fair time allocations across multiple years. The system handles:

### Core Components

- **winship_schedule.py** - Main scheduling algorithm with season definitions and owner allocations
- **take2.py** - Current schedule generation implementation with 50-year planning
- **date_finders.py** - Holiday and season calculation utilities (Memorial Day, Labor Day, Thanksgiving, Christmas, Tate Annual Weekend)
- **export_to_excel.py** - Excel export with color-coded schedule visualization
- **rebalance.py** / **rebalance2.py** - Schedule optimization and validation tools

### Scheduling Logic

The system operates on seasonal divisions based around the Tate Annual Weekend (1st Saturday in August):
- **Hot Weeks** - 8 weeks before to 2 weeks after Tate Annual Weekend
- **Early/Late Warm Weeks** - 5 weeks before hot weeks and 5 weeks after Tate Annual Weekend
- **Early/Late Cool Weeks** - Shoulder seasons around warm weeks
- **Cold Weeks** - 10 weeks after late cool weeks

### Share Types

- **10% shares** - 4 weeks per year, distributed across all seasons with minimum 8-week spacing
- **5% shares** - 2 weeks per year, alternating patterns (hot+cold one year, warm+cool the next)

### Key Constraints

- 40 schedulable weeks per year
- Holiday weeks distributed fairly (Memorial Day, Independence Day, Labor Day, Thanksgiving, Christmas)
- Minimum 8-week spacing between allocated weeks for same owner
- Even/odd year rotation system for fair distribution
- Tate Annual Weekend kept open for all

## File Structure

- Main schedule generators: `winship_schedule.py`, `take2.py`, `take3.py`
- Validation and rebalancing: `rebalance.py`, `rebalance2.py`
- Export functionality: `export_to_excel.py`, `export_winship_schedule_to_google_calender.py`
- Google Calendar integration: `google_calender.py`
- Utility functions: `date_finders.py`, `print_schedule.py`
- Generated schedules: `*.xlsx` files