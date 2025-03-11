import json
import os
import random
import time
import logging
from typing import List, Dict, Any, Optional

from google.cloud import storage
from google.api_core.exceptions import NotFound, Forbidden

from src.config import Config

logger = logging.getLogger(__name__)

# --- Configuration ---
GCS_BUCKET_NAME = Config.GCS_BUCKET_NAME
QUOTES_BLOB_NAME = "quotes.json"  # Name of the file in GCS
# LOCAL_QUOTES_PATH is removed as fallback is disabled

# --- GCS Helper Functions ---

def _get_gcs_blob() -> Optional[storage.Blob]:
    """Initializes GCS client and returns the blob object for quotes.json."""
    if not GCS_BUCKET_NAME:
        logger.error("GCS_BUCKET_NAME is not configured.")
        return None
    try:
        # Uses Application Default Credentials (ADC)
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(QUOTES_BLOB_NAME)
        return blob
    except Exception as e:
        logger.error(f"Failed to initialize GCS client or get blob: {e}", exc_info=True)
        return None

# _load_quotes_from_local_fallback function is removed

def _load_quotes_from_gcs() -> List[Dict[str, Any]]:
    """Loads quotes data strictly from GCS. Returns empty list on any error."""
    blob = _get_gcs_blob()
    if not blob:
        logger.error("Failed to get GCS blob object. Cannot load quotes.")
        return [] # No fallback

    try:
        if not blob.exists():
            logger.error(f"Quotes file '{QUOTES_BLOB_NAME}' not found in GCS bucket '{GCS_BUCKET_NAME}'. Cannot load quotes.")
            return [] # No fallback, file must exist

        logger.info(f"Loading quotes from GCS: gs://{GCS_BUCKET_NAME}/{QUOTES_BLOB_NAME}")
        json_string = blob.download_as_text()
        data = json.loads(json_string)

        if not isinstance(data, dict) or "quotes" not in data or not isinstance(data.get("quotes"), list):
            logger.error(f"Invalid JSON structure in GCS blob gs://{GCS_BUCKET_NAME}/{QUOTES_BLOB_NAME}. Expected {{'quotes': [...]}}. Cannot load quotes.")
            return [] # No fallback for invalid structure

        quotes_list = data["quotes"]
        # Ensure timestamps are present and numeric
        for quote in quotes_list:
            if "last_used_timestamp" not in quote:
                quote["last_used_timestamp"] = 0
            elif not isinstance(quote["last_used_timestamp"], (int, float)):
                logger.warning(f"Non-numeric timestamp in GCS data for quote: '{quote.get('text', 'N/A')[:50]}...'. Setting to 0.")
                quote["last_used_timestamp"] = 0
        return quotes_list

    except Forbidden as e:
        logger.error(f"Permission denied accessing GCS bucket '{GCS_BUCKET_NAME}' or blob '{QUOTES_BLOB_NAME}'. Check credentials/permissions. Error: {e}", exc_info=True)
        return [] # No fallback
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from GCS blob gs://{GCS_BUCKET_NAME}/{QUOTES_BLOB_NAME}: {e}")
        return [] # No fallback
    except Exception as e:
        logger.error(f"Unexpected error loading quotes from GCS: {e}", exc_info=True)
        return [] # No fallback

def _save_quotes_to_gcs(data: Dict[str, Any]) -> bool:
    """Saves the provided data dictionary (expected {'quotes': [...]}) to GCS as JSON."""
    blob = _get_gcs_blob()
    if not blob:
        logger.error("Failed to get GCS blob. Cannot save quotes.")
        return False

    if not isinstance(data, dict) or "quotes" not in data:
        logger.error(f"Invalid data structure for saving to GCS. Expected {{'quotes': [...]}}.")
        return False

    try:
        json_string = json.dumps(data, indent=2)
        blob.upload_from_string(json_string, content_type='application/json')
        logger.info(f"Successfully saved quotes state to GCS: gs://{GCS_BUCKET_NAME}/{QUOTES_BLOB_NAME}")
        return True
    except Forbidden as e:
        logger.error(f"Permission denied writing to GCS. Check credentials/permissions. Error: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Unexpected error saving quotes to GCS: {e}", exc_info=True)
        return False

# --- Core Quote Selection Logic ---

def _select_least_recently_used_quote(quotes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Selects a quote from the list, prioritizing those least recently used."""
    if not quotes:
        logger.warning("Cannot select quote from empty list.")
        return None

    valid_quotes = [q for q in quotes if isinstance(q, dict) and "last_used_timestamp" in q and isinstance(q["last_used_timestamp"], (int, float))]
    if not valid_quotes:
        logger.warning("No valid quotes with numeric 'last_used_timestamp' found.")
        return None

    min_timestamp = min(q["last_used_timestamp"] for q in valid_quotes)
    eligible_quotes = [q for q in valid_quotes if q["last_used_timestamp"] == min_timestamp]
    selected_quote = random.choice(eligible_quotes)
    logger.info(f"Selected quote by {selected_quote.get('author', 'N/A')} (Last used: {min_timestamp})")
    return selected_quote

def select_next_quote() -> Optional[Dict[str, Any]]:
    """
    Loads quotes from GCS, selects the next quote, updates its timestamp,
    saves the state back to GCS, and returns the selected quote.
    Requires the quotes file to exist in GCS. Returns None on failure.
    """
    logger.info("Selecting next quote using GCS state...")
    quotes_data_list = _load_quotes_from_gcs() # Now strictly loads from GCS or returns []

    if not quotes_data_list:
        # Error logged within _load_quotes_from_gcs if loading failed
        logger.error("Failed to load quotes from GCS. Cannot select.")
        return None

    selected_quote = _select_least_recently_used_quote(quotes_data_list)

    if not selected_quote:
        logger.warning("Could not select a suitable quote from loaded data.")
        return None

    # Update timestamp in memory
    quote_found_in_memory = False
    current_timestamp = int(time.time())
    for i, quote in enumerate(quotes_data_list):
        # Match based on text and author
        if isinstance(quote, dict) and quote.get("text") == selected_quote["text"] and quote.get("author") == selected_quote["author"]:
            logger.debug(f"Updating timestamp for selected quote (index {i}) in memory.")
            quotes_data_list[i]["last_used_timestamp"] = current_timestamp
            quote_found_in_memory = True
            break

    if not quote_found_in_memory:
        logger.error("Selected quote not found in memory list for timestamp update. Aborting GCS save.")
        return None # State wasn't updated

    # Save updated list back to GCS
    updated_data_to_save = {"quotes": quotes_data_list}
    if _save_quotes_to_gcs(updated_data_to_save):
        logger.info(f"Successfully updated quote usage state in GCS for quote by {selected_quote.get('author', 'N/A')}.")
        return selected_quote # Return the selected quote
    else:
        logger.error("Failed to save updated quotes state to GCS. Selection made, but state update failed.")
        # Return None to indicate the full process didn't complete successfully.
        return None


# --- Main execution block for local testing ---
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Ensure environment variables are loaded (e.g., from a .env file)
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env') # Assumes .env is in project root
    load_dotenv(dotenv_path=env_path)
    # Re-fetch GCS_BUCKET_NAME
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME") or Config.GCS_BUCKET_NAME
    if not GCS_BUCKET_NAME:
         logger.error("GCS_BUCKET_NAME not found in environment variables or config. Please set it in your .env file.")
         exit(1)

    logger.info(f"--- Running Quote Manager Test (Bucket: {GCS_BUCKET_NAME}, No Fallback) ---")

    try:
        # Crucial: Ensure quotes.json exists in the GCS bucket before running this test
        logger.info(f"Attempting to select quote. Ensure gs://{GCS_BUCKET_NAME}/{QUOTES_BLOB_NAME} exists and is accessible.")
        next_quote = select_next_quote()

        if next_quote:
            print("\n--- Selected Quote ---")
            print(f"Text: {next_quote.get('text')}")
            print(f"Author: {next_quote.get('author')}")
            print(f"Timestamp (before update): {next_quote.get('last_used_timestamp')}")
            print("----------------------\n")
            logger.info("Quote selection and GCS update process completed successfully (as reported by the function).")
        else:
            logger.warning("select_next_quote() returned None. Check logs for errors (GCS file missing/inaccessible, invalid format, selection error, or save failure).")

    except Exception as e:
        logger.error(f"An error occurred during the test execution: {e}", exc_info=True)

    logger.info("--- Quote Manager Test Finished ---")
