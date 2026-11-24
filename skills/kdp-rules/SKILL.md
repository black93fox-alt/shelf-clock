---
name: kdp-rules
description: Use whenever you state, apply, or re-check a KDP pre-order, KDP Select, Free Book Promotion, Countdown Deal, list-price, or BookBub rule, and for the monthly rules check.
---
# KDP rules

The rule book is `kdp-rules.md` in the template root. On the bot's own box it lives at `/workspace/shelf-clock/kdp-rules.md`.
- Every rule has an ID (PO-3, KCD-5, …), a source URL, and the date it was last checked.
- Quote the rule ID and URL whenever you tell the owner a rule.

## Core facts (keep in sync with kdp-rules.md)

**Pre-orders**
- The final manuscript must be submitted **72 h before release**. Shelf Clock counts from 00:00 UTC on release day, matching KDP's timer.
- For an account's **first-ever title** it's 5 days.
- Missing the deadline cancels the pre-order. A second miss or cancellation removes pre-order privileges for **6 months**.
- Pre-orders created on or after Sep 2, 2026 can be postponed up to **2 times**, to no more than **6 months** past the original date, and only before the deadline.

**KDP Select**
- Terms are **90 days**, and auto-renew is on by default.
- Opting out means turning auto-renew off **before the next renewal**. The current term is unaffected.
- A new enrollment can be cancelled within 3 days.
- For a pre-order, the term starts on the release date, and promotions can only be scheduled after release.

**Free days**
- 5 per term. The earliest is day 2 of the term.
- Schedule at least one day ahead, before 8 PM PT for a midnight start.
- They don't roll over, can't be scheduled for a future term, and run midnight to midnight Pacific with an exclusive end date.

**Countdown Deal**
- Amazon.com and Amazon.co.uk only.
- 30+ days enrolled.
- List price $2.99–$24.99 (£1.99–£15.99), with at least $1 off.
- **Price unchanged 30 days before and 14 days after.**
- At most 5 increments, 1 hour to 7 days long.
- Schedule 24 h ahead.
- One per term.
- It must end 14 days before the term ends unless the book renews.
- Times are Pacific for .com and UK time for .co.uk.

**Combining and pricing**
- Free days *or* a KCD in a term, never both.
- The 70% royalty band is $2.99–$12.99 on Amazon.com.

**BookBub (advisory only)**
- Free or at least 50% off, and no better price in the last 30 days.
- Same book at most once per 6 months, same author at most once per 30 days.

## Monthly rules check

1. Re-fetch each source URL listed in kdp-rules.md, with curl or a web fetch. KDP Help pages are public.
2. Compare each rule's wording and numbers with the file.
3. If anything changed, tell the owner what changed, citing the old and new text and the URL.
4. Propose the edit to kdp-rules.md and the matching constant in `calc/shelf_clock.py`. After the owner says yes, apply both and run the tests (`python3 -m unittest tests/test_shelf_clock.py`). If tests fail, roll back.
5. If nothing changed, update the "Checked" date and stay quiet.

## Honesty

- Where KDP is silent, say so and point the owner to KDP's own timer or screen:
  - the time zone for the 72 hours
  - the term-boundary time
  - the renewal cutoff
- Never present an assumption as a KDP rule. Owner buffers are labeled OWN-x.
