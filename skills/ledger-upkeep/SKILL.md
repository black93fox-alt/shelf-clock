---
name: ledger-upkeep
description: Use to create or update the Book Ledger (Google Sheet or a Page) from /workspace/shelf-clock/books.json, and to show the owner their books and upcoming deadlines.
---
# Book Ledger upkeep

**Source of truth:** `/workspace/shelf-clock/books.json`, the calculator input. The Sheet or Page is the owner's view. If the owner edits the Sheet, read it back into books.json before running the calculator, and confirm any conflicts with the owner.

## Layout

**Sheet tab "Books"** (one row per edition). Columns:
- ID, Title, Format, ASIN
- Release date, Pre-order (Y/N), First KDP title (Y/N), Manuscript submitted (Y/N)
- Select (Y/N), Select term start, Select term end, Select dates source (KDP screen / owner / computed), Auto-renew (Y/N)
- List price, Royalty plan, Last price change
- Free days used (this term), KCD this term (date/none), Last BookBub
- Notes

**Tab "Promotions":** Book ID, Type (free/kcd), Start, Days, Start price, Marketplace, Term #, Source.

**Tab "Price changes":** Book ID, Date, Old price, New price, Source.

**Tab "Next 120 days":** the output of `shelf_clock.py deadlines --horizon 120`. Columns: When (owner zone), KDP time, Book, Kind, What, Rule, Source.

**If Drive isn't connected:** make a Page with a books table, a "Next 30 days" list, and a "Needs confirming" list for `unconfirmed` Select dates.

## When to update

- After onboarding
- After each confirmed email intake
- After the owner reports a change they made in KDP
- On the weekly routine

Before overwriting the "Next 120 days" tab, take a dated backup copy of books.json (`books.YYYY-MM-DD.json`).

## Limits

- Never delete the owner's rows without asking.
- Never put KDP passwords, payment, or tax data in the ledger.
