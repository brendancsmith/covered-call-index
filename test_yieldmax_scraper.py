#!/usr/bin/env python3
"""
Simple tests for the Yieldmax scraper
"""

import os
import sys
from yieldmax_scraper import YieldmaxScraper, ReportGenerator


def test_mock_data():
    """Test that mock data is available"""
    scraper = YieldmaxScraper()
    data = scraper.get_mock_data()
    
    assert len(data) > 0, "Mock data should not be empty"
    assert all('ticker' in item for item in data), "All items should have ticker"
    assert all('name' in item for item in data), "All items should have name"
    print("✓ Mock data test passed")


def test_data_fetch():
    """Test that data can be fetched"""
    scraper = YieldmaxScraper()
    data = scraper.fetch_data()
    
    assert data is not None, "Data should not be None"
    assert len(data) > 0, "Data should not be empty"
    print(f"✓ Data fetch test passed - {len(data)} ETFs found")


def test_report_generation():
    """Test that reports can be generated"""
    scraper = YieldmaxScraper()
    data = scraper.fetch_data()
    
    # Clean up old test files
    test_files = ['test_report.txt', 'test_report.xlsx', 'test_report.json']
    for f in test_files:
        if os.path.exists(f):
            os.remove(f)
    
    generator = ReportGenerator(data)
    generator.generate_text_report('test_report.txt')
    generator.generate_excel_report('test_report.xlsx')
    generator.generate_json_report('test_report.json')
    
    # Verify files were created
    for f in test_files:
        assert os.path.exists(f), f"File {f} should be created"
        assert os.path.getsize(f) > 0, f"File {f} should not be empty"
    
    # Clean up
    for f in test_files:
        os.remove(f)
    
    print("✓ Report generation test passed")


def main():
    """Run all tests"""
    print("Running Yieldmax Scraper Tests")
    print("=" * 50)
    
    try:
        test_mock_data()
        test_data_fetch()
        test_report_generation()
        
        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
