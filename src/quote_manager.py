import json
import os
import random
import time
import logging
from typing import List, Dict, Any, Optional

from src.config import Config
logger = logging.getLogger(__name__)
DEFAULT_QUOTES_FILE_PATH = Config.QUOTES_FILE_PATH

def load_quotes_from_json(file_path: str = str(DEFAULT_QUOTES_FILE_PATH)) -> List[Dict[str, Any]]:
    """
    Loads quotes from a JSON file structured as {"quotes": [...]}.

    Args:
        file_path (str): The path to the JSON file containing quotes.
                         Defaults to QUOTES_FILE_PATH.

    Returns:
        List[Dict[str, Any]]: A list of quote dictionaries extracted from the
                              "quotes" key. Returns an empty list if the file
                              is not found, is invalid JSON, or doesn't follow
                              the expected structure.

    Raises:
        FileNotFoundError: If the specified file_path does not exist.
        json.JSONDecodeError: If the file content is not valid JSON.
        Exception: For other potential file reading errors.
    """
    if not os.path.exists(file_path):
        logger.error(f"Quotes file not found at {file_path}")
        raise FileNotFoundError(f"Quotes file not found at {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, dict) or "quotes" not in data or not isinstance(data.get("quotes"), list):
                logger.warning(f"Invalid JSON structure in {file_path}. Expected {{'quotes': [...]}}. Found type {type(data)} with quotes type {type(data.get('quotes'))}. Returning empty list.")
                return []

            quotes_list = data["quotes"]

            # Basic check: ensure all items are dicts if list is not empty
            if quotes_list and not all(isinstance(q, dict) for q in quotes_list):
                 logger.warning(f"Not all items in the 'quotes' list in {file_path} are dictionaries. Returning empty list.")
                 return []

            for quote in quotes_list:
                if "last_used_timestamp" not in quote:
                    # This should ideally not happen after the update script, but good fallback
                    quote["last_used_timestamp"] = 0
                elif not isinstance(quote["last_used_timestamp"], (int, float)):
                     # Ensure existing timestamps are numeric
                     logger.warning(f"Non-numeric timestamp found for quote: '{quote.get('text', 'N/A')[:50]}...'. Setting to 0.")
                     quote["last_used_timestamp"] = 0

            return quotes_list
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while reading {file_path}: {e}", exc_info=True)
        raise

def select_quote(quotes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Selects a quote from the list, prioritizing those least recently used.

    Args:
        quotes (List[Dict[str, Any]]): A list of quote dictionaries,
                                       each expected to have a 'last_used_timestamp'.

    Returns:
        Optional[Dict[str, Any]]: The selected quote dictionary, or None if the
                                  input list is empty or invalid.
    """
    if not quotes:
        logger.warning("Cannot select a quote from an empty list.")
        return None

    valid_quotes = [q for q in quotes if isinstance(q, dict) and "last_used_timestamp" in q and isinstance(q["last_used_timestamp"], (int, float))]
    if not valid_quotes:
        # This might happen if load_quotes_from_json returned an empty list due to format errors
        logger.warning("No valid quotes with numeric 'last_used_timestamp' found in the provided list.")
        return None

    min_timestamp = min(q["last_used_timestamp"] for q in valid_quotes)
    eligible_quotes = [q for q in valid_quotes if q["last_used_timestamp"] == min_timestamp]
    selected_quote = random.choice(eligible_quotes)
    return selected_quote

def update_quote_usage(selected_quote: Dict[str, Any], file_path: str = str(DEFAULT_QUOTES_FILE_PATH)) -> bool:
    """
    Updates the 'last_used_timestamp' for the selected quote in the JSON file.

    Args:
        selected_quote (Dict[str, Any]): The quote dictionary that was selected.
                                         Must contain 'text' and 'author' keys for matching.
        file_path (str): The path to the JSON file. Defaults to QUOTES_FILE_PATH.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    if not selected_quote or not isinstance(selected_quote, dict) or "text" not in selected_quote or "author" not in selected_quote:
        logger.error(f"Invalid selected_quote object provided for update: {selected_quote}")
        return False

    try:
        # Read the entire current data structure
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, dict) or "quotes" not in data or not isinstance(data.get("quotes"), list):
            logger.error(f"Invalid structure in {file_path} during update. Expected {{'quotes': [...]}}. Found type {type(data)} with quotes type {type(data.get('quotes'))}.")
            return False

        quote_found = False
        current_timestamp = int(time.time())
        quotes_list = data["quotes"]
        for i, quote in enumerate(quotes_list):
            # Match based on text and author to uniquely identify the quote
            if isinstance(quote, dict) and quote.get("text") == selected_quote["text"] and quote.get("author") == selected_quote["author"]:
                # Ensure the timestamp exists before updating
                if "last_used_timestamp" not in data["quotes"][i]:
                     logger.warning(f"Updating quote that was missing 'last_used_timestamp'. Adding it now.")
                data["quotes"][i]["last_used_timestamp"] = current_timestamp
                quote_found = True
                break # Assume text/author combination is unique enough

        if not quote_found:
            # This could happen if the quotes file was modified between selection and update
            logger.warning(f"Could not find the selected quote (Author: {selected_quote.get('author', 'N/A')}, Text: '{selected_quote.get('text', 'N/A')[:50]}...') in {file_path} to update timestamp.")
            return False

        # Write the entire modified data back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2) # Use indent=2 for readability

        # logger.info(f"Successfully updated timestamp for quote by {selected_quote['author']} in {file_path}.") # Keep this less verbose for normal operation
        return True

    except FileNotFoundError:
        logger.error(f"File not found at {file_path} during update.")
        return False
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path} during update: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during the update process: {e}", exc_info=True)
        return False


# Example usage (optional, can be placed under if __name__ == "__main__":)
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    try:
        # Use default path from config for test
        all_quotes = load_quotes_from_json()
        logger.info(f"Successfully loaded {len(all_quotes)} quotes for test.")
        if all_quotes:
            chosen_quote = select_quote(all_quotes)
            if chosen_quote:
                logger.info(f"  Selected Quote (Test):")
                logger.info(f"  Text: {chosen_quote.get('text', 'N/A')}")
                logger.info(f"  Author: {chosen_quote.get('author', 'N/A')}")
                logger.info(f"  Last Used (before update): {chosen_quote.get('last_used_timestamp', 'N/A')}")

                # Update the usage timestamp
                # Use default path from config for test update
                if update_quote_usage(chosen_quote):
                    logger.info("Quote usage updated successfully (Test).")
                    # Optionally reload and verify
                    # updated_quotes = load_quotes_from_json()
                    # for q in updated_quotes:
                    #     if q.get("text") == chosen_quote["text"] and q.get("author") == chosen_quote["author"]:
                    #         print(f"  Last Used (after update): {q.get('last_used_timestamp', 'N/A')}")
                    #         break
                else:
                    logger.error("Failed to update quote usage (Test).")
            else:
                logger.warning("Could not select a quote (Test).")
        else:
            logger.warning("No quotes loaded to select from (Test).")
    except Exception as e:
        logger.error(f"An error occurred in the example usage: {e}", exc_info=True)