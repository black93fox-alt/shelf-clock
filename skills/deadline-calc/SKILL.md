---
name: deadline-calc
description: Use to compute every KDP deadline and window for the owner's books (pre-order cutoffs, Select terms and renewals, free-day and Countdown windows, price locks), for the daily scan, or when the owner asks what's coming up.
---
# Deadline calculator

**Calculator:** `calc/shelf_clock.py` in the template root.
- A copy ships as this skill's helper file, `shelf_clock.py`. Install it to `/workspace/shelf-clock/calc/shelf_clock.py` if it's not there.
- It uses Python 3 standard library only. Tests are in `tests/` in the template repo.

**Input:** `/workspace/shelf-clock/books.json`. The schema is in `examples/books.example.json`.
- Dates are KDP calendar dates.
- Free promos are given as `start` + `days`. KDP's end date is exclusive.
- KCDs take `start`, `days`, `start_price`, and `marketplace`.

## Run

```
python3 /workspace/shelf-clock/calc/shelf_clock.py deadlines /workspace/shelf-clock/books.json --horizon 120
python3 /workspace/shelf-clock/calc/shelf_clock.py deadlines /workspace/shelf-clock/books.json --today 2026-12-01 --json
```

## Reporting

- Show times in the owner's zone, set by `settings.timezone`.
- Show KDP's original zone beside them: PT for promos, UTC for pre-order cutoffs, UK time for .co.uk deals.
- For each item, give the date, the book, what happens, the rule ID, and the source.
- Show the working when asked, for example: "release Feb 23 00:00 UTC − 72 h = Feb 20 00:00 UTC = Feb 19 6:00 PM CST".

## Trust order

1. A date KDP shows on screen or in an email (Manage KDP Select dates, the pre-order timer)
2. A date the owner typed
3. A computed date

If a computed date disagrees with KDP's, use KDP's and update `books.json`. If a Select start is marked `unconfirmed`, put "(unconfirmed)" on every date that depends on it.

## Errors

If the script fails, say so and show the error. Never make up dates.
