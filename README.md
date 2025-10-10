# covered--call-index
Learnings about covered call index ETFs

## Yieldmax ETF Data Scraper

This repository contains a Python script that pulls data from Yieldmax ETFs and generates comprehensive reports.

### Features

- Attempts to fetch data from Yieldmax API
- Falls back to web scraping if API is unavailable
- Uses mock data for demonstration when live data is inaccessible
- Generates three types of reports:
  - **Text Report** (`yieldmax_report.txt`): Human-readable summary with statistics
  - **Excel Report** (`yieldmax_report.xlsx`): Structured data in Excel format with multiple sheets
  - **JSON Report** (`yieldmax_report.json`): Machine-readable data format

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Usage

Run the scraper to generate reports:
```bash
python yieldmax_scraper.py
```

This will create three report files in the current directory:
- `yieldmax_report.txt` - Text report with ETF details and statistics
- `yieldmax_report.xlsx` - Excel workbook with ETF data and summary sheets
- `yieldmax_report.json` - JSON file with structured ETF data

### Testing

Run the test suite to verify the scraper works correctly:
```bash
python test_yieldmax_scraper.py
```

### Report Contents

The reports include information about Yieldmax ETFs:
- Ticker symbol
- ETF name
- Investment strategy
- Distribution yield
- Net Asset Value (NAV)
- Inception date
- Expense ratio

Summary statistics include:
- Total number of ETFs
- Average distribution yield
- Highest and lowest distribution yields

### Dependencies

- `requests` - HTTP library for API calls and web scraping
- `beautifulsoup4` - HTML parsing for web scraping
- `openpyxl` - Excel file generation
- `pandas` - Data manipulation and analysis
- `lxml` - XML/HTML parser

### Notes

The script intelligently handles different data sources:
1. First attempts to use the Yieldmax API
2. Falls back to web scraping if the API is unavailable
3. Uses demonstration data if neither method works

When live data becomes available, the script will automatically use real data from Yieldmax.
