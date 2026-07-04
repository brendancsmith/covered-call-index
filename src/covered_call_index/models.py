"""Data model for a single YieldMax ETF snapshot."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date

# Well-known YieldMax option-income ETFs. Override on the command line with
# ``--tickers`` to report on a different set.
DEFAULT_TICKERS: tuple[str, ...] = (
    "TSLY",
    "NVDY",
    "APLY",
    "MSFO",
    "GOOY",
    "AMZY",
    "CONY",
    "OARK",
    "YMAX",
)


@dataclass(frozen=True, slots=True)
class EtfRecord:
    """A point-in-time snapshot of one ETF's headline metrics.

    ``distribution_yield_pct`` is the trailing-twelve-month sum of
    distributions divided by NAV, expressed as a percentage. It is a
    reproducible measure computed from the fund's own distribution history,
    and differs from a fund's marketed "distribution rate" (which annualises
    the most recent distribution).
    """

    ticker: str
    name: str
    strategy: str
    distribution_yield_pct: float
    nav: float
    inception_date: date
    expense_ratio_pct: float

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-friendly mapping (dates rendered ISO-8601)."""
        data = asdict(self)
        data["inception_date"] = self.inception_date.isoformat()
        return data
