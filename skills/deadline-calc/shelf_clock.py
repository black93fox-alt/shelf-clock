#!/usr/bin/env python3
"""Shelf Clock: KDP deadline calculator and promo preflight.

Dependency-free (Python 3.9+ standard library only; uses zoneinfo with the
system tz database). Rule IDs (e.g. PO-1) refer to ../kdp-rules.md.

Conventions
- Input dates are KDP calendar dates (YYYY-MM-DD). KDP runs Free Book
  Promotions and Amazon.com Countdown Deals on Pacific time (midnight PT);
  Amazon.co.uk Countdown Deals run on UK time. We assume KDP Select term
  boundaries also fall at midnight Pacific (KDP does not say; see SEL-6).
- Pre-order manuscript deadlines are computed from 00:00 UTC on the release
  date (this matches the deadline KDP's own Bookshelf timer shows, e.g.
  "before Feb 19 11:59 PM GMT" for a Feb 23 release). UTC is also the
  earliest of the plausible interpretations, so it is the safe one.
- Every output time is shown in the owner's zone (default America/Chicago)
  and, where KDP uses Pacific or UTC, that original time as well.
- Free Book Promotion end dates are exclusive, as on KDP's help page
  (start Jan 2, end Jan 7 = 5 days: Jan 2-6). In this tool a free promo is
  given as start + days.

Usage
  python3 shelf_clock.py deadlines BOOKS.json [--today YYYY-MM-DD] [--horizon 120] [--json]
  python3 shelf_clock.py preflight BOOKS.json --book ID --action price|free|kcd|bookbub
          --date YYYY-MM-DD [--days N] [--price X] [--increments N]
          [--marketplace amazon.com|amazon.co.uk] [--now "YYYY-MM-DD HH:MM"] [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Los_Angeles")
UK = ZoneInfo("Europe/London")
UTC = timezone.utc
DEFAULT_TZ = "America/Chicago"

SRC = {
    "preorder": "https://kdp.amazon.com/en_US/help/topic/G201499380",
    "postpone": "https://kdp.amazon.com/en_US/help/topic/G201499440",
    "change_release": "https://kdp.amazon.com/en_US/help/topic/G201499480",
    "timelines": "https://kdp.amazon.com/en_US/help/topic/G202173620",
    "select": "https://kdp.amazon.com/en_US/help/topic/G200798990",
    "enrollment": "https://kdp.amazon.com/en_US/help/topic/GD9PMU58BV24QFZ7",
    "free": "https://kdp.amazon.com/en_US/help/topic/G201298240",
    "kcd": "https://kdp.amazon.com/en_US/help/topic/G201293780",
    "price": "https://kdp.amazon.com/en_US/help/topic/G200634560",
    "bookbub": "https://www.bookbub.com/partners/requirements",
}

TERM_DAYS = 90
FREE_DAYS_PER_TERM = 5
KCD_MIN_ENROLLED_DAYS = 30
KCD_LOCK_BEFORE = 30
KCD_LOCK_AFTER = 14
KCD_END_BUFFER = 14
KCD_MAX_DAYS = 7
KCD_MAX_INCREMENTS = 5
KCD_RANGE = {"amazon.com": (2.99, 24.99, 1.00, "$"), "amazon.co.uk": (1.99, 15.99, 1.00, "£")}
ROYALTY70_US = (2.99, 12.99)


# ---------------------------------------------------------------- helpers
def d(s):
    if s is None or isinstance(s, date):
        return s
    return date.fromisoformat(s)


def midnight(day: date, tz) -> datetime:
    return datetime.combine(day, time(0, 0), tzinfo=tz)


def fmt(dt: datetime, tz) -> str:
    loc = dt.astimezone(tz)
    return loc.strftime("%a %b %d %Y %I:%M %p ") + loc.tzname()


def fmt_pair(dt: datetime, tz, orig_tz, orig_label) -> str:
    o = dt.astimezone(orig_tz)
    return f"{fmt(dt, tz)} ({orig_label} {o.strftime('%b %d %I:%M %p')} {o.tzname()})"


def promo_tz(marketplace):
    return UK if marketplace == "amazon.co.uk" else PT


class Book:
    def __init__(self, raw: dict):
        self.raw = raw
        self.id = raw["id"]
        self.title = raw.get("title", self.id)
        self.format = raw.get("format", "ebook").lower()
        self.release = d(raw.get("release_date"))
        self.preorder = bool(raw.get("preorder", False))
        self.first_title = bool(raw.get("first_kdp_title", False))
        self.created_after_sep2 = bool(raw.get("preorder_created_on_or_after_2026_09_02", True))
        self.manuscript_submitted = bool(raw.get("manuscript_submitted", False))
        sel = raw.get("select") or {}
        self.select = bool(sel.get("enrolled", False)) and self.format == "ebook"
        start = d(sel.get("start"))
        if self.select and start is None and self.preorder:
            start = self.release  # PO-8: term begins on release date
        self.select_start = start
        self.auto_renew = bool(sel.get("auto_renew", True))
        self.price = raw.get("list_price")
        self.royalty = raw.get("royalty_plan", 70)
        self.price_changes = sorted(d(x) for x in raw.get("price_changes", []))
        self.promos = []
        for p in raw.get("promos", []):
            q = dict(p)
            q["start"] = d(p["start"])
            if q["type"] == "free":
                q["days"] = int(p.get("days") or (d(p["end"]) - q["start"]).days)
            else:
                q["days"] = int(p.get("days", 7))
                q["marketplace"] = p.get("marketplace", "amazon.com")
            q["end"] = q["start"] + timedelta(days=q["days"])  # exclusive
            self.promos.append(q)
        self.bookbub = sorted(d(x) for x in raw.get("bookbub_features", []))

    # ---- KDP Select terms (SEL-1, SEL-2)
    def term_index(self, day: date):
        if not self.select or self.select_start is None or day < self.select_start:
            return None
        return (day - self.select_start).days // TERM_DAYS

    def term(self, n: int):
        s = self.select_start + timedelta(days=TERM_DAYS * n)
        return s, s + timedelta(days=TERM_DAYS)  # start, exclusive end

    def live_on(self, day: date) -> bool:
        return self.release is not None and day >= self.release


def rule(ok, rid, text, src):
    return {"ok": ok, "rule": rid, "text": text, "source": SRC[src]}


# ------------------------------------------------------------- deadlines
def deadlines(book: Book, today: date, horizon: int, tz, buffer_days: int = 7):
    ev = []
    end = today + timedelta(days=horizon)

    def add(dt, kind, text, rid, src, orig=None):
        if isinstance(dt, date) and not isinstance(dt, datetime):
            when = dt.isoformat()
            sort = midnight(dt, tz)
            disp = dt.strftime("%a %b %d %Y")
        else:
            sort = dt
            disp = fmt_pair(dt, tz, *orig) if orig else fmt(dt, tz)
            when = dt.astimezone(tz).isoformat()
        ev.append({"book": book.id, "title": book.title, "when": when, "display": disp,
                   "kind": kind, "text": text, "rule": rid, "source": SRC[src], "_sort": sort})

    # Print editions: no pre-order, only a scheduled release date (PO-2)
    if book.format != "ebook":
        if book.preorder:
            add(today, "warning", "Print editions can't be on pre-order; only a scheduled release date.", "PO-2", "preorder")
        if book.release and today <= book.release <= end:
            add(book.release, "release", f"{book.format.title()} scheduled release.", "PO-2", "preorder")
        return ev

    if book.preorder and book.release:
        hours = 120 if book.first_title else 72
        rel_utc = midnight(book.release, UTC)
        dl = rel_utc - timedelta(hours=hours)
        rid = "PO-4" if book.first_title else "PO-3"
        if not book.manuscript_submitted or dl.date() >= today:
            add(dl, "deadline", f"Final manuscript must be uploaded AND submitted before this ({hours // 24} days before release). "
                "Missing it cancels the pre-order (PO-6). Also the last moment to postpone or change the release date (PO-7).",
                rid, "preorder", (UTC, "UTC"))
            safe = dl - timedelta(days=buffer_days)
            add(safe, "target", f"Safe target: submit final manuscript {buffer_days} days ahead of KDP's cutoff (owner buffer, not a KDP rule).",
                "OWN-1", "preorder", (UTC, "UTC"))
        if book.created_after_sep2:
            add(book.release, "info", "Postponement limit: up to 2 postponements, new date no more than 6 months after the ORIGINAL release date.",
                "PO-7", "postpone")
        add(book.release, "release", "Release day." + (" KDP Select term 1 starts today (PO-8)." if book.select else ""),
            "PO-8" if book.select else "PO-1", "preorder")

    if book.select and book.select_start:
        n0 = book.term_index(max(today, book.select_start)) or 0
        n = max(0, n0 - 0)
        while True:
            ts, te = book.term(n)
            if ts > end:
                break
            last_day = te - timedelta(days=1)
            if te >= today:
                if ts >= today:
                    add(midnight(ts, PT), "select", f"KDP Select term {n + 1} starts (auto-renew).", "SEL-2", "timelines", (PT, "PT"))
                if n == 0 and not book.preorder:
                    add(midnight(ts + timedelta(days=3), PT), "deadline",
                        "End of the 3-day window to cancel this new KDP Select enrollment from the Bookshelf.", "SEL-4", "enrollment", (PT, "PT"))
                free_early = ts + timedelta(days=1)
                if free_early >= today:
                    add(midnight(free_early, PT), "window", f"Earliest Free Book Promotion day in term {n + 1} (day 2 of the term).", "FREE-3", "free", (PT, "PT"))
                kcd_early = max(book.select_start + timedelta(days=KCD_MIN_ENROLLED_DAYS), ts)
                if ts <= kcd_early < te and kcd_early >= today:
                    add(midnight(kcd_early, PT), "window", "Earliest Countdown Deal start (title enrolled 30+ days), if no free days are used this term and the price has been unchanged 30 days.",
                        "KCD-2", "kcd", (PT, "PT"))
                kcd_last = te if book.auto_renew else te - timedelta(days=KCD_END_BUFFER)
                add(midnight(kcd_last, PT), "window", f"Latest moment a term-{n + 1} Countdown Deal may END"
                    + (" (auto-renew ON: may run to the last day of the term)." if book.auto_renew else " (auto-renew OFF: 14 days before term end)."),
                    "KCD-9", "kcd", (PT, "PT"))
                alert = last_day - timedelta(days=10)
                if alert >= today:
                    used = sum(p["days"] for p in book.promos if p["type"] == "free" and book.term_index(p["start"]) == n)
                    kcd = any(p["type"] == "kcd" and book.term_index(p["start"]) == n for p in book.promos)
                    if kcd:
                        status = "Countdown Deal used this term."
                    else:
                        status = f"{FREE_DAYS_PER_TERM - used} free day(s) unused" + ("" if used else ", Countdown Deal unused") + " - they do not roll over."
                    add(alert, "alert", f"Term {n + 1} ends in 10 days (last day {last_day:%b %d}). {status} Decide on renewal now.", "SEL-3", "free")
                if book.auto_renew:
                    add(midnight(te, PT), "deadline", f"Auto-renews into term {n + 2} at this moment. To leave KDP Select, turn off automatic renewal on the Bookshelf BEFORE this (KDP gives no earlier cutoff; we suggest 3+ days early).",
                        "SEL-2", "enrollment", (PT, "PT"))
                else:
                    add(midnight(te, PT), "select", f"Enrollment ends (auto-renew is OFF). Ebook exclusivity ends after this moment.", "SEL-2", "enrollment", (PT, "PT"))
                    break
            n += 1

    for p in book.promos:
        tzp = promo_tz(p.get("marketplace", "amazon.com"))
        lab = "UK" if tzp is UK else "PT"
        s = midnight(p["start"], tzp)
        e = midnight(p["end"], tzp)
        if p["type"] == "free":
            if p["start"] - timedelta(days=1) >= today:
                add(midnight(p["start"] - timedelta(days=1), PT) + timedelta(hours=20), "deadline",
                    "Schedule free promo before this (day before, by 8 PM PT, so it starts at midnight).", "FREE-4", "timelines", (PT, "PT"))
            if p["end"] >= today:
                add(s, "promo", f"Free Book Promotion starts ({p['days']} day(s)).", "FREE-1", "free", (tzp, lab))
                add(e, "promo", "Free Book Promotion ends.", "FREE-1", "free", (tzp, lab))
        else:
            hard = s - timedelta(hours=24)
            safe = midnight(p["start"] - timedelta(days=2), tzp)
            if hard.date() >= today:
                add(safe, "target", "Schedule this Countdown Deal by now (matches KDP's own example: Jan 10 start -> schedule before Jan 8).", "KCD-8", "kcd", (tzp, lab))
                add(hard, "deadline", "Hard cutoff: Countdown Deals must be scheduled 24 hours before start; no edits/cancel inside 24h.", "KCD-8", "kcd", (tzp, lab))
            lock_s = p["start"] - timedelta(days=KCD_LOCK_BEFORE)
            lock_e = p["end"] + timedelta(days=KCD_LOCK_AFTER)
            if lock_e >= today:
                add(lock_s, "lock", f"PRICE LOCK begins: no list-price change from {lock_s:%b %d} until {lock_e:%b %d} (first allowed change day) for the Countdown Deal.", "KCD-5", "kcd")
                add(s, "promo", f"Countdown Deal starts ({p['days']} day(s), {p.get('marketplace', 'amazon.com')}).", "KCD-1", "kcd", (tzp, lab))
                add(e, "promo", "Countdown Deal ends.", "KCD-1", "kcd", (tzp, lab))
                add(lock_e, "lock", "Price lock over: list price may change again.", "KCD-5", "kcd")

    ev = [x for x in ev if today <= x["_sort"].astimezone(tz).date() <= end or x["kind"] == "warning"]
    ev.sort(key=lambda x: x["_sort"])
    return ev


# -------------------------------------------------------------- preflight
def preflight(book: Book, action: str, day: date, now: datetime, tz, days=None, price=None,
              increments=1, marketplace="amazon.com", author_bookbub=None):
    R = []
    alt = None
    today = now.astimezone(PT).date()

    if action == "price":
        # KCD lock check (KCD-5)
        for p in book.promos:
            if p["type"] != "kcd":
                continue
            ls, le = p["start"] - timedelta(days=KCD_LOCK_BEFORE), p["end"] + timedelta(days=KCD_LOCK_AFTER)
            if ls <= day < le:
                R.append(rule(False, "KCD-5", f"{day} is inside the Countdown Deal price lock ({ls} to {le - timedelta(days=1)}). First allowed change: {le}.", "kcd"))
                alt = le.isoformat()
        if not any(not r["ok"] for r in R):
            R.append(rule(True, "KCD-5", "No booked Countdown Deal price lock covers this date.", "kcd"))
        if price is not None and book.royalty == 70:
            lo, hi = ROYALTY70_US
            if not (lo <= price <= hi):
                R.append(rule(None, "PRICE-1", f"${price:.2f} is outside the 70% royalty band (${lo}-${hi} on Amazon.com since July 7, 2026). The book would need the 35% plan.", "price"))
            else:
                R.append(rule(True, "PRICE-1", f"${price:.2f} is inside the 70% royalty band.", "price"))
        if book.preorder and book.live_on(day) is False:
            R.append(rule(True, "PO-5", "Pre-order price can change any time; if lowered, pre-order customers pay the lower price.", "preorder"))
        R.append(rule(True, "TIME-1", "List price changes take up to 24 hours to appear.", "timelines"))
        if book.select:
            nxt = day + timedelta(days=KCD_LOCK_BEFORE)
            R.append(rule(True, "KCD-5", f"Side effect: the earliest Countdown Deal start after this change becomes {nxt}.", "kcd"))

    elif action == "free":
        days = int(days or 1)
        endx = day + timedelta(days=days)
        if book.format != "ebook":
            R.append(rule(False, "FREE-1", "Free Book Promotions are for Kindle eBooks only.", "free"))
        if not book.select:
            R.append(rule(False, "FREE-2", "Book is not enrolled in KDP Select.", "free"))
        else:
            if not book.live_on(day):
                R.append(rule(False, "PO-8", "Promotions can only run (and be scheduled) after the book is released (live).", "preorder"))
                alt = (book.release + timedelta(days=1)).isoformat() if book.release else None
            elif not book.live_on(today):
                R.append(rule(None, "PO-8", f"Plan is valid, but KDP only lets you schedule it after release on {book.release}.", "preorder"))
            n = book.term_index(day)
            if n is None:
                R.append(rule(False, "SEL-1", "Date is before KDP Select enrollment starts.", "select"))
            else:
                ts, te = book.term(n)
                if day < ts + timedelta(days=1):
                    R.append(rule(False, "FREE-3", f"Earliest free day in this term is day 2: {ts + timedelta(days=1)}.", "free"))
                    alt = (ts + timedelta(days=1)).isoformat()
                if endx > te:
                    R.append(rule(False, "FREE-5", f"Promo would run past the end of term {n + 1} (last day {te - timedelta(days=1)}). Days don't carry across terms.", "free"))
                elif endx == te:
                    R.append(rule(None, "FREE-6", "Ends on the final day of the term; KDP says to avoid this.", "free"))
                used = sum(p["days"] for p in book.promos if p["type"] == "free" and book.term_index(p["start"]) == n)
                if used + days > FREE_DAYS_PER_TERM:
                    R.append(rule(False, "FREE-1", f"Only {FREE_DAYS_PER_TERM - used} free day(s) left in term {n + 1} ({used} used).", "free"))
                else:
                    R.append(rule(True, "FREE-1", f"{used} used + {days} requested <= 5 for term {n + 1}.", "free"))
                if any(p["type"] == "kcd" and book.term_index(p["start"]) == n for p in book.promos):
                    R.append(rule(False, "PROMO-1", "A Countdown Deal is already in this term; only one promotion type per term.", "kcd"))
                tn = book.term_index(today)
                if tn is not None and tn < n:
                    R.append(rule(False, "FREE-7", f"Can't schedule for a future term; you can schedule once term {n + 1} begins on {ts}.", "free"))
                cutoff = midnight(day - timedelta(days=1), PT) + timedelta(hours=20)
                hard = midnight(day - timedelta(days=1), PT) + timedelta(hours=24)
                if now >= hard:
                    R.append(rule(False, "FREE-4", "Must be scheduled at least one day before the start date.", "free"))
                elif now >= cutoff:
                    R.append(rule(None, "FREE-4", "Scheduled after 8 PM PT the day before: it starts within ~4 hours of scheduling, not at midnight.", "timelines"))
                else:
                    R.append(rule(True, "FREE-4", f"Schedule before {fmt_pair(cutoff, tz, PT, 'PT')} to start at midnight PT.", "timelines"))
                R.append(rule(True, "FREE-8", f"Runs {fmt_pair(midnight(day, PT), tz, PT, 'PT')} to {fmt_pair(midnight(endx, PT), tz, PT, 'PT')}.", "free"))

    elif action == "kcd":
        days = int(days or 7)
        tzp = promo_tz(marketplace)
        lab = "UK" if tzp is UK else "PT"
        endx = day + timedelta(days=days)
        if marketplace not in KCD_RANGE:
            R.append(rule(False, "KCD-1", "Countdown Deals run only on Amazon.com and Amazon.co.uk.", "kcd"))
        if book.format != "ebook" or not book.select:
            R.append(rule(False, "KCD-1", "Countdown Deals need a Kindle eBook enrolled in KDP Select.", "kcd"))
        else:
            if not book.live_on(day):
                R.append(rule(False, "PO-8", "Promotions can only run (and be scheduled) after the book is released.", "preorder"))
            elif not book.live_on(today):
                R.append(rule(None, "PO-8", f"Plan is valid, but KDP only lets you schedule it after release on {book.release}.", "preorder"))
            need = book.select_start + timedelta(days=KCD_MIN_ENROLLED_DAYS)
            if day < need:
                R.append(rule(False, "KCD-2", f"Title must be enrolled at least 30 days; earliest start {need}.", "kcd"))
                alt = need.isoformat()
            else:
                R.append(rule(True, "KCD-2", f"Enrolled since {book.select_start} (30+ days).", "kcd"))
            lo, hi, mindrop, cur = KCD_RANGE.get(marketplace, KCD_RANGE["amazon.com"])
            if book.price is None or not (lo <= book.price <= hi):
                R.append(rule(False, "KCD-3", f"List price {cur}{book.price} must be {cur}{lo}-{cur}{hi}.", "kcd"))
            else:
                R.append(rule(True, "KCD-3", f"List price {cur}{book.price} is within {cur}{lo}-{cur}{hi}.", "kcd"))
            if price is not None and book.price is not None:
                if round(book.price - price, 2) < mindrop:
                    R.append(rule(False, "KCD-4", f"Starting promo price must be at least {cur}{mindrop:.2f} below list ({cur}{book.price}).", "kcd"))
                else:
                    R.append(rule(True, "KCD-4", f"Discount {cur}{book.price - price:.2f} meets the {cur}{mindrop:.2f} minimum.", "kcd"))
            if increments > KCD_MAX_INCREMENTS:
                R.append(rule(False, "KCD-6", "Maximum 5 price increments.", "kcd"))
            if days > KCD_MAX_DAYS or days < 1:
                R.append(rule(False, "KCD-7", "Duration must be 1 hour to 7 days, as one block.", "kcd"))
            recent = [c for c in book.price_changes if day - timedelta(days=KCD_LOCK_BEFORE) < c <= day]
            if recent:
                ok_from = recent[-1] + timedelta(days=KCD_LOCK_BEFORE)
                R.append(rule(False, "KCD-5", f"List price changed on {recent[-1]}; it must be unchanged for 30 days before the deal. Earliest start {ok_from}.", "kcd"))
                alt = max(d(alt) if alt else ok_from, ok_from).isoformat()
            else:
                R.append(rule(True, "KCD-5", "No list-price change in the 30 days before; keep the price unchanged until 14 days after the deal ends "
                              f"(first allowed change {endx + timedelta(days=KCD_LOCK_AFTER)}).", "kcd"))
            n = book.term_index(day)
            if n is not None:
                ts, te = book.term(n)
                if any(p["type"] == "kcd" and book.term_index(p["start"]) == n for p in book.promos):
                    R.append(rule(False, "KCD-10", f"Already one Countdown Deal in term {n + 1}.", "kcd"))
                if any(p["type"] == "free" and book.term_index(p["start"]) == n for p in book.promos):
                    R.append(rule(False, "PROMO-1", f"Free days already used/booked in term {n + 1}; only one promotion type per term. Next term starts {te}.", "kcd"))
                    alt = alt or te.isoformat()
                limit = te if book.auto_renew else te - timedelta(days=KCD_END_BUFFER)
                if endx > limit:
                    R.append(rule(False, "KCD-9", f"Deal would end after the latest allowed end ({limit}{' - term end' if book.auto_renew else ', 14 days before term end because auto-renew is OFF'}).", "kcd"))
                else:
                    R.append(rule(True, "KCD-9", f"Ends {endx}, within the allowed end ({limit}).", "kcd"))
                tn = book.term_index(today)
                if tn is not None and tn < n:
                    R.append(rule(None, "KCD-11", f"Deal is in a future term ({n + 1}). KDP states the no-future-term limit only for free promos; it may still refuse until {ts}.", "kcd"))
            s = midnight(day, tzp)
            hard = s - timedelta(hours=24)
            safe = midnight(day - timedelta(days=2), tzp)
            if now >= hard:
                R.append(rule(False, "KCD-8", f"Too late: must be scheduled 24h before start ({fmt_pair(hard, tz, tzp, lab)}).", "kcd"))
            elif now >= safe:
                R.append(rule(None, "KCD-8", f"Inside KDP's own example window; hard cutoff {fmt_pair(hard, tz, tzp, lab)}. Schedule immediately.", "kcd"))
            else:
                R.append(rule(True, "KCD-8", f"Schedule before {fmt_pair(safe, tz, tzp, lab)} (hard cutoff {fmt_pair(hard, tz, tzp, lab)}).", "kcd"))
            R.append(rule(True, "KCD-12", f"Runs {fmt_pair(s, tz, tzp, lab)} to {fmt_pair(midnight(endx, tzp), tz, tzp, lab)}.", "kcd"))

    elif action == "bookbub":
        if price is None or book.price is None:
            R.append(rule(False, "BB-1", "Need the deal price and the book's list price.", "bookbub"))
        else:
            if not (price == 0 or price <= book.price * 0.5 + 1e-9):
                R.append(rule(False, "BB-1", f"Deal must be free or at least 50% off (<= {book.price * 0.5:.2f}).", "bookbub"))
            else:
                R.append(rule(True, "BB-1", "Free or at least 50% off.", "bookbub"))
            lower = [p for p in book.promos if p["start"] <= day and p["end"] > day - timedelta(days=30)
                     and (p["type"] == "free" or (p.get("start_price") is not None and p["start_price"] < price))]
            if lower:
                R.append(rule(False, "BB-2", "A lower price (free promo or cheaper Countdown step) ran in the last 30 days.", "bookbub"))
            else:
                R.append(rule(True, "BB-2", "No lower price found in this ledger for the last 30 days (check other stores too).", "bookbub"))
        if book.bookbub:
            last = book.bookbub[-1]
            y, m = last.year + (last.month + 5) // 12, (last.month + 5) % 12 + 1
            try:
                nxt = last.replace(year=y, month=m)
            except ValueError:
                nxt = date(y, m + 1, 1) if m < 12 else date(y + 1, 1, 1)
            if day < nxt:
                R.append(rule(False, "BB-3", f"Same book featured {last}; not again until {nxt} (6 months).", "bookbub"))
                alt = nxt.isoformat()
            else:
                R.append(rule(True, "BB-3", "6+ months since this book's last feature.", "bookbub"))
        for a in sorted(author_bookbub or []):
            a = d(a)
            if a <= day < a + timedelta(days=30):
                R.append(rule(False, "BB-4", f"Author featured {a}; not again until {a + timedelta(days=30)} (30 days).", "bookbub"))
        R.append(rule(None, "BB-5", "Meeting the rules doesn't guarantee selection; length minimums apply (e.g. novels 150+ pages).", "bookbub"))
    else:
        raise SystemExit(f"unknown action {action}")

    if any(r["ok"] is False for r in R):
        ans = "NO"
    elif any(r["ok"] is None for r in R):
        ans = "CHECK"
    else:
        ans = "YES"
    return {"book": book.id, "action": action, "date": day.isoformat(), "answer": ans,
            "alternative": alt, "reasons": R}


# ------------------------------------------------------------------- CLI
def load(path):
    with open(path) as f:
        data = json.load(f)
    return data, [Book(b) for b in data["books"]]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Shelf Clock KDP deadline calculator")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("deadlines")
    a.add_argument("books")
    a.add_argument("--today")
    a.add_argument("--horizon", type=int, default=120)
    a.add_argument("--json", action="store_true")
    b = sub.add_parser("preflight")
    b.add_argument("books")
    b.add_argument("--book", required=True)
    b.add_argument("--action", required=True, choices=["price", "free", "kcd", "bookbub"])
    b.add_argument("--date", required=True)
    b.add_argument("--days", type=int)
    b.add_argument("--price", type=float)
    b.add_argument("--increments", type=int, default=1)
    b.add_argument("--marketplace", default="amazon.com")
    b.add_argument("--now")
    b.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    data, books = load(args.books)
    settings = data.get("settings", {})
    tz = ZoneInfo(settings.get("timezone", DEFAULT_TZ))

    if args.cmd == "deadlines":
        today = d(args.today) if args.today else datetime.now(tz).date()
        out = []
        for bk in books:
            out += deadlines(bk, today, args.horizon, tz, settings.get("safe_buffer_days", 7))
        out.sort(key=lambda x: x["_sort"])
        for x in out:
            x.pop("_sort")
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(f"Shelf Clock deadlines from {today} (+{args.horizon} days), times in {tz.key}")
            for x in out:
                print(f"- {x['display']} | {x['title']} | {x['kind'].upper()}: {x['text']} [{x['rule']}]")
        return 0

    bk = next((x for x in books if x.id == args.book), None)
    if bk is None:
        raise SystemExit(f"no book {args.book}")
    now = datetime.fromisoformat(args.now).replace(tzinfo=tz) if args.now else datetime.now(tz)
    res = preflight(bk, args.action, d(args.date), now, tz, args.days, args.price, args.increments,
                    args.marketplace, data.get("author", {}).get("bookbub_features"))
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"{res['answer']}: {args.action} for {bk.title} on {res['date']}")
        for r in res["reasons"]:
            mark = {True: "ok ", False: "NO ", None: "?? "}[r["ok"]]
            print(f"  {mark}[{r['rule']}] {r['text']}  ({r['source']})")
        if res["alternative"]:
            print(f"  Suggested date: {res['alternative']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
