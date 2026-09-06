import pytest

from lazy_log.utils import python_fmt_to_printf, to_string_literal


@pytest.mark.parametrize(
    ("input_fmt", "expected"),
    [
        # Test empty and special cases
        ("", "%s"),
        (",", "%s"),
        # Test float format specifiers
        (".2f", "%.2f"),
        ("10.2f", "%10.2f"),
        ("f", "%f"),
        # Test integer format specifiers
        ("d", "%d"),
        ("5d", "%5d"),
        ("+5d", "%+5d"),
        # Test generic format specifiers
        ("10.2s", "%10.2s"),
        ("5x", "%5x"),
        ("o", "%o"),
        ("e", "%e"),
        # Test edge cases
        ("10.2", "%s"),  # No type character
        ("10.2z", "%s"),  # Unsupported type character
        ("+10.2f", "%+10.2f"),  # Float with sign
        ("-10.2d", "%-10.2d"),  # Integer with sign
    ],
)
def test_python_fmt_to_printf(input_fmt, expected):
    actual = python_fmt_to_printf(input_fmt)
    assert actual == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # No quotes in the value: prefer double quotes.
        ("Hello %s", '"Hello %s"'),
        ("", '""'),
        # Value contains a double quote but no single quote: keep single quotes
        # to avoid escaping.
        ('He said "%s"', "'He said \"%s\"'"),
        # Value contains a single quote but no double quote: repr already uses
        # double quotes.
        ("He said '%s'", "\"He said '%s'\""),
        # Non-ASCII characters are preserved, not escaped.
        ("Temp %.2f°C", '"Temp %.2f°C"'),
    ],
)
def test_to_string_literal(value, expected):
    literal = to_string_literal(value)
    assert literal == expected
    # The literal must round-trip back to the original value.
    assert eval(literal) == value  # ruff: ignore[suspicious-eval-usage]
