"""Tests for cronparse.forecaster."""

from datetime import datetime

import pytest

from cronparse.forecaster import ExpressionForecast, ForecastResult, forecast

# Fixed reference point so tests are deterministic
REF = datetime(2024, 1, 15, 12, 0, 0)


# ---------------------------------------------------------------------------
# ForecastResult helpers
# ---------------------------------------------------------------------------

def test_forecast_returns_forecast_result():
    result = forecast(["* * * * *"], n=3, after=REF)
    assert isinstance(result, ForecastResult)


def test_forecast_result_contains_one_forecast_per_expression():
    result = forecast(["* * * * *", "0 * * * *"], n=3, after=REF)
    assert len(result.forecasts) == 2


def test_forecast_valid_count():
    result = forecast(["* * * * *", "bad expr"], n=2, after=REF)
    assert result.valid_count == 1


def test_forecast_error_count():
    result = forecast(["* * * * *", "bad expr"], n=2, after=REF)
    assert result.error_count == 1


def test_forecast_str_contains_expression():
    result = forecast(["0 0 * * *"], n=2, after=REF)
    assert "0 0 * * *" in str(result)


# ---------------------------------------------------------------------------
# ExpressionForecast
# ---------------------------------------------------------------------------

def test_expression_forecast_valid_when_no_error():
    ef = ExpressionForecast(expression="* * * * *", runs=[])
    assert ef.valid is True


def test_expression_forecast_invalid_when_error_set():
    ef = ExpressionForecast(expression="bad", error="parse error")
    assert ef.valid is False


def test_expression_forecast_str_shows_error():
    ef = ExpressionForecast(expression="bad", error="oops")
    assert "ERROR" in str(ef)
    assert "oops" in str(ef)


def test_expression_forecast_str_shows_runs():
    runs = [datetime(2024, 1, 15, 12, 1), datetime(2024, 1, 15, 12, 2)]
    ef = ExpressionForecast(expression="* * * * *", runs=runs)
    text = str(ef)
    assert "2024-01-15 12:01" in text
    assert "2024-01-15 12:02" in text


# ---------------------------------------------------------------------------
# Functional: correct number of runs
# ---------------------------------------------------------------------------

def test_forecast_n_runs_returned():
    result = forecast(["* * * * *"], n=5, after=REF)
    assert len(result.forecasts[0].runs) == 5


def test_forecast_runs_are_datetimes():
    result = forecast(["0 9 * * 1"], n=3, after=REF)
    for run in result.forecasts[0].runs:
        assert isinstance(run, datetime)


def test_forecast_runs_are_in_ascending_order():
    result = forecast(["*/15 * * * *"], n=4, after=REF)
    runs = result.forecasts[0].runs
    assert runs == sorted(runs)


def test_forecast_runs_are_after_reference_time():
    result = forecast(["0 0 * * *"], n=3, after=REF)
    for run in result.forecasts[0].runs:
        assert run > REF


def test_forecast_invalid_expression_captured_as_error():
    result = forecast(["99 99 99 99 99"], n=3, after=REF)
    fc = result.forecasts[0]
    assert not fc.valid
    assert fc.error is not None


def test_forecast_empty_list_returns_empty_result():
    result = forecast([], n=5, after=REF)
    assert result.forecasts == []
    assert result.valid_count == 0
    assert result.error_count == 0


def test_forecast_default_n_is_five():
    result = forecast(["* * * * *"], after=REF)
    assert result.n == 5
    assert len(result.forecasts[0].runs) == 5
