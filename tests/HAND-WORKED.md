# Hand-worked expected values (worked out before running the code)

Notation: "+90" means calendar days. Term end is *exclusive* (the next term's day 1);
the last day of a term is end − 1. Midnight PT = 2:00 AM CT, except on the two DST
Sundays (see below). 00:00 UTC = 6:00 PM CST / 7:00 PM CDT on the previous day.
US DST 2027 starts Sun Mar 14; DST 2026 ended Sun Nov 1.

## The five fixture books
**A — first-ever KDP title, pre-order, release Tue Mar 16 2027, Select, auto-renew OFF**
- Manuscript deadline (PO-4, 5 days = 120 h): Mar 16 00:00 UTC − 120 h = Mar 11 00:00 UTC = **Mar 10 6:00 PM CST** (DST not yet in effect).
- Term 1 starts on release (PO-8): Mar 16 → +90: Mar 16→Apr 16 (31), →May 16 (30) = 61, →Jun 14 (29) = 90. **Term 1 = Mar 16 – Jun 13; end-exclusive Jun 14.**
- Earliest free day = day 2 = **Mar 17**, 00:00 PDT = **2:00 AM CDT**.
- Earliest KCD = Mar 16 + 30 = **Apr 15**.
- Latest KCD end with auto-renew OFF = Jun 14 − 14 = **May 31** (00:00 PT).
- Free promo on Mar 10 (before release) → **NO** (PO-8). Free promo on Mar 20 asked in Nov 2026 → **CHECK**: valid plan, but it can only be scheduled after release.

**B — returning author, pre-order, release Tue Feb 23 2027, Select, auto-renew ON (shaped like a real pre-order)**
- Deadline (PO-3, 72 h): Feb 23 00:00 UTC − 72 h = Feb 20 00:00 UTC = **Feb 19 6:00 PM CST**. This equals KDP's Bookshelf timer wording "before Feb 19 11:59 PM GMT".
- Safe target (7-day buffer) = **Feb 12 6:00 PM CST**.
- Term 1: Feb 23 →Mar 23 (28) →Apr 23 (31) = 59 →May 24 (31) = 90. **Term 1 = Feb 23 – May 23; renews May 24 00:00 PDT = 2:00 AM CDT.**
- 10-day alert = last day May 23 − 10 = **May 13**.
- Earliest KCD = Feb 23 + 30 = **Mar 25**.

**C — Select since Nov 4 2026 (day 20 on Nov 24)**
- KCD Nov 24 → **NO** (KCD-2); earliest Nov 4 + 30 = **Dec 4**.
- KCD Dec 4: safe booking = Dec 2 00:00 PST = **Wed Dec 2 2:00 AM CST**; hard (24 h) = Dec 3 00:00 PST = **Thu Dec 3 2:00 AM CST**.
- Term 1 end-exclusive: Nov 4 →Dec 4 (30) →Jan 4 (31) = 61 →Feb 2 (29) = 90 → **Feb 2 2027**.

**D — Select since Aug 1 2026; list price changed Nov 10 2026**
- KCD Nov 30 → **NO** (KCD-5): the change on Nov 10 is within the 30 days before. Earliest = Nov 10 + 30 = **Dec 10** → YES.
- Terms: Aug 1 →Sep 1 (31) →Oct 1 (30) = 61 →Oct 30 (29) = 90; term 2 = **Oct 30 – Jan 27**, end-exclusive **Jan 28 2027** (Oct 30 →Nov 30 (31) →Dec 30 (30) →Jan 28 (29)).
- Price drop Dec 1 → YES; side effect: next KCD no earlier than Dec 1 + 30 = **Dec 31**.

**E — Select since Sep 12 2026; free promo Nov 20–22 (end exclusive = 2 days used)**
- Term 1: Sep 12 →Oct 12 (30) →Nov 12 (31) = 61 →Dec 11 (29) = 90 → **term 1 = Sep 12 – Dec 10**. Term 2 = Dec 11 →Jan 11 (31) →Feb 11 (31) = 62 →Mar 11 (28) = 90 → **Dec 11 – Mar 10**.
- KCD Dec 1 → **NO** (PROMO-1, free days already used this term); suggest **Dec 11** (term 2).
- Free 4 days from Dec 5 → 2 + 4 = 6 > 5 → **NO**; 3 days → **YES**.
- Free Dec 10 for 2 days → runs into term 2 → **NO** (FREE-5).
- Free Dec 11 → term 2 day 1 → **NO** (FREE-3); suggest **Dec 12**.
- Free Dec 12 asked on Nov 24 (still term 1) → **NO** (FREE-7, can't schedule for a future term).
- KCD Dec 11 asked Nov 24 → **CHECK** (KDP only states the future-term rule for free promos).

## Edge cases
- Leap: Jan 15 2028 + 90 = Jan 15→Feb 15 (31) →Mar 15 (29, leap) = 60 →Apr 14 (30) = 90 → **Apr 14 2028**. Non-leap 2027: 31 + 28 + 31 = 90 → **Apr 15 2027**. Feb 29 2028 →Mar 29 (29) →Apr 29 (31) = 60 →May 29 (30) = 90 → **May 29 2028**.
- DST spring forward: free promo Sun Mar 14 2027: 00:00 PST = 08:00 UTC; CT jumps to CDT at 08:00 UTC → **3:00 AM CDT**.
- DST fall back: free promo Sun Nov 1 2026: 00:00 PDT = 07:00 UTC; CT falls back at 07:00 UTC → **1:00 AM CST**.
- Pre-order deadlines around DST: release Mar 16 2027 → Mar 13 00:00 UTC = **Mar 12 6 PM CST**; Mar 17 → Mar 14 00:00 UTC (before the 08:00 UTC switch) = **Mar 13 6 PM CST**; Mar 18 → Mar 15 00:00 UTC = **Mar 14 7 PM CDT**.
- KCD price range: $2.98 NO; $2.99 yes; $24.99 yes; $25.00 NO. Promo $4.00 from $4.99 = $0.99 off → NO (min $1.00).
- KCD 8 days → NO; 6 increments → NO.
- G (Select Oct 1 2026, auto-renew OFF): term 1 end-exclusive Oct 1 →Nov 1 (31) →Dec 1 (30) = 61 →Dec 30 (29) = 90 → **Dec 30**; latest KCD end = Dec 30 − 14 = **Dec 16**. A KCD from Dec 10 for 7 days ends Dec 17 → NO; from Dec 9 it ends Dec 16 → OK.
- G booked KCD Jan 5 for 7 days (ends Jan 12 exclusive): lock starts Jan 5 − 30 = **Dec 6 2026**; first allowed change = Jan 12 + 14 = **Jan 26 2027**. Price change Dec 5 OK, Dec 6 NO, Jan 25 NO, Jan 26 OK.
- KCD booking: Dec 4 start, asked Dec 3 3:00 AM CST (after the 2:00 AM hard cutoff) → NO; asked Dec 2 noon → CHECK.
- UK KCD Dec 20 2026 starts 00:00 GMT = **Sat Dec 19 6:00 PM CST**; £1.99 list is within £1.99–£15.99.
- Free scheduling cutoff for a Nov 26 start: 8 PM PST Nov 25 = 10 PM CST. 9:30 PM CST OK; 10:30 PM CST → CHECK; 2:30 AM CST Nov 26 (after midnight PT) → NO.
- BookBub (E, deal Dec 20 2026 at $0.99): free promo Nov 20–21 is within 30 days → BB-2 NO; last feature Jul 15 2026 + 6 months = **Jan 15 2027** → BB-3 NO. Author feature Nov 10 → not before **Dec 10** → BB-4. $2.50 on a $4.99 book is above 50% (≤ $2.495) → BB-1 NO.
- Price $1.99 on a 70% book → CHECK (outside $2.99–$12.99); $12.99 → YES.
- Paperback: release event only (no pre-order, no Select).
