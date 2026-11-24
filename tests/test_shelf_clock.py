"""Shelf Clock tests. Every expected value below was worked out by hand
(see HAND-WORKED.md) before running the code. Run:
    python3 -m unittest -v tests/test_shelf_clock.py   (from the template root)
"""
import json
import os
import sys
import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "calc"))
import shelf_clock as sc  # noqa: E402

CT = ZoneInfo("America/Chicago")
with open(os.path.join(HERE, "fixtures.json")) as f:
    DATA = json.load(f)
BOOKS = {b["id"]: sc.Book(b) for b in DATA["books"]}


def ev(book_id, today, horizon=400, kind=None, contains=None):
    out = sc.deadlines(BOOKS[book_id], date.fromisoformat(today), horizon, CT)
    if kind:
        out = [e for e in out if e["kind"] == kind]
    if contains:
        out = [e for e in out if contains in e["text"]]
    return out


def ct(e):
    return e["_sort"].astimezone(CT).strftime("%Y-%m-%d %H:%M %Z")


def pf(book_id, action, day, now="2026-11-24 09:00", **kw):
    return sc.preflight(BOOKS[book_id], action, date.fromisoformat(day),
                        datetime.fromisoformat(now).replace(tzinfo=CT), CT, **kw)


def failed(res):
    return {r["rule"] for r in res["reasons"] if r["ok"] is False}


class FiveBooks(unittest.TestCase):
    # ---- Book A: first-ever title, 5-day rule, auto-renew OFF
    def test_A_manuscript_deadline_5_days(self):
        e = ev("A", "2026-11-24", kind="deadline", contains="Final manuscript")[0]
        self.assertEqual(ct(e), "2027-03-10 18:00 CST")  # Mar 11 00:00 UTC
        self.assertEqual(e["rule"], "PO-4")

    def test_A_terms_and_windows(self):
        self.assertEqual(BOOKS["A"].select_start, date(2027, 3, 16))  # PO-8
        self.assertEqual(BOOKS["A"].term(0), (date(2027, 3, 16), date(2027, 6, 14)))
        free = ev("A", "2026-11-24", contains="Earliest Free")[0]
        self.assertEqual(ct(free), "2027-03-17 02:00 CDT")
        kcd = ev("A", "2026-11-24", contains="Earliest Countdown")[0]
        self.assertEqual(kcd["when"][:10], "2027-04-15")
        last = ev("A", "2026-11-24", contains="Latest moment")[0]
        self.assertEqual(last["when"][:10], "2027-05-31")  # 14 days before Jun 14, auto-renew off

    def test_A_no_promo_before_release(self):
        r = pf("A", "free", "2027-03-10", days=2)  # before release -> NO
        self.assertEqual(r["answer"], "NO")
        self.assertIn("PO-8", failed(r))
        r = pf("A", "free", "2027-03-20", days=2)  # after release, but asked pre-release -> CHECK
        self.assertEqual(r["answer"], "CHECK")
        self.assertTrue(any(x["rule"] == "PO-8" and x["ok"] is None for x in r["reasons"]))

    # ---- Book B: returning author pre-order (72h, UTC basis)
    def test_B_manuscript_deadline_72h(self):
        e = ev("B", "2026-11-24", kind="deadline", contains="Final manuscript")[0]
        self.assertEqual(ct(e), "2027-02-19 18:00 CST")  # = KDP timer "before Feb 19 11:59 PM GMT"
        t = ev("B", "2026-11-24", kind="target")[0]
        self.assertEqual(ct(t), "2027-02-12 18:00 CST")

    def test_B_term_and_renewal(self):
        self.assertEqual(BOOKS["B"].term(0), (date(2027, 2, 23), date(2027, 5, 24)))
        alert = ev("B", "2026-11-24", kind="alert")[0]
        self.assertEqual(alert["when"], "2027-05-13")
        renew = ev("B", "2026-11-24", contains="Auto-renews into term 2")[0]
        self.assertEqual(ct(renew), "2027-05-24 02:00 CDT")
        self.assertEqual(ev("B", "2026-11-24", contains="Earliest Countdown")[0]["when"][:10], "2027-03-25")

    # ---- Book C: Select day 20 -> KCD not yet allowed
    def test_C_kcd_too_early(self):
        r = pf("C", "kcd", "2026-11-24", days=7, price=1.99)
        self.assertEqual(r["answer"], "NO")
        self.assertIn("KCD-2", failed(r))
        self.assertEqual(r["alternative"], "2026-12-04")

    def test_C_kcd_dec4_ok_and_booking_times(self):
        r = pf("C", "kcd", "2026-12-04", days=7, price=1.99)
        self.assertEqual(r["answer"], "YES")
        k8 = [x for x in r["reasons"] if x["rule"] == "KCD-8"][0]["text"]
        self.assertIn("Wed Dec 02 2026 02:00 AM CST", k8)  # safe: Dec 2 00:00 PT
        self.assertIn("Thu Dec 03 2026 02:00 AM CST", k8)  # hard: Dec 3 00:00 PT
        self.assertEqual(BOOKS["C"].term(0)[1], date(2027, 2, 2))

    # ---- Book D: recent price change blocks KCD
    def test_D_price_change_blocks_kcd(self):
        r = pf("D", "kcd", "2026-11-30", days=7, price=1.99)
        self.assertEqual(r["answer"], "NO")
        self.assertIn("KCD-5", failed(r))
        self.assertEqual(r["alternative"], "2026-12-10")
        self.assertEqual(pf("D", "kcd", "2026-12-10", days=7, price=1.99)["answer"], "YES")

    def test_D_terms(self):
        self.assertEqual(BOOKS["D"].term(1), (date(2026, 10, 30), date(2027, 1, 28)))

    def test_D_price_drop_side_effect(self):
        r = pf("D", "price", "2026-12-01", price=3.99)
        self.assertEqual(r["answer"], "YES")
        self.assertTrue(any("2026-12-31" in x["text"] for x in r["reasons"]))

    # ---- Book E: free days used this term
    def test_E_kcd_blocked_same_term(self):
        r = pf("E", "kcd", "2026-12-01", days=7, price=1.99)
        self.assertEqual(r["answer"], "NO")
        self.assertIn("PROMO-1", failed(r))
        self.assertEqual(r["alternative"], "2026-12-11")

    def test_E_free_day_budget(self):
        self.assertEqual(pf("E", "free", "2026-12-05", days=4)["answer"], "NO")
        self.assertEqual(pf("E", "free", "2026-12-05", days=3)["answer"], "YES")

    def test_E_term_boundary(self):
        self.assertEqual(BOOKS["E"].term(1), (date(2026, 12, 11), date(2027, 3, 11)))
        r = pf("E", "free", "2026-12-10", days=2)  # Dec 10-11 crosses into term 2
        self.assertIn("FREE-5", failed(r))
        r = pf("E", "free", "2026-12-11", days=1, now="2026-12-11 09:00")  # term-2 day 1
        self.assertIn("FREE-3", failed(r))
        self.assertEqual(r["alternative"], "2026-12-12")
        r = pf("E", "free", "2026-12-12", days=1)  # future term, scheduled from term 1
        self.assertIn("FREE-7", failed(r))

    def test_E_kcd_next_term_flagged(self):
        r = pf("E", "kcd", "2026-12-11", days=7, price=1.99)
        self.assertEqual(r["answer"], "CHECK")  # only the future-term caveat


class EdgeCases(unittest.TestCase):
    def test_leap_year_terms(self):
        self.assertEqual(BOOKS["L1"].term(1)[0], date(2028, 4, 14))
        self.assertEqual(BOOKS["L2"].term(1)[0], date(2027, 4, 15))
        self.assertEqual(BOOKS["L3"].term(1)[0], date(2028, 5, 29))

    def test_dst_spring_forward_free_promo(self):
        # midnight PT on Sun Mar 14 2027 = 08:00 UTC = 3:00 AM CDT
        r = pf("L2", "free", "2027-03-14", days=1, now="2027-03-01 09:00")
        txt = [x for x in r["reasons"] if x["rule"] == "FREE-8"][0]["text"]
        self.assertIn("Sun Mar 14 2027 03:00 AM CDT", txt)

    def test_dst_fall_back_free_promo(self):
        # midnight PT on Sun Nov 1 2026 = 07:00 UTC = 1:00 AM CST
        r = pf("E", "free", "2026-11-01", days=1, now="2026-10-20 09:00")
        txt = [x for x in r["reasons"] if x["rule"] == "FREE-8"][0]["text"]
        self.assertIn("Sun Nov 01 2026 01:00 AM CST", txt)

    def test_dst_preorder_deadlines(self):
        g = lambda i: ct(ev(i, "2026-11-24", kind="deadline", contains="Final manuscript")[0])
        self.assertEqual(g("S1"), "2027-03-12 18:00 CST")
        self.assertEqual(g("S2"), "2027-03-13 18:00 CST")
        self.assertEqual(g("S3"), "2027-03-14 19:00 CDT")

    def test_kcd_price_range_and_min_drop(self):
        b = sc.Book({"id": "x", "release_date": "2026-01-01", "select": {"enrolled": True, "start": "2026-01-01"}, "list_price": 2.98})
        r = sc.preflight(b, "kcd", date(2026, 12, 20), datetime(2026, 11, 24, 9, tzinfo=CT), CT, days=7, price=0.99)
        self.assertIn("KCD-3", failed(r))
        for p, ok in [(2.99, True), (24.99, True), (25.00, False)]:
            b = sc.Book({"id": "x", "release_date": "2026-01-01", "select": {"enrolled": True, "start": "2026-01-01"}, "list_price": p})
            r = sc.preflight(b, "kcd", date(2026, 12, 20), datetime(2026, 11, 24, 9, tzinfo=CT), CT, days=7, price=p - 1.0)
            self.assertEqual("KCD-3" not in failed(r), ok, p)
        r = pf("C", "kcd", "2026-12-04", days=7, price=4.00)  # only $0.99 off
        self.assertIn("KCD-4", failed(r))

    def test_kcd_duration_increments(self):
        self.assertIn("KCD-7", failed(pf("C", "kcd", "2026-12-04", days=8, price=1.99)))
        self.assertIn("KCD-6", failed(pf("C", "kcd", "2026-12-04", days=7, price=1.99, increments=6)))

    def test_kcd_end_buffer_auto_renew_off(self):
        # G: term 1 Oct 1 2026 - Dec 30 2026 (exclusive), auto-renew off -> latest end Dec 16
        self.assertEqual(BOOKS["G"].term(0)[1], date(2026, 12, 30))
        g2 = sc.Book({**BOOKS["G"].raw, "promos": []})
        r = sc.preflight(g2, "kcd", date(2026, 12, 10), datetime(2026, 11, 24, 9, tzinfo=CT), CT, days=7, price=1.99)
        self.assertIn("KCD-9", failed(r))  # ends Dec 17 > Dec 16
        r = sc.preflight(g2, "kcd", date(2026, 12, 9), datetime(2026, 11, 24, 9, tzinfo=CT), CT, days=7, price=1.99)
        self.assertNotIn("KCD-9", failed(r))  # ends Dec 16

    def test_kcd_price_lock_window(self):
        # G KCD Jan 5-12 2027 (end exclusive): lock Dec 6 2026 .. Jan 25 2027, first change Jan 26
        self.assertIn("KCD-5", failed(pf("G", "price", "2026-12-06", price=3.99)))
        self.assertIn("KCD-5", failed(pf("G", "price", "2027-01-25", price=3.99)))
        self.assertEqual(pf("G", "price", "2026-12-05", price=3.99)["answer"], "YES")
        self.assertEqual(pf("G", "price", "2027-01-26", price=3.99)["answer"], "YES")
        lock = ev("G", "2026-11-24", kind="lock")
        self.assertEqual([e["when"] for e in lock], ["2026-12-06", "2027-01-26"])

    def test_kcd_booking_too_late(self):
        r = pf("C", "kcd", "2026-12-04", days=7, price=1.99, now="2026-12-03 03:00")  # after Dec 3 2 AM CST
        self.assertIn("KCD-8", failed(r))
        r = pf("C", "kcd", "2026-12-04", days=7, price=1.99, now="2026-12-02 12:00")
        self.assertEqual(r["answer"], "CHECK")

    def test_uk_kcd(self):
        r = pf("U", "kcd", "2026-12-20", days=3, price=0.99, marketplace="amazon.co.uk")
        self.assertNotIn("KCD-3", failed(r))
        txt = [x for x in r["reasons"] if x["rule"] == "KCD-12"][0]["text"]
        self.assertIn("Sat Dec 19 2026 06:00 PM CST", txt)  # 00:00 GMT Dec 20

    def test_not_in_select(self):
        self.assertIn("FREE-2", failed(pf("F", "free", "2026-12-05", days=1)))
        self.assertIn("KCD-1", failed(pf("F", "kcd", "2026-12-05", days=1, price=1.99)))

    def test_royalty_band_warning(self):
        r = pf("F", "price", "2026-12-05", price=1.99)
        self.assertEqual(r["answer"], "CHECK")
        self.assertEqual(pf("F", "price", "2026-12-05", price=12.99)["answer"], "YES")

    def test_paperback_release_only(self):
        e = ev("P", "2026-11-24")
        self.assertEqual([x["kind"] for x in e], ["release"])

    def test_free_schedule_cutoff(self):
        r = pf("E", "free", "2026-11-26", days=1, now="2026-11-25 21:30")  # 7:30 PM PT -> ok
        self.assertNotIn("FREE-4", failed(r))
        r = pf("E", "free", "2026-11-26", days=1, now="2026-11-25 22:30")  # 8:30 PM PT -> CHECK
        self.assertEqual(r["answer"], "CHECK")
        r = pf("E", "free", "2026-11-26", days=1, now="2026-11-26 02:30")  # after midnight PT
        self.assertIn("FREE-4", failed(r))

    def test_bookbub(self):
        r = pf("E", "bookbub", "2026-12-20", price=0.99)  # free promo Nov 20-21 within 30 days
        self.assertIn("BB-2", failed(r))
        self.assertIn("BB-3", failed(r))  # Jul 15 + 6 months = Jan 15 2027
        self.assertEqual(r["alternative"], "2027-01-15")
        r = pf("C", "bookbub", "2026-12-01", price=0.99, author_bookbub=["2026-11-10"])
        self.assertIn("BB-4", failed(r))  # until Dec 10
        r = pf("C", "bookbub", "2026-12-10", price=2.50, author_bookbub=["2026-11-10"])
        self.assertIn("BB-1", failed(r))  # 2.50 > 4.99/2


class Packaging(unittest.TestCase):
    def test_skill_helper_copy_matches(self):
        root = os.path.join(HERE, "..")
        a = open(os.path.join(root, "calc", "shelf_clock.py")).read()
        b = open(os.path.join(root, "skills", "deadline-calc", "shelf_clock.py")).read()
        self.assertEqual(a, b, "skills/deadline-calc/shelf_clock.py is out of sync with calc/shelf_clock.py")

    def test_example_file_runs(self):
        root = os.path.join(HERE, "..")
        with open(os.path.join(root, "examples", "books.example.json")) as f:
            books = [sc.Book(b) for b in json.load(f)["books"]]
        out = sum((sc.deadlines(b, date(2026, 11, 24), 120, CT) for b in books), [])
        self.assertTrue(any(e["rule"] == "PO-3" for e in out))


if __name__ == "__main__":
    unittest.main(verbosity=2)
