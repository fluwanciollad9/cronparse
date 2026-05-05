"""Tests for cronparse.schedule module."""

from datetime import datetime

import pytest

from cronparse.schedule import _expand_field, next_run, next_n_runs


# ---------------------------------------------------------------------------
# _expand_field helpers
# ---------------------------------------------------------------------------

def test_expand_wildcard():
    assert _expand_field("*", 0, 4) == [0, 1, 2, 3, 4]


def test_expand_specific_value():
    assert _expand_field("3", 0, 59) == [3]


def test_expand_range():
    assert _expand_field("1-3", 0, 59) == [1, 2, 3]


def test_expand_step():
    assert _expand_field("*/15", 0, 59) == [0, 15, 30, 45]


def test_expand_list():
    assert _expand_field("0,15,30", 0, 59) == [0, 15, 30]


def test_expand_range_with_step():
    assert _expand_field("0-30/10", 0, 59) == [0, 10, 20, 30]


# ---------------------------------------------------------------------------
# next_run
# ---------------------------------------------------------------------------

BASE = datetime(2024, 1, 15, 10, 0)  # Monday 10:00


def test_next_run_every_minute():
    nxt = next_run("* * * * *", after=BASE)
    assert nxt == datetime(2024, 1, 15, 10, 1)


def test_next_run_specific_minute():
    nxt = next_run("30 * * * *", after=BASE)
    assert nxt == datetime(2024, 1, 15, 10, 30)


def test_next_run_next_hour_when_minute_passed():
    after = datetime(2024, 1, 15, 10, 45)
    nxt = next_run("30 * * * *", after=after)
    assert nxt == datetime(2024, 1, 15, 11, 30)


def test_next_run_specific_hour_and_minute():
    nxt = next_run("0 9 * * *", after=BASE)
    # 10:00 has passed 09:00, so next is tomorrow
    assert nxt == datetime(2024, 1, 16, 9, 0)


def test_next_run_crosses_day_boundary():
    after = datetime(2024, 1, 15, 23, 55)
    nxt = next_run("0 0 * * *", after=after)
    assert nxt == datetime(2024, 1, 16, 0, 0)


def test_next_run_specific_dom():
    # Next 1st of month at midnight
    after = datetime(2024, 1, 15, 0, 0)
    nxt = next_run("0 0 1 * *", after=after)
    assert nxt == datetime(2024, 2, 1, 0, 0)


def test_next_run_step_expression():
    after = datetime(2024, 1, 15, 10, 0)
    nxt = next_run("*/15 * * * *", after=after)
    assert nxt == datetime(2024, 1, 15, 10, 15)


def test_next_run_advances_past_current_minute():
    # Even if current minute matches, must advance at least one minute
    after = datetime(2024, 1, 15, 10, 0)
    nxt = next_run("0 10 * * *", after=after)
    # 10:00 is the current moment; next is tomorrow
    assert nxt == datetime(2024, 1, 16, 10, 0)


# ---------------------------------------------------------------------------
# next_n_runs
# ---------------------------------------------------------------------------

def test_next_n_runs_returns_correct_count():
    runs = next_n_runs("0 * * * *", n=3, after=BASE)
    assert len(runs) == 3


def test_next_n_runs_are_strictly_increasing():
    runs = next_n_runs("*/10 * * * *", n=5, after=BASE)
    for a, b in zip(runs, runs[1:]):
        assert b > a


def test_next_n_runs_hourly():
    runs = next_n_runs("0 * * * *", n=3, after=BASE)
    assert runs[0] == datetime(2024, 1, 15, 11, 0)
    assert runs[1] == datetime(2024, 1, 15, 12, 0)
    assert runs[2] == datetime(2024, 1, 15, 13, 0)
