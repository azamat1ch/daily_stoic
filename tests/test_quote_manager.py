import pytest
import json
import os
import time
from unittest.mock import mock_open, patch

# Import the script functions (adjust the import path if needed)
from src.quote_manager import load_quotes_from_json, select_quote, update_quote_usage

# Test data
SAMPLE_QUOTES = {
    "quotes": [
        {
            "text": "Test quote 1",
            "author": "Author 1",
            "last_used_timestamp": 100
        },
        {
            "text": "Test quote 2",
            "author": "Author 2",
            "last_used_timestamp": 200
        },
        {
            "text": "Test quote 3",
            "author": "Author 3",
            "last_used_timestamp": 100
        }
    ]
}

@pytest.fixture
def sample_quotes_list():
    """Fixture providing a sample list of quotes"""
    return SAMPLE_QUOTES["quotes"]

@pytest.fixture
def sample_json_file(tmp_path):
    """Fixture creating a temporary JSON file with test quotes"""
    file_path = tmp_path / "test_quotes.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(SAMPLE_QUOTES, f)
    return file_path

## Tests for load_quotes_from_json

def test_load_quotes_valid_json(sample_json_file):
    """Test loading quotes from a valid JSON file"""
    quotes = load_quotes_from_json(sample_json_file)
    assert len(quotes) == 3
    assert quotes[0]["text"] == "Test quote 1"
    assert quotes[1]["author"] == "Author 2"

def test_load_quotes_file_not_found():
    """Test handling of nonexistent file"""
    with pytest.raises(FileNotFoundError):
        load_quotes_from_json("nonexistent_file.json")

@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data="invalid json")
def test_load_quotes_invalid_json(mock_exists, mock_file):
    with pytest.raises(json.JSONDecodeError):
        load_quotes_from_json("any_path.json")

@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"not_quotes": []}))
def test_load_quotes_missing_quotes_key(mock_file):
    """Test handling of missing 'quotes' key"""
    result = load_quotes_from_json("any_path.json")
    assert result == []

## Tests for select_quote

def test_select_quote_normal(sample_quotes_list):
    """Test quote selection with normal data"""
    quote = select_quote(sample_quotes_list)
    assert quote is not None
    # Should select quotes with lowest timestamp (100)
    assert quote["text"] in ["Test quote 1", "Test quote 3"]
    assert quote["last_used_timestamp"] == 100

def test_select_quote_empty_list():
    """Test handling of empty quotes list"""
    result = select_quote([])
    assert result is None

def test_select_quote_invalid_items():
    """Test handling of invalid items in quotes list"""
    invalid_list = [{"no_timestamp": "value"}, None, 123]
    result = select_quote(invalid_list)
    assert result is None

## Tests for update_quote_usage

def test_update_quote_usage_success(sample_json_file, sample_quotes_list):
    """Test successful quote usage update"""
    quote = sample_quotes_list[0].copy()
    result = update_quote_usage(quote, sample_json_file)
    assert result is True
    
    # Verify the file was updated
    with open(sample_json_file, 'r', encoding='utf-8') as f:
        updated_data = json.load(f)
    
    found_quote = next((q for q in updated_data["quotes"] if q["text"] == quote["text"]), None)
    assert found_quote is not None
    assert found_quote["last_used_timestamp"] > quote["last_used_timestamp"]

def test_update_quote_usage_not_found(sample_json_file):
    """Test handling of quote not found in file"""
    quote = {
        "text": "Nonexistent quote",
        "author": "Nonexistent author",
        "last_used_timestamp": 0
    }
    result = update_quote_usage(quote, sample_json_file)
    assert result is False

def test_update_quote_usage_invalid_input():
    """Test handling of invalid quote objects"""
    # None input
    assert update_quote_usage(None) is False
    
    # Missing required fields
    assert update_quote_usage({"text": "Missing author"}) is False
    assert update_quote_usage({"author": "Missing text"}) is False

def test_update_quote_usage_file_not_found():
    """Test handling of nonexistent file for update"""
    quote = {
        "text": "Some quote",
        "author": "Some author",
        "last_used_timestamp": 0
    }
    result = update_quote_usage(quote, "nonexistent_file.json")
    assert result is False
