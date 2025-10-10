#!/usr/bin/env python3
"""
Yieldmax ETF Data Scraper
Fetches ETF data from Yieldmax and generates reports
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import sys
from typing import Dict, List, Optional


class YieldmaxScraper:
    """Scraper for Yieldmax ETF data"""
    
    BASE_URL = "https://www.yieldmaxetfs.com"
    API_URL = "https://www.yieldmaxetfs.com/api"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_api_data(self) -> Optional[Dict]:
        """Attempt to fetch data from the API"""
        try:
            response = self.session.get(f"{self.API_URL}/etfs", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API fetch failed: {e}")
            return None
    
    def scrape_website(self) -> Optional[List[Dict]]:
        """Scrape ETF data from the website"""
        try:
            response = self.session.get(self.BASE_URL, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            
            etfs = []
            
            # Try to find ETF listings on the page
            # This is a generic approach - actual implementation may vary based on website structure
            etf_containers = soup.find_all(['div', 'table', 'section'], class_=lambda x: x and ('etf' in x.lower() or 'fund' in x.lower()))
            
            for container in etf_containers:
                etf_data = self._parse_etf_container(container)
                if etf_data:
                    etfs.append(etf_data)
            
            return etfs if etfs else None
        except Exception as e:
            print(f"Website scraping failed: {e}")
            return None
    
    def _parse_etf_container(self, container) -> Optional[Dict]:
        """Parse an ETF container element"""
        try:
            etf_data = {}
            
            # Look for ticker symbol
            ticker_elem = container.find(['span', 'strong', 'div'], class_=lambda x: x and 'ticker' in x.lower())
            if ticker_elem:
                etf_data['ticker'] = ticker_elem.text.strip()
            
            # Look for ETF name
            name_elem = container.find(['h2', 'h3', 'h4', 'div'], class_=lambda x: x and 'name' in x.lower())
            if name_elem:
                etf_data['name'] = name_elem.text.strip()
            
            # Look for yield information
            yield_elem = container.find(['span', 'div'], class_=lambda x: x and 'yield' in x.lower())
            if yield_elem:
                etf_data['yield'] = yield_elem.text.strip()
            
            return etf_data if etf_data else None
        except Exception:
            return None
    
    def get_mock_data(self) -> List[Dict]:
        """Return mock data for demonstration purposes"""
        return [
            {
                'ticker': 'TSLY',
                'name': 'YieldMax TSLA Option Income Strategy ETF',
                'strategy': 'Tesla Covered Call',
                'distribution_yield': '53.2%',
                'nav': '$12.45',
                'inception_date': '2022-11-01',
                'expense_ratio': '0.99%'
            },
            {
                'ticker': 'NVDY',
                'name': 'YieldMax NVDA Option Income Strategy ETF',
                'strategy': 'NVIDIA Covered Call',
                'distribution_yield': '48.7%',
                'nav': '$18.32',
                'inception_date': '2022-12-06',
                'expense_ratio': '0.99%'
            },
            {
                'ticker': 'APLY',
                'name': 'YieldMax AAPL Option Income Strategy ETF',
                'strategy': 'Apple Covered Call',
                'distribution_yield': '41.3%',
                'nav': '$15.67',
                'inception_date': '2023-01-10',
                'expense_ratio': '0.99%'
            },
            {
                'ticker': 'MSFO',
                'name': 'YieldMax MSFT Option Income Strategy ETF',
                'strategy': 'Microsoft Covered Call',
                'distribution_yield': '39.8%',
                'nav': '$16.89',
                'inception_date': '2023-02-14',
                'expense_ratio': '0.99%'
            },
            {
                'ticker': 'GOOY',
                'name': 'YieldMax GOOGL Option Income Strategy ETF',
                'strategy': 'Google Covered Call',
                'distribution_yield': '44.2%',
                'nav': '$14.23',
                'inception_date': '2023-03-21',
                'expense_ratio': '0.99%'
            },
            {
                'ticker': 'AMZY',
                'name': 'YieldMax AMZN Option Income Strategy ETF',
                'strategy': 'Amazon Covered Call',
                'distribution_yield': '42.5%',
                'nav': '$13.78',
                'inception_date': '2023-04-11',
                'expense_ratio': '0.99%'
            },
            {
                'ticker': 'CONY',
                'name': 'YieldMax COIN Option Income Strategy ETF',
                'strategy': 'Coinbase Covered Call',
                'distribution_yield': '61.4%',
                'nav': '$11.34',
                'inception_date': '2023-05-02',
                'expense_ratio': '0.99%'
            },
            {
                'ticker': 'OARK',
                'name': 'YieldMax ARKK Option Income Strategy ETF',
                'strategy': 'ARK Innovation ETF Covered Call',
                'distribution_yield': '55.8%',
                'nav': '$10.92',
                'inception_date': '2023-06-13',
                'expense_ratio': '0.99%'
            }
        ]
    
    def fetch_data(self) -> List[Dict]:
        """Fetch ETF data using available methods"""
        print("Attempting to fetch data from Yieldmax API...")
        api_data = self.fetch_api_data()
        
        if api_data:
            print("Successfully fetched data from API")
            return api_data
        
        print("API unavailable. Attempting to scrape website...")
        scraped_data = self.scrape_website()
        
        if scraped_data:
            print("Successfully scraped data from website")
            return scraped_data
        
        print("Warning: Could not fetch live data. Using mock data for demonstration.")
        print("Note: In production, you would need to verify website structure and API endpoints.")
        return self.get_mock_data()


class ReportGenerator:
    """Generate reports from ETF data"""
    
    def __init__(self, data: List[Dict]):
        self.data = data
        self.df = pd.DataFrame(data)
    
    def generate_text_report(self, filename: str = "yieldmax_report.txt"):
        """Generate a text report"""
        with open(filename, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("YIELDMAX ETF DATA REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Total ETFs: {len(self.data)}\n\n")
            
            for idx, etf in enumerate(self.data, 1):
                f.write(f"\n{idx}. {etf.get('ticker', 'N/A')}\n")
                f.write("-" * 40 + "\n")
                for key, value in etf.items():
                    if key != 'ticker':
                        f.write(f"  {key.replace('_', ' ').title()}: {value}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("SUMMARY STATISTICS\n")
            f.write("=" * 80 + "\n")
            
            if 'distribution_yield' in self.df.columns:
                # Extract numeric values from percentage strings
                yields = self.df['distribution_yield'].str.rstrip('%').astype(float)
                f.write(f"\nAverage Distribution Yield: {yields.mean():.2f}%\n")
                f.write(f"Highest Distribution Yield: {yields.max():.2f}%\n")
                f.write(f"Lowest Distribution Yield: {yields.min():.2f}%\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        print(f"Text report generated: {filename}")
    
    def generate_excel_report(self, filename: str = "yieldmax_report.xlsx"):
        """Generate an Excel report"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main data sheet
            self.df.to_excel(writer, sheet_name='ETF Data', index=False)
            
            # Summary sheet
            summary_data = {
                'Metric': ['Total ETFs', 'Report Date'],
                'Value': [len(self.data), datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            }
            
            if 'distribution_yield' in self.df.columns:
                yields = self.df['distribution_yield'].str.rstrip('%').astype(float)
                summary_data['Metric'].extend([
                    'Average Distribution Yield (%)',
                    'Highest Distribution Yield (%)',
                    'Lowest Distribution Yield (%)'
                ])
                summary_data['Value'].extend([
                    f"{yields.mean():.2f}",
                    f"{yields.max():.2f}",
                    f"{yields.min():.2f}"
                ])
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Format the Excel file
            workbook = writer.book
            for sheet_name in workbook.sheetnames:
                worksheet = workbook[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(cell.value)
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"Excel report generated: {filename}")
    
    def generate_json_report(self, filename: str = "yieldmax_report.json"):
        """Generate a JSON report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_etfs': len(self.data),
            'etfs': self.data
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"JSON report generated: {filename}")


def main():
    """Main execution function"""
    print("YieldMax ETF Data Scraper")
    print("=" * 50)
    
    # Fetch data
    scraper = YieldmaxScraper()
    etf_data = scraper.fetch_data()
    
    if not etf_data:
        print("Error: No data available")
        sys.exit(1)
    
    print(f"\nFetched data for {len(etf_data)} ETFs")
    
    # Generate reports
    print("\nGenerating reports...")
    generator = ReportGenerator(etf_data)
    
    generator.generate_text_report()
    generator.generate_excel_report()
    generator.generate_json_report()
    
    print("\n" + "=" * 50)
    print("All reports generated successfully!")
    print("\nGenerated files:")
    print("  - yieldmax_report.txt")
    print("  - yieldmax_report.xlsx")
    print("  - yieldmax_report.json")


if __name__ == "__main__":
    main()
