"""Utility functions for the lazy_log package."""

import re
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import TextIO

from lazy_log.constants import PROG_NAME

FLOAT_FMT_PATTERN = re.compile(r"^([+-]?)(\d+)?(\.\d+)?f$")
INT_FMT_PATTERN = re.compile(r"^([+-]?)(\d+)?d$")
GENERIC_FMT_PATTERN = re.compile(r"^([+-]?)(\d+)?(\.\d+)?[fdsxoe]$")


def python_fmt_to_printf(fmt: str) -> str:
    """Convert a Python format specifier to a printf-style format specifier.

    Args:
        fmt: The Python format specifier string.

    Returns:
        The corresponding printf-style format specifier string.
    """
    fmt = fmt.strip()
    result = "%s"  # Default format

    if fmt in {"", ","}:
        result = "%s"
    elif float_match := FLOAT_FMT_PATTERN.match(fmt):
        sign = float_match.group(1) or ""
        width = float_match.group(2) or ""
        precision = float_match.group(3) or ""
        result = f"%{sign}{width}{precision}f"
    elif int_match := INT_FMT_PATTERN.match(fmt):
        sign = int_match.group(1) or ""
        width = int_match.group(2) or ""
        result = f"%{sign}{width}d"
    elif generic_match := GENERIC_FMT_PATTERN.match(fmt):
        sign = generic_match.group(1) or ""
        width = generic_match.group(2) or ""
        precision = generic_match.group(3) or ""
        typechar = fmt[-1]
        result = f"%{sign}{width}{precision}{typechar}"
    elif fmt.endswith(("d", "f", "s", "x", "o", "e")):
        result = f"%{fmt[-1]}"

    return result


def to_string_literal(value: str) -> str:
    """Render a Python string literal for value, preferring double quotes.

    Uses repr() to produce a correctly escaped literal, then flips the outer
    quotes to double quotes when doing so does not introduce escaping (i.e. when
    the value contains no double quote).

    Args:
        value: The string value to render as a literal.

    Returns:
        A valid Python string literal for value.
    """
    literal = repr(value)
    if literal.startswith("'") and '"' not in value:
        literal = f'"{literal[1:-1]}"'
    return literal


def get_version() -> str:
    """Return installed package version, falling back gracefully when not installed."""
    try:
        return version(PROG_NAME)
    except PackageNotFoundError:
        return "unknown"


def print_with_fallback(message: str, stream: TextIO | None = None) -> None:
    """Print text, degrading safely when the console cannot encode the characters.

    Pre-commit hooks run on consoles with a limited code page (e.g. Windows cp1252),
    where a file path with non-ASCII characters or the status
    emoji would otherwise raise UnicodeEncodeError and abort the commit. When the
    stream cannot encode the message, fall back to writing bytes with unencodable
    characters escaped rather than crashing.

    Args:
        message: The text to print.
        stream: The text stream to write to. Defaults to ``sys.stdout``.
    """
    stream = stream if stream is not None else sys.stdout
    try:
        print(message, file=stream)
    except UnicodeEncodeError:
        encoding = stream.encoding or "utf-8"
        safe_bytes = message.encode(encoding, errors="backslashreplace")
        stream.buffer.write(safe_bytes + b"\n")


def prepare_exclude_patterns(patterns: list[str]) -> list[str]:
    """Normalize user-provided exclude patterns for cross-platform matching."""
    prepared = []
    for pattern in patterns:
        normalized = pattern.replace("\\", "/")
        if normalized.startswith(("**/", "/")) or ":" in normalized:
            prepared.append(normalized)
        else:
            prepared.append(f"**/{normalized}")
    return prepared
