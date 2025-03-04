#!/usr/bin/env python3
"""
Quote ingestion script for the Daily Stoic project.
Reads quotes from a CSV file and populates the SQLite database.
"""

import os
import csv
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the path to find local modules
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.database import QuoteDatabase
from src.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def read_quotes_from_csv(csv_path: Path) -> List[Dict[str, str]]:
    """
    Read quotes from a CSV file.
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        List of dictionaries, each representing a quote
    """
    quotes = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                # Validate required fields
                if not row.get('quote_text') or not row.get('author'):
                    logger.warning(f"Skipping row due to missing required fields: {row}")
                    continue
                
                quotes.append({
                    'quote_text': row['quote_text'].strip(),
                    'author': row['author'].strip(),
                    'source': row.get('source', '').strip()
                })
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        raise
    
    return quotes

def ingest_quotes(db: QuoteDatabase, quotes: List[Dict[str, str]]) -> Dict[str, int]:
    """
    Ingest quotes into the database.
    
    Args:
        db: Database connection
        quotes: List of quote dictionaries
        
    Returns:
        Dictionary with statistics about ingestion
    """
    stats = {
        'total': len(quotes),
        'inserted': 0,
        'skipped': 0,
        'errors': 0
    }
    
    for quote in quotes:
        try:
            quote_id = db.add_quote(
                quote_text=quote['quote_text'],
                author=quote['author'],
                source=quote.get('source')
            )
            
            if quote_id > 0:
                stats['inserted'] += 1
                logger.debug(f"Added quote ID {quote_id}: {quote['quote_text'][:30]}...")
            else:
                stats['skipped'] += 1
                logger.debug(f"Skipped existing quote: {quote['quote_text'][:30]}...")
                
        except Exception as e:
            stats['errors'] += 1
            logger.error(f"Error adding quote: {e}")
            logger.error(f"Quote data: {quote}")
    
    return stats

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Ingest quotes from CSV into database")
    parser.add_argument('csv_file', help="Path to CSV file containing quotes")
    parser.add_argument('--reset', action='store_true', help="Reset usage cycle before ingestion")
    args = parser.parse_args()
    
    csv_path = Path(args.csv_file)
    if not csv_path.exists() or not csv_path.is_file():
        logger.error(f"CSV file not found: {csv_path}")
        sys.exit(1)
    
    try:
        # Read quotes from CSV
        logger.info(f"Reading quotes from {csv_path}")
        quotes = read_quotes_from_csv(csv_path)
        logger.info(f"Found {len(quotes)} quotes in CSV file")
        
        # Connect to database and ingest quotes
        logger.info("Connecting to database")
        with QuoteDatabase() as db:
            # Optional: reset cycle
            if args.reset:
                logger.info("Resetting usage cycle")
                reset_count = db.reset_cycle()
                logger.info(f"Reset {reset_count} quotes to unused")
            
            # Ingest quotes
            logger.info("Ingesting quotes into database")
            stats = ingest_quotes(db, quotes)
            
            # Get final counts
            counts = db.count_quotes()
            
            # Display results
            logger.info("Quote ingestion completed")
            logger.info(f"Total quotes in CSV:        {stats['total']}")
            logger.info(f"Quotes inserted:            {stats['inserted']}")
            logger.info(f"Quotes skipped (duplicates): {stats['skipped']}")
            logger.info(f"Errors during ingestion:    {stats['errors']}")
            logger.info(f"Total quotes in database:   {counts['total']}")
            logger.info(f"Unused quotes in database:  {counts['unused']}")
    
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
