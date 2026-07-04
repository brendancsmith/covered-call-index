# covered-call-index

Learnings about covered call index ETFs.

## YieldMax ETF Data Reporter

Fetches live data for [YieldMax](https://www.yieldmaxetfs.com/) option-income
ETFs from Yahoo Finance and generates text, JSON, and Excel reports.

### Data source

Fund data comes from Yahoo Finance via the [`yfinance`](https://github.com/ranaroussi/yfinance)
library — no API key required. For each ticker the reporter collects:

| Field | Source |
| --- | --- |
| Name | `longName` |
| Strategy | derived from the fund name |
| Distribution yield (TTM) | trailing-12-month distributions ÷ NAV, computed from the fund's distribution history |
| NAV | `navPrice` |
| Inception date | `fundInceptionDate` |
| Expense ratio | `netExpenseRatio` (total expense ratio) |

The **distribution yield** is the sum of the trailing twelve months of
distributions divided by NAV. It is reproducible from the fund's own
distribution history and differs from a fund's marketed "distribution rate,"
which annualises the most recent distribution.

### Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

### Usage

Generate reports for the default set of YieldMax ETFs:

```bash
uv run yieldmax-report
```

This writes three files to the current directory:

- `yieldmax_report.txt` — human-readable summary with per-ETF details and statistics
- `yieldmax_report.json` — machine-readable data
- `yieldmax_report.xlsx` — Excel workbook with an **ETF Data** sheet and a **Summary** sheet

Options:

```bash
uv run yieldmax-report --tickers TSLY NVDY CONY --output-dir reports --prefix my_report
```

| Option | Default | Description |
| --- | --- | --- |
| `--tickers` | well-known YieldMax funds | ETF tickers to report on |
| `--output-dir` | `.` | directory to write reports into |
| `--prefix` | `yieldmax_report` | base filename for the reports |

A ticker that cannot be fetched is reported as a warning on stderr and skipped;
the command still succeeds as long as at least one ticker returns data.

### Development

```bash
uv run ruff check --fix
uv run ruff format
uv run ty check
uv run pytest
```

Tests run fully offline: the report-building logic is a pure layer exercised
without any network calls.
