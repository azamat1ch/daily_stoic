#!/usr/bin/env python3
"""
Database module for the Daily Stoic project.
Provides functionality to connect to and interact with the SQLite database.
"""

import sqlite3
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from pathlib import Path
from datetime import datetime

from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Database:
    """SQLite database wrapper for managing connections and queries."""
    
    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file. If None, uses the path from config.
        """
        if db_path is None:
            self.db_path = config.get_absolute_db_path()
        else:
            self.db_path = Path(db_path)
        
        self.conn = None
        self.cursor = None
        logger.info(f"Database initialized with path: {self.db_path}")
    
    def connect(self) -> None:
        """Establish a connection to the database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
            self.cursor = self.conn.cursor()
            logger.info("Connected to database successfully")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            logger.info("Disconnected from database")
    
    def __enter__(self):
        """Context manager support - connect when entering context."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support - disconnect when exiting context."""
        self.disconnect()
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        Execute a query with optional parameters.
        
        Args:
            query: SQL query to execute
            params: Parameters for the query
            
        Returns:
            Cursor object for the query
        """
        try:
            if not self.conn:
                self.connect()
            return self.cursor.execute(query, params)
        except sqlite3.Error as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    def commit(self) -> None:
        """Commit the current transaction."""
        if self.conn:
            self.conn.commit()
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a query and fetch all results.
        
        Args:
            query: SQL query to execute
            params: Parameters for the query
            
        Returns:
            List of rows as dictionaries
        """
        self.execute(query, params)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """
        Execute a query and fetch one result.
        
        Args:
            query: SQL query to execute
            params: Parameters for the query
            
        Returns:
            Single row as dictionary or None if no results
        """
        self.execute(query, params)
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """
        Insert a row into a table.
        
        Args:
            table: Table name
            data: Dictionary of column:value pairs
            
        Returns:
            ID of the inserted row
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            self.execute(query, tuple(data.values()))
            self.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                logger.warning(f"Attempt to insert duplicate data into {table}: {data}")
            raise
    
    def update(self, table: str, data: Dict[str, Any], condition: str, params: tuple) -> int:
        """
        Update rows in a table.
        
        Args:
            table: Table name
            data: Dictionary of column:value pairs to update
            condition: WHERE clause of the update statement
            params: Parameters for the WHERE clause
            
        Returns:
            Number of rows affected
        """
        set_clause = ', '.join([f"{col} = ?" for col in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        
        all_params = tuple(data.values()) + params
        self.execute(query, all_params)
        self.commit()
        return self.cursor.rowcount


class QuoteDatabase(Database):
    """Specialized database class for quote-related operations."""
    
    def add_quote(self, quote_text: str, author: str, source: Optional[str] = None) -> int:
        """
        Add a new quote to the database.
        
        Args:
            quote_text: The text of the quote
            author: The author of the quote
            source: The source of the quote (optional)
            
        Returns:
            ID of the new quote
        """
        data = {
            'quote_text': quote_text,
            'author': author
        }
        if source:
            data['source'] = source
        
        try:
            return self.insert('quotes', data)
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                logger.warning(f"Quote already exists: {quote_text} - {author}")
                # Get the ID of the existing quote
                existing_quote = self.fetch_one(
                    "SELECT quote_id FROM quotes WHERE quote_text = ? AND author = ?",
                    (quote_text, author)
                )
                return existing_quote['quote_id'] if existing_quote else 0
            raise
    
    def get_quote_by_id(self, quote_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a quote by its ID.
        
        Args:
            quote_id: ID of the quote to retrieve
            
        Returns:
            Quote data as dictionary or None if not found
        """
        return self.fetch_one("SELECT * FROM quotes WHERE quote_id = ?", (quote_id,))
    
    def get_random_unused_quote(self) -> Optional[Dict[str, Any]]:
        """
        Get a random quote that hasn't been used in the current cycle.
        
        Returns:
            Quote data as dictionary or None if all quotes are used
        """
        return self.fetch_one(
            "SELECT * FROM quotes WHERE is_used_in_current_cycle = 0 ORDER BY RANDOM() LIMIT 1"
        )
    
    def mark_quote_as_used(self, quote_id: int) -> bool:
        """
        Mark a quote as used in the current cycle and update its last used date.
        
        Args:
            quote_id: ID of the quote to mark
            
        Returns:
            True if the quote was marked, False otherwise
        """
        now = datetime.now().isoformat()
        rows_affected = self.update(
            'quotes',
            {'is_used_in_current_cycle': 1, 'last_used_date': now},
            'quote_id = ?',
            (quote_id,)
        )
        return rows_affected > 0
    
    def reset_cycle(self) -> int:
        """
        Reset the cycle by marking all quotes as unused.
        
        Returns:
            Number of quotes reset
        """
        self.execute("UPDATE quotes SET is_used_in_current_cycle = 0")
        self.commit()
        return self.cursor.rowcount
    
    def count_quotes(self) -> Dict[str, int]:
        """
        Count the total quotes and how many are used/unused in the current cycle.
        
        Returns:
            Dictionary with total, used, and unused counts
        """
        total = self.fetch_one("SELECT COUNT(*) as count FROM quotes")
        used = self.fetch_one("SELECT COUNT(*) as count FROM quotes WHERE is_used_in_current_cycle = 1")
        unused = self.fetch_one("SELECT COUNT(*) as count FROM quotes WHERE is_used_in_current_cycle = 0")
        
        return {
            'total': total['count'] if total else 0,
            'used': used['count'] if used else 0,
            'unused': unused['count'] if unused else 0
        }


# Create a singleton instance for importing elsewhere
db = QuoteDatabase()
