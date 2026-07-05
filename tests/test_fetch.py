"""Tests for the pure record-building layer (no network)."""

from __future__ import annotations

from datetime import date

import pytest

from covered_call_index.fetch import (
    EtfDataError,
    build_record,
    strategy_from_name,
    trailing_twelve_month_yield_pct,
)

INFO = {
    "longName": "YieldMax TSLA Option Income Strategy ETF",
    "navPrice": 26.95,
    "fundInceptionDate": 1669075200,  # 2022-11-22 UTC
    "netExpenseRatio": 1.07,
}


class TestTrailingTwelveMonthYield:
    def test_sums_only_the_trailing_year(self):
        asof = date(2024, 6, 1)
        distributions = [
            (date(2023, 5, 15), 1.00),  # older than cutoff -> excluded
            (date(2023, 7, 1), 2.00),  # included
            (date(2024, 5, 1), 3.00),  # included
            (date(2024, 6, 1), 4.00),  # boundary (== asof) -> included
            (date(2024, 6, 2), 5.00),  # future -> excluded
        ]
        # (2 + 3 + 4) / 20 * 100 = 45.00
        assert trailing_twelve_month_yield_pct(distributions, 20.0, asof=asof) == 45.0

    def test_no_distributions_yields_zero(self):
        assert trailing_twelve_month_yield_pct([], 20.0, asof=date(2024, 6, 1)) == 0.0

    def test_non_positive_nav_raises(self):
        with pytest.raises(EtfDataError):
            trailing_twelve_month_yield_pct([], 0.0, asof=date(2024, 6, 1))


class TestStrategyFromName:
    def test_strips_prefix_and_suffix(self):
        assert (
            strategy_from_name("YieldMax TSLA Option Income Strategy ETF")
            == "TSLA Option Income Strategy"
        )

    def test_leaves_unmatched_name_untouched(self):
        assert strategy_from_name("Universe Fund of Option Income ETFs") == (
            "Universe Fund of Option Income ETFs"
        )


class TestBuildRecord:
    def test_builds_full_record(self):
        distributions = [(date(2024, 5, 1), 13.475)]  # 13.475 / 26.95 = 50.0%
        record = build_record("tsly", INFO, distributions, asof=date(2024, 6, 1))

        assert record.ticker == "TSLY"
        assert record.name == "YieldMax TSLA Option Income Strategy ETF"
        assert record.strategy == "TSLA Option Income Strategy"
        assert record.nav == 26.95
        assert record.inception_date == date(2022, 11, 22)
        assert record.expense_ratio_pct == 1.07
        assert record.distribution_yield_pct == 50.0

    def test_as_dict_renders_iso_date(self):
        record = build_record("tsly", INFO, [], asof=date(2024, 6, 1))
        assert record.as_dict()["inception_date"] == "2022-11-22"

    @pytest.mark.parametrize(
        "missing",
        ["longName", "navPrice", "fundInceptionDate", "netExpenseRatio"],
    )
    def test_missing_required_field_raises(self, missing):
        info = {key: value for key, value in INFO.items() if key != missing}
        with pytest.raises(EtfDataError):
            build_record("TSLY", info, [], asof=date(2024, 6, 1))

    def test_non_positive_nav_raises(self):
        info = INFO | {"navPrice": 0.0}
        with pytest.raises(EtfDataError):
            build_record("TSLY", info, [], asof=date(2024, 6, 1))

    def test_boolean_is_not_accepted_as_numeric(self):
        info = INFO | {"netExpenseRatio": True}
        with pytest.raises(EtfDataError):
            build_record("TSLY", info, [], asof=date(2024, 6, 1))
