#!/usr/bin/env python3
"""
Test script to verify datetime filter functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from app import create_app

def test_filters():
    """Test the custom Jinja2 filters"""
    app = create_app()
    
    with app.app_context():
        # Test data types
        test_datetime = datetime.now()
        test_string = "2024-07-05 14:30:25"
        test_none = None
        
        # Get the filters
        format_date = app.jinja_env.filters['format_date']
        format_time = app.jinja_env.filters['format_time']
        format_datetime = app.jinja_env.filters['format_datetime']
        
        print("Testing format_date filter:")
        print(f"  datetime object: {format_date(test_datetime)}")
        print(f"  string: {format_date(test_string)}")
        print(f"  None: {format_date(test_none)}")
        
        print("\nTesting format_time filter:")
        print(f"  datetime object: {format_time(test_datetime)}")
        print(f"  string: {format_time(test_string)}")
        print(f"  None: {format_time(test_none)}")
        
        print("\nTesting format_datetime filter:")
        print(f"  datetime object: {format_datetime(test_datetime)}")
        print(f"  string: {format_datetime(test_string)}")
        print(f"  None: {format_datetime(test_none)}")
        
        print("\nAll filters tested successfully!")

if __name__ == "__main__":
    test_filters()
