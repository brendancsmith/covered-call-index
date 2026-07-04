"""Fetch YieldMax option-income ETF data and generate reports."""

from __future__ import annotations

from .fetch import EtfDataError, build_record, fetch_etf, fetch_etfs
from .models import DEFAULT_TICKERS, EtfRecord
from .reports import (
    render_text,
    to_dataframe,
    write_excel_report,
    write_json_report,
    write_text_report,
)

__all__ = [
    "DEFAULT_TICKERS",
    "EtfDataError",
    "EtfRecord",
    "build_record",
    "fetch_etf",
    "fetch_etfs",
    "render_text",
    "to_dataframe",
    "write_excel_report",
    "write_json_report",
    "write_text_report",
]
