"""
Unit tests for utility functions using property-based testing.
"""

from hypothesis import given, strategies as st
from hypothesis.extra.datetime import datetimes
from datetime import datetime, timezone


def test_format_duration():
    """Test the format_duration utility function."""
    from src.utils.time_utils import format_duration

    # Test with exact seconds
    assert format_duration(90) == "01:30"
    assert format_duration(3600) == "01:00:00"
    assert format_duration(3665) == "01:01:05"

    # Test edge cases
    assert format_duration(0) == "00:00"
    assert format_duration(59) == "00:59"


def test_parse_timestamp():
    """Test the parse_timestamp utility function."""
    from src.utils.time_utils import parse_timestamp

    # Test with valid timestamps
    assert parse_timestamp("2023-01-01T00:00:00Z") == datetime(
        2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc
    )

    # Test with invalid timestamps
    with pytest.raises(ValueError):
        parse_timestamp("invalid-timestamp")


# Property-based test for duration formatting
@given(st.integers(min_value=0, max_value=86400))  # Up to 24 hours
def test_format_duration_property(seconds):
    """Property-based test for format_duration function."""
    from src.utils.time_utils import format_duration

    result = format_duration(seconds)

    # Verify the format is either MM:SS or HH:MM:SS
    parts = result.split(":")
    if len(parts) == 2:
        # MM:SS format
        minutes, seconds = map(int, parts)
        assert 0 <= minutes < 60
        assert 0 <= seconds < 60
    else:
        # HH:MM:SS format
        hours, minutes, seconds = map(int, parts)
        assert hours >= 0
        assert 0 <= minutes < 60
        assert 0 <= seconds < 60
