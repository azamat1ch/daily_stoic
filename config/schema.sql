-- Database schema for Daily Stoic Quotes
-- This defines the structure of the SQLite database used to store quotes

-- Drop tables if they exist (useful for resetting the database)
DROP TABLE IF EXISTS quotes;

-- Create quotes table
CREATE TABLE quotes (
    quote_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_text       TEXT NOT NULL,               -- The actual quote text
    author           TEXT NOT NULL,               -- The author of the quote (e.g., "Seneca", "Marcus Aurelius")
    source           TEXT,                        -- Source work (e.g., "Meditations", "Letters to Lucilius")
    last_used_date   TIMESTAMP,                   -- When this quote was last used (NULL if never used)
    is_used_in_current_cycle BOOLEAN DEFAULT 0,   -- Whether this quote has been used in the current cycle
    date_added       TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- When this quote was added to the database
    
    -- Ensure quote text and author combination is unique to avoid duplicates
    UNIQUE(quote_text, author)
);

-- Create an index on the is_used_in_current_cycle field for faster queries
CREATE INDEX idx_quotes_usage ON quotes(is_used_in_current_cycle);

-- Create an index on the last_used_date field for faster sorting by date
CREATE INDEX idx_quotes_date ON quotes(last_used_date);

-- Insert some initial test data (optional)
-- INSERT INTO quotes (quote_text, author, source) VALUES 
--     ('The happiness of your life depends upon the quality of your thoughts.', 'Marcus Aurelius', 'Meditations'),
--     ('You have power over your mind - not outside events. Realize this, and you will find strength.', 'Marcus Aurelius', 'Meditations'),
--     ('The best revenge is not to be like your enemy.', 'Marcus Aurelius', 'Meditations');
