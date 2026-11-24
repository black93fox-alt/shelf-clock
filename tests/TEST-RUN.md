# Test run — 2026-11-24 05:28 CST

```
Python 3.13.5
test_bookbub (tests.test_shelf_clock.EdgeCases.test_bookbub) ... ok
test_dst_fall_back_free_promo (tests.test_shelf_clock.EdgeCases.test_dst_fall_back_free_promo) ... ok
test_dst_preorder_deadlines (tests.test_shelf_clock.EdgeCases.test_dst_preorder_deadlines) ... ok
test_dst_spring_forward_free_promo (tests.test_shelf_clock.EdgeCases.test_dst_spring_forward_free_promo) ... ok
test_free_schedule_cutoff (tests.test_shelf_clock.EdgeCases.test_free_schedule_cutoff) ... ok
test_kcd_booking_too_late (tests.test_shelf_clock.EdgeCases.test_kcd_booking_too_late) ... ok
test_kcd_duration_increments (tests.test_shelf_clock.EdgeCases.test_kcd_duration_increments) ... ok
test_kcd_end_buffer_auto_renew_off (tests.test_shelf_clock.EdgeCases.test_kcd_end_buffer_auto_renew_off) ... ok
test_kcd_price_lock_window (tests.test_shelf_clock.EdgeCases.test_kcd_price_lock_window) ... ok
test_kcd_price_range_and_min_drop (tests.test_shelf_clock.EdgeCases.test_kcd_price_range_and_min_drop) ... ok
test_leap_year_terms (tests.test_shelf_clock.EdgeCases.test_leap_year_terms) ... ok
test_not_in_select (tests.test_shelf_clock.EdgeCases.test_not_in_select) ... ok
test_paperback_release_only (tests.test_shelf_clock.EdgeCases.test_paperback_release_only) ... ok
test_royalty_band_warning (tests.test_shelf_clock.EdgeCases.test_royalty_band_warning) ... ok
test_uk_kcd (tests.test_shelf_clock.EdgeCases.test_uk_kcd) ... ok
test_A_manuscript_deadline_5_days (tests.test_shelf_clock.FiveBooks.test_A_manuscript_deadline_5_days) ... ok
test_A_no_promo_before_release (tests.test_shelf_clock.FiveBooks.test_A_no_promo_before_release) ... ok
test_A_terms_and_windows (tests.test_shelf_clock.FiveBooks.test_A_terms_and_windows) ... ok
test_B_manuscript_deadline_72h (tests.test_shelf_clock.FiveBooks.test_B_manuscript_deadline_72h) ... ok
test_B_term_and_renewal (tests.test_shelf_clock.FiveBooks.test_B_term_and_renewal) ... ok
test_C_kcd_dec4_ok_and_booking_times (tests.test_shelf_clock.FiveBooks.test_C_kcd_dec4_ok_and_booking_times) ... ok
test_C_kcd_too_early (tests.test_shelf_clock.FiveBooks.test_C_kcd_too_early) ... ok
test_D_price_change_blocks_kcd (tests.test_shelf_clock.FiveBooks.test_D_price_change_blocks_kcd) ... ok
test_D_price_drop_side_effect (tests.test_shelf_clock.FiveBooks.test_D_price_drop_side_effect) ... ok
test_D_terms (tests.test_shelf_clock.FiveBooks.test_D_terms) ... ok
test_E_free_day_budget (tests.test_shelf_clock.FiveBooks.test_E_free_day_budget) ... ok
test_E_kcd_blocked_same_term (tests.test_shelf_clock.FiveBooks.test_E_kcd_blocked_same_term) ... ok
test_E_kcd_next_term_flagged (tests.test_shelf_clock.FiveBooks.test_E_kcd_next_term_flagged) ... ok
test_E_term_boundary (tests.test_shelf_clock.FiveBooks.test_E_term_boundary) ... ok
test_example_file_runs (tests.test_shelf_clock.Packaging.test_example_file_runs) ... ok
test_skill_helper_copy_matches (tests.test_shelf_clock.Packaging.test_skill_helper_copy_matches) ... /workspace/ops/shelf-clock/tests/test_shelf_clock.py:245: ResourceWarning: unclosed file <_io.TextIOWrapper name='/workspace/ops/shelf-clock/tests/../calc/shelf_clock.py' mode='r' encoding='UTF-8'>
  a = open(os.path.join(root, "calc", "shelf_clock.py")).read()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
/workspace/ops/shelf-clock/tests/test_shelf_clock.py:246: ResourceWarning: unclosed file <_io.TextIOWrapper name='/workspace/ops/shelf-clock/tests/../skills/deadline-calc/shelf_clock.py' mode='r' encoding='UTF-8'>
  b = open(os.path.join(root, "skills", "deadline-calc", "shelf_clock.py")).read()
ResourceWarning: Enable tracemalloc to get the object allocation traceback
ok

----------------------------------------------------------------------
Ran 31 tests in 0.011s

OK
```

Mutation check (TERM_DAYS=91, first-title window 96h): 9 tests failed, so the tests catch wrong rules.
