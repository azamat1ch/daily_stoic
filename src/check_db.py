#!/usr/bin/env python3
"""
Simple script to check the database state.
"""

import sys
import logging
from pathlib import Path

# Add the project root to the path to find local modules
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.database import QuoteDatabase

# Disable logging for cleaner output
logging.disable(logging.CRITICAL)

def main():
    """Check database state."""
    with QuoteDatabase() as db:
        counts = db.count_quotes()
        print(f"Database Status:")
        print(f"- Total quotes: {counts['total']}")
        print(f"- Used quotes: {counts['used']}")
        print(f"- Unused quotes: {counts['unused']}")

if __name__ == "__main__":
    main()
