# Stoic Quotes Data Format

This document describes the data format used for storing and importing Stoic quotes into the Daily Stoic database.

## CSV Format

The quotes are stored in CSV (Comma-Separated Values) format with the following columns:

1. **quote_text** - The full text of the quote
2. **author** - The name of the author (e.g., "Marcus Aurelius", "Seneca", "Epictetus")
3. **source** - The source work (e.g., "Meditations", "Letters to Lucilius", "Discourses")

### Rules for CSV Formatting

1. All fields should be enclosed in double quotes (`"`) to handle commas and other special characters within the text
2. Any double quotes within the text should be escaped by doubling them (`""`)
3. UTF-8 encoding should be used for proper handling of special characters
4. The first line of the file should be the header row with column names

### Example

```csv
quote_text,author,source
"The happiness of your life depends upon the quality of your thoughts.","Marcus Aurelius","Meditations"
"You have power over your mind - not outside events. Realize this, and you will find strength.","Marcus Aurelius","Meditations"
"The best revenge is not to be like your enemy.","Marcus Aurelius","Meditations"
```

## JSON Format (Alternative)

For more complex quote structures or additional metadata, a JSON format can also be used:

```json
[
  {
    "quote_text": "The happiness of your life depends upon the quality of your thoughts.",
    "author": "Marcus Aurelius",
    "source": "Meditations",
    "book": "Book IV",
    "notes": "Often paraphrased in modern renditions"
  },
  {
    "quote_text": "You have power over your mind - not outside events. Realize this, and you will find strength.",
    "author": "Marcus Aurelius",
    "source": "Meditations",
    "book": "Book V",
    "notes": ""
  }
]
```

## Database Fields Mapping

When importing quotes from these formats, the following mapping is used:

| CSV/JSON Field | Database Field           | Notes                                       |
|----------------|--------------------------|---------------------------------------------|
| quote_text     | quote_text               | Required                                    |
| author         | author                   | Required                                    |
| source         | source                   | Optional, but recommended                   |
| N/A            | last_used_date           | Set to NULL on initial import               |
| N/A            | is_used_in_current_cycle | Set to 0 (false) on initial import          |
| N/A            | date_added               | Set to current timestamp on import          |

## Recommendations for Quote Collection

1. **Quality over quantity**: Include fewer, high-quality quotes rather than many low-quality ones
2. **Consistent formatting**: Maintain consistent capitalization and punctuation 
3. **Attribution accuracy**: Verify quotes are correctly attributed to their authors
4. **Source verification**: Provide the original source work when possible
5. **Quote length**: Keep quotes concise enough to fit nicely on an image (ideally under 250 characters)
6. **Uniqueness**: Avoid duplicate quotes or quotes that express the same idea
