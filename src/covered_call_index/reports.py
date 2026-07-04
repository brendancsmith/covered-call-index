"""Render ETF records into text, JSON, and Excel reports.

DataFrame work uses polars; the Excel writer uses ``xlsxwriter`` under polars'
:meth:`polars.DataFrame.write_excel`.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

import polars as pl
from xlsxwriter import Workbook

from .models import EtfRecord

_COLUMN_ORDER = (
    "ticker",
    "name",
    "strategy",
    "distribution_yield_pct",
    "nav",
    "inception_date",
    "expense_ratio_pct",
)


def to_dataframe(records: Sequence[EtfRecord]) -> pl.DataFrame:
    """Build a polars DataFrame from ETF records, columns in report order."""
    frame = pl.DataFrame([record.as_dict() for record in records])
    if frame.is_empty():
        return frame
    return frame.select(_COLUMN_ORDER)


def summary_frame(frame: pl.DataFrame) -> pl.DataFrame:
    """Aggregate headline statistics across all ETFs (single-row frame)."""
    return frame.select(
        pl.len().alias("total_etfs"),
        pl.col("distribution_yield_pct").mean().round(2).alias("avg_yield_pct"),
        pl.col("distribution_yield_pct").max().alias("max_yield_pct"),
        pl.col("distribution_yield_pct").min().alias("min_yield_pct"),
    )


def _summary_metric_value(frame: pl.DataFrame, generated_at: datetime) -> pl.DataFrame:
    stats = summary_frame(frame).to_dicts()[0]
    return pl.DataFrame(
        {
            "Metric": [
                "Total ETFs",
                "Average Distribution Yield (%)",
                "Highest Distribution Yield (%)",
                "Lowest Distribution Yield (%)",
                "Report Generated",
            ],
            "Value": [
                str(stats["total_etfs"]),
                f"{stats['avg_yield_pct']:.2f}",
                f"{stats['max_yield_pct']:.2f}",
                f"{stats['min_yield_pct']:.2f}",
                generated_at.strftime("%Y-%m-%d %H:%M:%S %Z"),
            ],
        }
    )


def render_text(
    records: Sequence[EtfRecord], *, generated_at: datetime | None = None
) -> str:
    """Render a human-readable text report."""
    generated_at = generated_at or datetime.now(UTC)
    rule = "=" * 80
    lines = [
        rule,
        "YIELDMAX ETF DATA REPORT",
        f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M:%S %Z')}",
        rule,
        "",
        f"Total ETFs: {len(records)}",
    ]
    for index, etf in enumerate(records, start=1):
        lines += [
            "",
            f"{index}. {etf.ticker} - {etf.name}",
            "-" * 40,
            f"  Strategy: {etf.strategy}",
            f"  Distribution Yield (TTM): {etf.distribution_yield_pct:.2f}%",
            f"  NAV: ${etf.nav:.2f}",
            f"  Inception Date: {etf.inception_date.isoformat()}",
            f"  Expense Ratio: {etf.expense_ratio_pct:.2f}%",
        ]

    if records:
        stats = summary_frame(to_dataframe(records)).to_dicts()[0]
        lines += [
            "",
            rule,
            "SUMMARY STATISTICS",
            rule,
            "",
            f"Average Distribution Yield: {stats['avg_yield_pct']:.2f}%",
            f"Highest Distribution Yield: {stats['max_yield_pct']:.2f}%",
            f"Lowest Distribution Yield: {stats['min_yield_pct']:.2f}%",
        ]

    lines += ["", rule, "END OF REPORT", rule, ""]
    return "\n".join(lines)


def write_text_report(
    records: Sequence[EtfRecord],
    path: str | Path,
    *,
    generated_at: datetime | None = None,
) -> Path:
    """Write the text report to ``path`` and return it."""
    path = Path(path)
    path.write_text(render_text(records, generated_at=generated_at))
    return path


def write_json_report(
    records: Sequence[EtfRecord],
    path: str | Path,
    *,
    generated_at: datetime | None = None,
) -> Path:
    """Write a machine-readable JSON report to ``path`` and return it."""
    generated_at = generated_at or datetime.now(UTC)
    payload = {
        "generated_at": generated_at.isoformat(),
        "total_etfs": len(records),
        "etfs": [record.as_dict() for record in records],
    }
    path = Path(path)
    path.write_text(json.dumps(payload, indent=2))
    return path


def write_excel_report(
    records: Sequence[EtfRecord],
    path: str | Path,
    *,
    generated_at: datetime | None = None,
) -> Path:
    """Write a multi-sheet Excel workbook (ETF Data + Summary) to ``path``."""
    generated_at = generated_at or datetime.now(UTC)
    frame = to_dataframe(records)
    summary = _summary_metric_value(frame, generated_at)
    path = Path(path)
    with Workbook(str(path)) as workbook:
        frame.write_excel(workbook=workbook, worksheet="ETF Data", autofit=True)
        summary.write_excel(workbook=workbook, worksheet="Summary", autofit=True)
    return path
