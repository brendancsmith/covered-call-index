"""Fetch YieldMax ETF data from Yahoo Finance via ``yfinance``.

The network-touching entry points (:func:`fetch_etf`, :func:`fetch_etfs`) are
thin wrappers around :func:`build_record`, a pure function that turns the raw
``yfinance`` fields into an :class:`~covered_call_index.models.EtfRecord`. Keep
parsing logic in the pure layer so it can be unit-tested without a network.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime, timedelta

import yfinance as yf

from .models import EtfRecord


class EtfDataError(RuntimeError):
    """Raised when a ticker's data is missing or unusable."""


def fetch_etf(ticker: str) -> EtfRecord:
    """Fetch one ticker from Yahoo Finance and build its record.

    Hits the network. Raises :class:`EtfDataError` when the returned data is
    missing required fields.
    """
    yf_ticker = yf.Ticker(ticker)
    info = dict(yf_ticker.info or {})
    distributions = [
        (_to_date(timestamp), float(amount))
        for timestamp, amount in yf_ticker.dividends.items()
    ]
    return build_record(ticker, info, distributions)


def fetch_etfs(
    tickers: Sequence[str],
) -> tuple[list[EtfRecord], dict[str, str]]:
    """Fetch many tickers.

    Returns ``(records, errors)`` where ``errors`` maps each failed ticker to
    its error message. Failures are surfaced, never swallowed silently.
    """
    records: list[EtfRecord] = []
    errors: dict[str, str] = {}
    for ticker in tickers:
        try:
            records.append(fetch_etf(ticker))
        except Exception as exc:  # noqa: BLE001 - reported per ticker, not swallowed
            errors[ticker] = f"{type(exc).__name__}: {exc}"
    return records, errors


def build_record(
    ticker: str,
    info: Mapping[str, object],
    distributions: Sequence[tuple[date, float]],
    *,
    asof: date | None = None,
) -> EtfRecord:
    """Build an :class:`EtfRecord` from raw ``yfinance`` fields.

    Pure and network-free so it can be exercised directly in tests.
    """
    name = _require_str(info, "longName", ticker)
    nav = _require_positive_float(info, "navPrice", ticker)
    asof = asof or datetime.now(UTC).date()
    return EtfRecord(
        ticker=ticker.upper(),
        name=name,
        strategy=strategy_from_name(name),
        distribution_yield_pct=trailing_twelve_month_yield_pct(
            distributions, nav, asof=asof
        ),
        nav=nav,
        inception_date=_inception_date(info, ticker),
        expense_ratio_pct=_require_float(info, "netExpenseRatio", ticker),
    )


def trailing_twelve_month_yield_pct(
    distributions: Sequence[tuple[date, float]],
    nav: float,
    *,
    asof: date,
) -> float:
    """Sum of distributions in the trailing 12 months over NAV, as a percent."""
    if nav <= 0:
        raise EtfDataError(f"NAV must be positive to compute a yield, got {nav!r}")
    cutoff = asof - timedelta(days=365)
    ttm = sum(amount for when, amount in distributions if cutoff < when <= asof)
    return round(ttm / nav * 100, 2)


def strategy_from_name(name: str) -> str:
    """Derive a short strategy label from the fund's long name.

    ``"YieldMax TSLA Option Income Strategy ETF"`` -> ``"TSLA Option Income
    Strategy"``.
    """
    return name.removeprefix("YieldMax ").removesuffix(" ETF").strip()


def _to_date(value: object) -> date:
    """Coerce a pandas dividend-index label to a plain :class:`date`."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raise EtfDataError(f"unexpected distribution timestamp: {value!r}")


def _require_str(info: Mapping[str, object], key: str, ticker: str) -> str:
    value = info.get(key)
    if not isinstance(value, str) or not value:
        raise EtfDataError(f"{ticker}: missing or empty {key!r}")
    return value


def _require_float(info: Mapping[str, object], key: str, ticker: str) -> float:
    value = info.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise EtfDataError(f"{ticker}: missing or non-numeric {key!r}")
    return float(value)


def _require_positive_float(info: Mapping[str, object], key: str, ticker: str) -> float:
    value = _require_float(info, key, ticker)
    if value <= 0:
        raise EtfDataError(f"{ticker}: {key!r} must be positive, got {value!r}")
    return value


def _inception_date(info: Mapping[str, object], ticker: str) -> date:
    value = info.get("fundInceptionDate")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise EtfDataError(f"{ticker}: missing or non-numeric 'fundInceptionDate'")
    return datetime.fromtimestamp(value, UTC).date()
