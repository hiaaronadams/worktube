from datetime import date

from worktube.normalize import (
    clean_text,
    normalize_currency,
    parse_date,
    parse_money,
    sha256,
)


def test_clean_text_strips_html_and_whitespace():
    assert clean_text("<p>Hello   world</p>\n") == "Hello world"
    assert clean_text("   ") is None
    assert clean_text(None) is None


def test_parse_date_handles_various_formats():
    assert parse_date("2026-07-01") == date(2026, 7, 1)
    assert parse_date("07/01/2026") == date(2026, 7, 1)
    assert parse_date("July 1, 2026") == date(2026, 7, 1)
    assert parse_date("") is None
    assert parse_date("not a date") is None


def test_normalize_currency():
    assert normalize_currency("$") == "USD"
    assert normalize_currency("eur") == "EUR"
    assert normalize_currency("CAD") == "CAD"
    assert normalize_currency("") is None


def test_parse_money():
    assert parse_money("$1,200,000") == 1200000.0
    assert parse_money(50000) == 50000.0
    assert parse_money(None) is None
    assert parse_money("n/a") is None


def test_sha256_stable_and_case_insensitive():
    assert sha256("A", "b") == sha256("a ", " B")
