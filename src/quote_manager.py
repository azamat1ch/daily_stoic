import json
import os
import random
import time
from typing import List, Dict, Any, Optional

# Define the expected path to the quotes file relative to this script's location
# Assumes quote_manager.py is in src/ and quotes.json is in data/
QUOTES_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'quotes.json')

def load_quotes_from_json(file_path: str = QUOTES_FILE_PATH) -> List[Dict[str, Any]]:
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
        raise FileNotFoundError(f"Error: Quotes file not found at {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, dict) or "quotes" not in data:
                print(f"Warning: Expected a dictionary with a 'quotes' key in {file_path}, but found {type(data)}. Returning empty list.")
                return []

            quotes_list = data["quotes"]
            if not isinstance(quotes_list, list):
                print(f"Warning: Expected 'quotes' key to contain a list in {file_path}, but got {type(quotes_list)}. Returning empty list.")
                return []

            if quotes_list and not all(isinstance(q, dict) for q in quotes_list):
                 print(f"Warning: Expected all items in the 'quotes' list in {file_path} to be dictionaries. Returning empty list.")
                 return []

            for quote in quotes_list:
                if "last_used_timestamp" not in quote:
                    # This should ideally not happen after the update script, but good fallback
                    quote["last_used_timestamp"] = 0
                elif not isinstance(quote["last_used_timestamp"], (int, float)):
                     # Ensure existing timestamps are numeric
                     print(f"Warning: Non-numeric timestamp found for quote: {quote.get('text', 'N/A')}. Setting to 0.")
                     quote["last_used_timestamp"] = 0

            return quotes_list
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred while reading {file_path}: {e}")
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
        print("Warning: Cannot select a quote from an empty list.")
        return None

    valid_quotes = [q for q in quotes if isinstance(q, dict) and "last_used_timestamp" in q and isinstance(q["last_used_timestamp"], (int, float))]
    if not valid_quotes:
        print("Warning: No valid quotes with 'last_used_timestamp' found.")
        return None

    min_timestamp = min(q["last_used_timestamp"] for q in valid_quotes)
    eligible_quotes = [q for q in valid_quotes if q["last_used_timestamp"] == min_timestamp]
    selected_quote = random.choice(eligible_quotes)
    return selected_quote

def update_quote_usage(selected_quote: Dict[str, Any], file_path: str = QUOTES_FILE_PATH) -> bool:
    """
    Updates the 'last_used_timestamp' for the selected quote in the JSON file.

    Args:
        selected_quote (Dict[str, Any]): The quote dictionary that was selected.
                                         Must contain 'text' and 'author' keys for matching.
        file_path (str): The path to the JSON file. Defaults to QUOTES_FILE_PATH.

    Returns:
        bool: True if the update was successful, False otherwise.
    """
    if not selected_quote or "text" not in selected_quote or "author" not in selected_quote:
        print("Error: Invalid selected_quote object provided for update.")
        return False

    try:
        # Read the entire current data structure
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, dict) or "quotes" not in data or not isinstance(data["quotes"], list):
            print(f"Error: Invalid structure in {file_path} during update. Expected {{'quotes': [...]}}.")
            return False

        quote_found = False
        current_timestamp = int(time.time())
        quotes_list = data["quotes"]
        for i, quote in enumerate(quotes_list):
            # Match based on text and author to uniquely identify the quote
            if isinstance(quote, dict) and quote.get("text") == selected_quote["text"] and quote.get("author") == selected_quote["author"]:
                # Ensure the timestamp exists before updating
                if "last_used_timestamp" not in data["quotes"][i]:
                     print(f"Warning: 'last_used_timestamp' missing for quote being updated. Adding it.")
                data["quotes"][i]["last_used_timestamp"] = current_timestamp
                quote_found = True
                break # Assume text/author combination is unique enough

        if not quote_found:
            print(f"Warning: Could not find the selected quote in {file_path} to update timestamp.")
            return False

        # Write the entire modified data back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2) # Use indent=2 for readability

        # print(f"Successfully updated timestamp for quote by {selected_quote['author']} in {file_path}.") # Keep this less verbose for validation
        return True

    except FileNotFoundError:
        print(f"Error: File not found at {file_path} during update.")
        return False
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path} during update: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during the update process: {e}")
        return False


# Example usage (optional, can be placed under if __name__ == "__main__":)
if __name__ == "__main__":
    try:
        all_quotes = load_quotes_from_json()
        print(f"Successfully loaded {len(all_quotes)} quotes.")
        if all_quotes:
            chosen_quote = select_quote(all_quotes)
            if chosen_quote:
                print("\nSelected Quote:")
                print(f"  Text: {chosen_quote.get('text', 'N/A')}")
                print(f"  Author: {chosen_quote.get('author', 'N/A')}")
                print(f"  Last Used (before update): {chosen_quote.get('last_used_timestamp', 'N/A')}")

                # Update the usage timestamp
                if update_quote_usage(chosen_quote):
                    print("Quote usage updated successfully.")
                    # Optionally reload and verify
                    # updated_quotes = load_quotes_from_json()
                    # for q in updated_quotes:
                    #     if q.get("text") == chosen_quote["text"] and q.get("author") == chosen_quote["author"]:
                    #         print(f"  Last Used (after update): {q.get('last_used_timestamp', 'N/A')}")
                    #         break
                else:
                    print("Failed to update quote usage.")
            else:
                print("Could not select a quote.")
        else:
            print("No quotes loaded to select from.")
    except Exception as e:
        print(f"An error occurred in the example usage: {e}")