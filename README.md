# Shelf Clock

**A Grok Bot template that keeps your KDP clock.** Never lose a pre-order, free days, or a Countdown Deal to a missed date.

Shelf Clock tracks every Kindle book you publish and warns you before KDP deadlines pass:

- **Pre-orders:** the final-manuscript cutoff (72 hours before release, 5 days for your first KDP title), postponement limits, and what happens if you miss.
- **KDP Select:** 90-day terms, auto-renewal moments, and when to switch auto-renew off if you want out.
- **Free Book Promotions:** 5 days per term, day 2 earliest, one day's notice, and no carry-over.
- **Kindle Countdown Deals:** 30 days enrolled, $2.99–$24.99, at least $1 off, **price locked 30 days before and 14 days after**, 24-hour booking, and one per term. A term gets free days *or* a Countdown Deal, never both.
- **BookBub (optional):** eligibility only (50% off, best price in 30 days, 6 months per book, 30 days per author).

Ask "Can I drop Book 2 to $0.99 on Dec 5?" and you get **YES / NO / CHECK**, the KDP rule, the source link, and a better date if the answer is no.

**What it never does:** log into KDP, change prices, schedule promotions, upload, publish, submit to BookBub, or ask readers for reviews. You make every change in KDP yourself.

## How it works

1. Onboarding asks for your books, release dates, KDP Select term dates, prices, and any promotions this term.
2. It keeps a Book Ledger in a Google Sheet, or in a Page if you don't connect Drive.
3. **Every morning** it checks the next 7 days and only messages you if something is due.
4. **Weekly** it reads your KDP emails (read-only, if you connect Gmail) and proposes ledger updates for you to confirm.
5. **Monthly** it re-reads the KDP Help pages and tells you if a rule changed.

Times are shown in your time zone, next to KDP's own: Pacific for promotions, UTC for pre-order cutoffs, UK time for Amazon.co.uk deals.

## Repo layout

```
kdp-rules.md            every rule with ID, KDP Help URL, and date checked
calc/shelf_clock.py     dependency-free deadline calculator + promo preflight (Python 3.9+)
tests/                  31 tests: 5 fixture books with hand-worked dates + edge cases
                        (term boundaries, leap years, DST); HAND-WORKED.md; TEST-RUN.md
skills/                 the bot's skills (getting-started, kdp-rules, deadline-calc,
                        promo-preflight, kdp-email-intake, ledger-upkeep)
template.md             bot profile, instructions, routine drafts
examples/books.example.json
sources/                text snapshots of the KDP Help pages used
```

## Use the calculator on its own

```
python3 calc/shelf_clock.py deadlines examples/books.example.json --horizon 120
python3 calc/shelf_clock.py preflight examples/books.example.json --book B1 --action kcd --date 2026-12-20 --days 7 --price 0.99
python3 -m unittest -v tests/test_shelf_clock.py
```

## Honest limits

- **KDP doesn't publish everything.** It doesn't say which time zone the 72-hour pre-order window counts from. Shelf Clock uses 00:00 UTC on release day, which matches KDP's own Bookshelf timer and is the earliest reading. KDP also doesn't give a time of day for Select renewals or term boundaries; Shelf Clock assumes midnight Pacific.
- **KDP's screens are the final word.** Always check the pre-order timer on your title setup page and the dates on Manage KDP Select.
- **Rules change.** KDP changed pre-order rules on Sep 2, 2026 and the 70% price band on Jul 7, 2026. Rules were last checked Nov 24, 2026, and the bot re-checks monthly.
- **This isn't legal, tax, or financial advice.**

## License

To be decided by the owner before publishing.

Shelf Clock is not affiliated with Amazon, KDP, or BookBub.
