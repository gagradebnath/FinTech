#!/usr/bin/env python3
"""
Script to identify the exact source of the timestamp.split error
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import re

def find_split_usage():
    """Find any remaining .split() usage in templates"""
    template_dir = "app/templates"
    
    split_patterns = [
        r'\.split\s*\(',
        r'timestamp\.split',
        r'\.split\s*\(\s*[\'"][^\'\"]*[\'\"]\s*\)',
    ]
    
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        for pattern in split_patterns:
                            if re.search(pattern, line):
                                print(f"Found split usage in {filepath}:{i}")
                                print(f"  Line: {line.strip()}")
                                print()

def check_template_line_137():
    """Check what's actually at line 137 in dashboard.html"""
    filepath = "app/templates/dashboard.html"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) >= 137:
                print(f"Line 137 in {filepath}:")
                print(f"  {lines[136].strip()}")  # Line 137 (0-indexed)
                print(f"Context (lines 135-140):")
                for i in range(134, min(140, len(lines))):
                    print(f"  {i+1}: {lines[i].rstrip()}")
            else:
                print(f"File {filepath} has only {len(lines)} lines")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

if __name__ == "__main__":
    print("Searching for .split() usage in templates...")
    find_split_usage()
    print("\nChecking line 137 in dashboard.html...")
    check_template_line_137()
