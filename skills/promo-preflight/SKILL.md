---
name: promo-preflight
description: Use when the owner asks whether they can change a KDP list price, run free days, run a Kindle Countdown Deal, or apply for a BookBub deal on a given date, and before they make any such change in KDP themselves.
---
# Promo preflight

Answer **YES**, **NO**, or **CHECK**, with the rule and source for each point, and a better date when the answer is NO.

## Run

```
python3 /workspace/shelf-clock/calc/shelf_clock.py preflight /workspace/shelf-clock/books.json --book ID --action price   --date YYYY-MM-DD --price 3.99
python3 /workspace/shelf-clock/calc/shelf_clock.py preflight /workspace/shelf-clock/books.json --book ID --action free    --date YYYY-MM-DD --days 3
python3 /workspace/shelf-clock/calc/shelf_clock.py preflight /workspace/shelf-clock/books.json --book ID --action kcd     --date YYYY-MM-DD --days 7 --price 0.99 [--marketplace amazon.co.uk] [--increments 2]
python3 /workspace/shelf-clock/calc/shelf_clock.py preflight /workspace/shelf-clock/books.json --book ID --action bookbub --date YYYY-MM-DD --price 0.99
```

Add `--now "YYYY-MM-DD HH:MM"` (owner's zone) to test a scheduling time, and `--json` for structured output.

## How to answer

1. **Make sure the ledger is current.** Ask about any price change or promotion not yet recorded. A preflight on a stale ledger is wrong.
2. Lead with the answer and a one-line reason. Then list each check (ok / NO / ??) with its rule ID and URL.
3. **On NO,** give the suggested date and why it works.
4. **On CHECK,** explain the caveat. Examples:
   - outside the 70% band
   - scheduled after 8 PM PT
   - a deal in a future term
   - a pre-order not yet released
5. **Side effects.** Mention them:
   - a price change pushes the earliest Countdown Deal 30 days out
   - a KCD locks the price until 14 days after it ends
   - free days use up this term's promotion type
6. **End with the action note:** "If you go ahead, you make this change in KDP yourself; tell me when it's done and I'll update the ledger."

## Never

Never change the price, schedule, or submit anything yourself, including BookBub (it costs money).
