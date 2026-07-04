"""Tests for report rendering (text, JSON, Excel)."""

from __future__ import annotations

import json
import zipfile
from datetime import UTC, date, datetime

from covered_call_index.models import EtfRecord
from covered_call_index.reports import (
    render_text,
    summary_frame,
    to_dataframe,
    write_excel_report,
    write_json_report,
    write_text_report,
)

GENERATED_AT = datetime(2024, 6, 1, 12, 0, tzinfo=UTC)

RECORDS = [
    EtfRecord(
        ticker="TSLY",
        name="YieldMax TSLA Option Income Strategy ETF",
        strategy="TSLA Option Income Strategy",
        distribution_yield_pct=50.0,
        nav=26.95,
        inception_date=date(2022, 11, 22),
        expense_ratio_pct=1.07,
    ),
    EtfRecord(
        ticker="NVDY",
        name="YieldMax NVDA Option Income Strategy ETF",
        strategy="NVDA Option Income Strategy",
        distribution_yield_pct=30.0,
        nav=12.12,
        inception_date=date(2022, 12, 6),
        expense_ratio_pct=1.09,
    ),
]


class TestDataFrame:
    def test_columns_in_report_order(self):
        frame = to_dataframe(RECORDS)
        assert frame.columns == [
            "ticker",
            "name",
            "strategy",
            "distribution_yield_pct",
            "nav",
            "inception_date",
            "expense_ratio_pct",
        ]
        assert frame.height == 2

    def test_summary_frame_statistics(self):
        stats = summary_frame(to_dataframe(RECORDS)).to_dicts()[0]
        assert stats["total_etfs"] == 2
        assert stats["avg_yield_pct"] == 40.0
        assert stats["max_yield_pct"] == 50.0
        assert stats["min_yield_pct"] == 30.0


class TestTextReport:
    def test_render_contains_key_content(self):
        text = render_text(RECORDS, generated_at=GENERATED_AT)
        assert "YIELDMAX ETF DATA REPORT" in text
        assert "Total ETFs: 2" in text
        assert "TSLY - YieldMax TSLA Option Income Strategy ETF" in text
        assert "Distribution Yield (TTM): 50.00%" in text
        assert "Average Distribution Yield: 40.00%" in text

    def test_write_creates_file(self, tmp_path):
        path = write_text_report(
            RECORDS, tmp_path / "report.txt", generated_at=GENERATED_AT
        )
        assert path.exists()
        assert path.read_text().startswith("=" * 80)


class TestJsonReport:
    def test_write_roundtrips(self, tmp_path):
        path = write_json_report(
            RECORDS, tmp_path / "report.json", generated_at=GENERATED_AT
        )
        payload = json.loads(path.read_text())
        assert payload["generated_at"] == GENERATED_AT.isoformat()
        assert payload["total_etfs"] == 2
        assert payload["etfs"][0]["ticker"] == "TSLY"
        assert payload["etfs"][0]["inception_date"] == "2022-11-22"


class TestExcelReport:
    def test_writes_valid_multisheet_workbook(self, tmp_path):
        path = write_excel_report(
            RECORDS, tmp_path / "report.xlsx", generated_at=GENERATED_AT
        )
        assert path.exists()
        assert zipfile.is_zipfile(path)
        with zipfile.ZipFile(path) as workbook:
            names = workbook.namelist()
            assert "xl/workbook.xml" in names
            workbook_xml = workbook.read("xl/workbook.xml").decode()
        assert "ETF Data" in workbook_xml
        assert "Summary" in workbook_xml
