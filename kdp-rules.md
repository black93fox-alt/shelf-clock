# KDP rules Shelf Clock relies on

**Checked:** Tue Nov 24, 2026 (America/Chicago). Each page was fetched live with curl, and text snapshots are in `sources/`.

**How to use this file:**
- Rule IDs match the calculator (`calc/shelf_clock.py`) and the skills.
- If KDP changes a page, update the rule here, update the constant in the calculator, and re-run the tests.
- The monthly rules-check routine re-fetches these URLs and compares them with this file.

## Sources

| Key | Page | URL |
|---|---|---|
| preorder | Kindle eBook Pre-Order | https://kdp.amazon.com/en_US/help/topic/G201499380 |
| postpone | Postpone or cancel a pre-order release | https://kdp.amazon.com/en_US/help/topic/G201499440 |
| change_release | Change your pre-order release | https://kdp.amazon.com/en_US/help/topic/G201499480 |
| timelines | Timelines | https://kdp.amazon.com/en_US/help/topic/G202173620 |
| select | KDP Select | https://kdp.amazon.com/en_US/help/topic/G200798990 |
| enrollment | KDP Select Enrollment | https://kdp.amazon.com/en_US/help/topic/GD9PMU58BV24QFZ7 |
| free | Free Book Promotions | https://kdp.amazon.com/en_US/help/topic/G201298240 |
| kcd | Kindle Countdown Deals | https://kdp.amazon.com/en_US/help/topic/G201293780 |
| price | eBook List Price Requirements | https://kdp.amazon.com/en_US/help/topic/G200634560 |
| bookbub | BookBub Featured Deals Requirements | https://www.bookbub.com/partners/requirements |

Every source was checked on 2026-11-24. KDP pages were fetched with curl; the BookBub page returned 403 to curl, so it was read through a web fetch.

## Pre-orders (eBook only)

- **PO-1:** Pre-orders are for **new Kindle eBooks only**. The limit is 10 active pre-orders. Release dates can be up to **18 months** out for pre-orders created on or after Sep 2, 2026 (12 months before that). [preorder]
- **PO-2:** Paperbacks and hardcovers **can't be on pre-order**; they get a scheduled release date and are separate editions. [preorder]
- **PO-3:** The final manuscript must be **uploaded and submitted at least 72 hours before the release date**. Inside 72 hours, nothing can be changed. [preorder, timelines]
  - *Time basis:* KDP doesn't say which time zone the 72 hours count from. KDP's own Bookshelf timer showed "before Feb 19 11:59 PM GMT" for a Feb 23 release, which is 72 hours before **00:00 UTC** on release day. Shelf Clock uses 00:00 UTC; it is also the earliest plausible reading, so it's the safe one.
  - In Chicago that's 6:00 PM CST, or 7:00 PM CDT, three days before.
  - The bot always tells the owner to also check the timer on the title setup page, which KDP says is "the most accurate timeline".
- **PO-4:** **First title an account publishes on KDP:**
  - The manuscript must be uploaded when the pre-order is submitted.
  - The final version is due **at least 5 days before release** (5 days = 120 h, same UTC basis).
  - The release date must be at least 5 days out. [preorder, timelines]
- **PO-5:** List price can change at any time. If it is lowered, pre-order customers pay the lower price. [preorder]
- **PO-6:** Missing the deadline **cancels the pre-order** and the customer orders.
  - First miss or cancellation per account: no penalty (a one-time courtesy).
  - **Second: pre-order privileges are removed for 6 months**, catalog-wide. During that time the account can't create or postpone pre-orders.
  - A one-year penalty still applies if privileges were removed before Sep 2, 2026.
  - A cancelled pre-order's ASIN can't be reused. [preorder, postpone]
- **PO-7:** **Postponing:**
  - Pre-orders created on or after Sep 2, 2026: **up to 2 postponements**, and the new date can be no more than **6 months after the original release date**.
  - Pre-orders created before then: 1 postponement of up to 30 days.
  - Exceeding the limit auto-cancels the pre-order, which counts toward PO-6.
  - Any release-date change must happen **before the submission deadline**.
  - Moving the date earlier needs the final manuscript submitted. The earliest new date is 3 days from today (5 for a first title). [postpone, change_release]
- **PO-8:** A pre-order can be enrolled in KDP Select.
  - **The Select term begins on the release date.**
  - Free Book Promotions and Countdown Deals can **only be scheduled after release**. [preorder]
  - Select enrollment of a pre-order can't be cancelled until the book is released. [enrollment]

## KDP Select terms and renewal (settles an open item)

- **SEL-1:** KDP Select is a **90-day** program. During the term, the Kindle eBook must be exclusive to Amazon (public libraries excepted). Print and audio can go elsewhere. [select, enrollment]
- **SEL-2: Auto-renewal.** "Every KDP Select–enrolled title will be **automatically renewed every 90 days from the time you first enrolled it, unless you opt out through the KDP website before the next renewal**." [timelines]
  - Auto-renew is **on by default**. It is turned off at Bookshelf → "…" → Manage KDP Select → "Turn off automatic renewal" → Save. [enrollment]
  - Changing the setting **does not affect the current term**, so the book stays enrolled and exclusive until the term ends.
  - **What this means for opting out:** turning auto-renew off any time before the renewal moment ends Select at the end of the current term. Once the next term starts, the book is locked in (and exclusive) for another 90 days.
  - KDP publishes **no earlier cutoff and no time of day** for renewal. Shelf Clock treats the renewal as midnight Pacific at the start of the next term's day 1 (this is an assumption, see SEL-6). It tells the owner to switch auto-renew off **at least 3 days early** (our buffer, not a KDP rule) and to check the Manage KDP Select screen for the exact end date.
  - If an eBook has an associated audiobook, turning auto-renew off removes the virtual-voice audiobook from Kindle+/Audible Plus at the end of the term.
- **SEL-3:** Free days don't roll over. "Unused Free Book Promotion days won't rollover from one enrollment period to another." [free] This is why the bot sends an end-of-term alert 10 days before each term's last day.
- **SEL-4:** A new enrollment can be **cancelled within 3 days of the enrollment start** (after that, contact KDP). [select, enrollment]
- **SEL-5:** Unpublishing a Select title pauses its term until it's republished. [enrollment] The calculator doesn't model pauses, so the owner must re-enter the term start shown by KDP.
- **SEL-6 (assumption):** KDP doesn't state the time zone of term boundaries. Shelf Clock assumes midnight Pacific, the same as promotions. Exact start and end **dates** come from Bookshelf → Manage KDP Select, which shows them. Always prefer the dates KDP shows over computed ones.

## Free Book Promotions

- **FREE-1:** Up to **5 free days per 90-day term**, for Kindle eBooks only, in all marketplaces. No royalties are paid on free days. [free]
- **FREE-2:** The book must be **enrolled in KDP Select and live** to schedule one. [free]
- **FREE-3:** The earliest start is **day 2 of the term**. [free]
- **FREE-4:** It must be scheduled **at least one day before** the start date.
  - Scheduled before **8:00 PM PT** the day before, it starts at about midnight PT.
  - Scheduled after 8 PM, it starts within about 4 hours. [free, timelines]
- **FREE-5:** Free days can't be scheduled into a different term (no carry-over, and you can't schedule for future terms). Shelf Clock rejects a promo that would cross the term end. [free]
- **FREE-6:** KDP says to **avoid ending on the final day of the term**. Shelf Clock treats this as a warning. [free]
- **FREE-7:** "We're unable to schedule a Free Book Promotion for **future KDP Select enrollment periods**." You can schedule once the new term begins. [free]
- **FREE-8:** Start and end are **midnight Pacific**, and the **end date is exclusive**: start Jan 2 + end Jan 7 = 5 days (Jan 2–6). [free, timelines]
  - In Chicago, midnight PT is 2:00 AM.
  - On the US DST Sundays it is 3:00 AM CDT (spring) or 1:00 AM CST (fall).
  - Calculator input is start + number of days.

## Kindle Countdown Deals (KCD)

- **KCD-1:** Available on **Amazon.com and Amazon.co.uk only**, for KDP Select eBooks. [kcd, select]
- **KCD-2:** The title must have been **enrolled in KDP Select for at least 30 days**. [kcd]
- **KCD-3:** The list price must be **$2.99–$24.99** (Amazon.com) or **£1.99–£15.99** (Amazon.co.uk, including VAT). [kcd]
- **KCD-4:** The minimum discount from list is **$1.00 / £1.00**. [kcd]
- **KCD-5: Price lock.** The digital list price must be **unchanged for 30 days before and 14 days after** the deal. [kcd]
  - The calculator blocks any list-price change from (start − 30 days) up to (end + 14 days), where the end is exclusive.
  - *Boundary:* a change exactly 30 days before the start is treated as allowed. If you want zero risk, add a day.
- **KCD-6:** A maximum of **5 price increments**. [kcd]
- **KCD-7:** Duration is **1 hour to 7 days**, run as one block. [kcd]
- **KCD-8: Scheduling.** It must be scheduled **24 hours before** the start. A deal can't be edited or cancelled within 24 hours of starting or while it runs. [kcd, timelines]
  - KDP's two pages give different examples for a Jan 10 start: "before Jan 8" on the KCD page, "before Jan 9" on Timelines.
  - Shelf Clock shows **both**: a *safe* target (00:00 two days before) and the *hard* 24-hour cutoff.
- **KCD-9:** The latest end is **14 days before the Select term ends**. If the book renews into a consecutive term (auto-renew on), the end can fall on the term's last day. [kcd]
- **KCD-10:** **One KCD per Select term.** [kcd]
- **KCD-11:** KDP states the "no future term" limit only for free promos. Shelf Clock flags a KCD in a future term as CHECK, not NO.
- **KCD-12:** Time zone: Amazon.com deals run on **Pacific time**, and Amazon.co.uk deals on **UK time (GMT/BST)**. [kcd]
- **PROMO-1:** **Only one promotion type per term:** free days *or* a KCD, never both. [kcd, free]

## Price and timing

- **PRICE-1:** On Amazon.com the 70% royalty plan needs a list price of **$2.99–$12.99** (widened from $9.99 on July 7, 2026). Outside that band, only the 35% plan applies. [price] Shelf Clock warns (CHECK); it never changes a price.
- **TIME-1:** List-price updates take up to **24 hours** to appear. [timelines]

## BookBub Featured Deals (settles an open item: sourced, kept in scope as an advisory check)

- **BB-1:** The deal must be **free or at least 50% off**. [bookbub]
- **BB-2:** It must be the best deal available: **no better price in the last 30 days**, or soon after. [bookbub]
- **BB-3:** BookBub won't feature **the same book more than once every 6 months**. [bookbub]
- **BB-4:** BookBub won't feature **the same author more than once every 30 days**. [bookbub]
- **BB-5:** Length minimums apply (novels and collections 150 pages, nonfiction 100, middle grade 100, cookbooks 70, picture books 20). Meeting the rules doesn't guarantee selection. After a rejection, wait at least 4 weeks before resubmitting. [bookbub]

BookBub is a paid service. Shelf Clock only checks eligibility; it never submits or pays.

## Owner buffers (not KDP rules)

- **OWN-1:** A safe target for the pre-order manuscript, `safe_buffer_days` (default 7) before KDP's cutoff.
- **OWN-2:** Turn off auto-renew at least 3 days before the renewal.
- **OWN-3:** An end-of-term alert 10 days before each term's last day.

## Things Shelf Clock never does

It never:
- logs into KDP
- changes a price
- schedules or cancels a promotion
- uploads
- publishes
- submits to BookBub
- asks readers for reviews

Amazon's rules forbid asking for or incentivizing reviews. Advance copies (ARCs) are fine, but no review may be required in exchange.
