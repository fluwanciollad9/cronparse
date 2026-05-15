"""Tests for cronparse.pipeline."""

from cronparse.pipeline import Pipeline, PipelineResult


EXPRS = [
    "0 * * * *",    # hourly
    "0 0 * * *",    # daily midnight
    "*/5 * * * *",  # every 5 min
    "0 12 * * 1",   # monday noon
    "0 0 1 * *",    # monthly
]


# ---------------------------------------------------------------------------
# PipelineResult helpers
# ---------------------------------------------------------------------------

def test_pipeline_result_output_count():
    pr = PipelineResult(output=["a", "b"], dropped=["c"])
    assert pr.output_count == 2
    assert pr.dropped_count == 1


# ---------------------------------------------------------------------------
# Pipeline execution
# ---------------------------------------------------------------------------

def test_pipeline_no_steps_returns_all():
    result = Pipeline().run(EXPRS)
    assert result.output_count == len(EXPRS)
    assert result.dropped_count == 0


def test_pipeline_filter_field_minute_zero():
    result = Pipeline().filter_field("minute", "0").run(EXPRS)
    assert all(e.startswith("0 ") for e in result.output)
    assert "*/5 * * * *" in result.dropped


def test_pipeline_filter_field_hour_wildcard():
    result = Pipeline().filter_field("hour", "*").run(EXPRS)
    assert "0 * * * *" in result.output
    assert "*/5 * * * *" in result.output
    assert "0 0 * * *" in result.dropped


def test_pipeline_filter_tag_hourly():
    result = Pipeline().filter_tag("hourly").run(EXPRS)
    assert "0 * * * *" in result.output


def test_pipeline_filter_tag_daily():
    result = Pipeline().filter_tag("daily").run(EXPRS)
    assert "0 0 * * *" in result.output


def test_pipeline_filter_predicate():
    result = Pipeline().filter_predicate(lambda e: e.dow != "*").run(EXPRS)
    assert "0 12 * * 1" in result.output
    assert result.output_count == 1


def test_pipeline_chained_steps_reduce_set():
    result = (
        Pipeline()
        .filter_field("minute", "0")
        .filter_field("hour", "0")
        .run(EXPRS)
    )
    # Only expressions with minute=0 AND hour=0 survive
    for expr in result.output:
        parts = expr.split()
        assert parts[0] == "0"
        assert parts[1] == "0"


def test_pipeline_normalize_step_does_not_crash():
    result = Pipeline().normalize().filter_field("minute", "0").run(["0 * * * *"])
    assert result.output_count == 1


def test_pipeline_invalid_expression_in_errors():
    result = Pipeline().filter_field("minute", "0").run(["not valid", "0 * * * *"])
    assert result.error_count == 1
    assert "0 * * * *" in result.output


def test_pipeline_dropped_accumulates_across_steps():
    exprs = ["0 * * * *", "*/5 * * * *", "0 0 * * *", "0 12 * * *"]
    result = (
        Pipeline()
        .filter_field("minute", "0")   # drops */5 * * * *
        .filter_field("hour", "0")     # drops 0 * * * * and 0 12 * * *
        .run(exprs)
    )
    assert "*/5 * * * *" in result.dropped
    assert "0 * * * *" in result.dropped
    assert "0 12 * * *" in result.dropped
    assert result.output == ["0 0 * * *"]
