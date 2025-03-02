#!/usr/bin/env python3
"""
Test script for the database module.
Run this to verify that database operations work as expected.
"""

import logging
from database import db

def test_database():
    """Test basic database operations."""
    print("Daily Stoic Database Test")
    print("========================")
    
    # Connect to the database
    print("\nConnecting to database...")
    with db:
        # Add a test quote
        print("\nAdding test quotes...")
        quote1_id = db.add_quote(
            "The happiness of your life depends upon the quality of your thoughts.",
            "Marcus Aurelius",
            "Meditations"
        )
        print(f"Added quote with ID: {quote1_id}")
        
        quote2_id = db.add_quote(
            "You have power over your mind - not outside events. Realize this, and you will find strength.",
            "Marcus Aurelius",
            "Meditations"
        )
        print(f"Added quote with ID: {quote2_id}")
        
        quote3_id = db.add_quote(
            "The best revenge is not to be like your enemy.",
            "Marcus Aurelius",
            "Meditations"
        )
        print(f"Added quote with ID: {quote3_id}")
        
        # Try to add a duplicate quote (should return existing ID)
        dup_id = db.add_quote(
            "The happiness of your life depends upon the quality of your thoughts.",
            "Marcus Aurelius",
            "Meditations"
        )
        print(f"Attempted to add duplicate quote, got ID: {dup_id} (should match {quote1_id})")
        
        # Get quote by ID
        print("\nRetrieving quote by ID...")
        quote = db.get_quote_by_id(quote1_id)
        if quote:
            print(f"Retrieved quote: \"{quote['quote_text']}\" - {quote['author']}")
        else:
            print("Failed to retrieve quote by ID")
        
        # Get random unused quote
        print("\nGetting random unused quote...")
        random_quote = db.get_random_unused_quote()
        if random_quote:
            print(f"Random quote: \"{random_quote['quote_text']}\" - {random_quote['author']}")
        else:
            print("No unused quotes found")
        
        # Mark quote as used
        print("\nMarking quote as used...")
        if db.mark_quote_as_used(quote1_id):
            print(f"Marked quote {quote1_id} as used")
        else:
            print(f"Failed to mark quote {quote1_id} as used")
        
        # Get counts
        print("\nCounting quotes in database...")
        counts = db.count_quotes()
        print(f"Total quotes: {counts['total']}")
        print(f"Used quotes: {counts['used']}")
        print(f"Unused quotes: {counts['unused']}")
        
        # Reset cycle
        print("\nResetting cycle...")
        reset_count = db.reset_cycle()
        print(f"Reset {reset_count} quotes to unused")
        
        # Verify reset
        counts = db.count_quotes()
        print(f"Used quotes after reset: {counts['used']}")
        print(f"Unused quotes after reset: {counts['unused']}")
        
        print("\nTest completed successfully!")

if __name__ == "__main__":
    # Disable logging for cleaner output
    logging.disable(logging.CRITICAL)
    test_database()
