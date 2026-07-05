"""Command-line entry point: fetch YieldMax ETF data and write reports."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from .fetch import fetch_etfs
from .models import DEFAULT_TICKERS
from .reports import write_excel_report, write_json_report, write_text_report


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="yieldmax-report",
        description="Fetch YieldMax ETF data and generate text, JSON, "
        "and Excel reports.",
    )
    parser.add_argument(
        "--tickers",
        nargs="+",
        metavar="TICKER",
        default=list(DEFAULT_TICKERS),
        help="ETF tickers to report on (default: the well-known YieldMax funds).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Directory to write reports into (default: current directory).",
    )
    parser.add_argument(
        "--prefix",
        default="yieldmax_report",
        help="Base filename for the generated reports (default: yieldmax_report).",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Fetch the requested tickers and write the three report files.

    Returns a process exit code: ``0`` on success (even with some per-ticker
    failures), ``1`` when no data could be fetched at all.
    """
    args = _parse_args(argv)

    records, errors = fetch_etfs(args.tickers)
    for ticker, message in errors.items():
        print(f"warning: could not fetch {ticker}: {message}", file=sys.stderr)

    if not records:
        print("error: no ETF data could be fetched", file=sys.stderr)
        return 1

    generated_at = datetime.now(UTC)
    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    prefix: str = args.prefix

    written = [
        write_text_report(
            records, output_dir / f"{prefix}.txt", generated_at=generated_at
        ),
        write_json_report(
            records, output_dir / f"{prefix}.json", generated_at=generated_at
        ),
        write_excel_report(
            records, output_dir / f"{prefix}.xlsx", generated_at=generated_at
        ),
    ]

    print(f"Fetched {len(records)} ETF(s). Reports written:")
    for path in written:
        print(f"  - {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
