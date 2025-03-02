# Database Schema Diagram

## quotes Table

| Column                  | Type      | Constraints                | Description                                |
|-------------------------|-----------|----------------------------|--------------------------------------------|
| quote_id                | INTEGER   | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each quote           |
| quote_text              | TEXT      | NOT NULL                   | The text content of the quote              |
| author                  | TEXT      | NOT NULL                   | The author of the quote                    |
| source                  | TEXT      |                            | Source work (book, essay, etc.)            |
| last_used_date          | TIMESTAMP |                            | When this quote was last used              |
| is_used_in_current_cycle| BOOLEAN   | DEFAULT 0                  | Flag to track usage in current cycle       |
| date_added              | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP  | When the quote was added to the database   |

## Indexes

1. **idx_quotes_usage**: On `is_used_in_current_cycle` - Speeds up queries to find unused quotes
2. **idx_quotes_date**: On `last_used_date` - Helps with sorting by last used date

## Unique Constraints

- `(quote_text, author)`: Ensures no duplicate quotes from the same author

## Usage Flow

1. When selecting a quote for the day:
   - Query for quotes where `is_used_in_current_cycle = 0`
   - Select one randomly
   - Update its `last_used_date` to current date/time
   - Set `is_used_in_current_cycle = 1`

2. When all quotes have been used in a cycle:
   - Reset all quotes to `is_used_in_current_cycle = 0`
   - Begin new cycle
