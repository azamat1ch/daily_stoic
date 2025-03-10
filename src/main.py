import os
import json
import logging
import asyncio
from dotenv import load_dotenv

# Import project-specific modules
try:
    from src.config import config
    from src.quote_manager import load_quotes_from_json, select_quote, update_quote_usage 
    from src.gemini_utils import generate_image_prompt, generate_explanation, generate_image_gemini_exp 
    from src.image_utils import embed_text_on_image 
    from src.telegram_utils import post_to_telegram 
except ImportError as e:
    logging.error(f"Error importing modules: {e}. Ensure all required files exist and PYTHONPATH is set correctly.")
    exit(1)

# --- Configuration Loading ---
def load_configuration():
    """Loads configuration from .env file and config.py"""
    logging.info("Loading configuration...")
    # Load environment variables from .env file
    load_dotenv()

    # Accessing config variables (examples)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    target_chat_id = os.getenv("TELEGRAM_TARGET_CHAT_ID")
    #font_path = config.FONT_PATH
    quotes_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'quotes.json')

    if not all([bot_token, gemini_api_key, target_chat_id]):
        logging.error("Missing critical environment variables (TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, TELEGRAM_TARGET_CHAT_ID). Check .env file.")
        # In a real scenario, might exit or raise an exception
        # For now, just log the error.
        # exit(1) # Uncomment if execution should halt

    logging.info("Configuration loaded successfully.")
    # Return loaded config values if needed elsewhere, or just confirm loading
    return {
        "bot_token": bot_token,
        "gemini_api_key": gemini_api_key,
        "target_chat_id": target_chat_id,
        #"font_path": font_path,
        "quotes_file": quotes_file
    }

# --- Main Workflow (Async) ---
async def main_workflow():
    """Orchestrates the daily stoic post generation and sending, with error handling."""
    logging.info("Starting main workflow...")

    # Load configuration first
    app_config = load_configuration()
    if not app_config:
        logging.error("Halting workflow due to configuration loading issues.")
        return

    try:
        # --- Core Workflow Logic ---

        # --- 1. Load and Select Quote ---
        logging.info("Loading quotes...")
        try:
            all_quotes = load_quotes_from_json(app_config['quotes_file'])
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            logging.error(f"Failed to load quotes: {e}. Halting workflow.")
            return

        if not all_quotes:
            logging.error("No quotes loaded from file. Halting workflow.")
            return

        logging.info(f"Loaded {len(all_quotes)} quotes. Selecting one...")
        selected_quote = select_quote(all_quotes) # Pass the list of quotes

        if not selected_quote:
            logging.error("Failed to select a quote from the loaded list. Halting workflow.")
            return # Exit workflow if quote selection fails
        logging.info(f"Selected quote: \"{selected_quote['text'][:50]}...\" by {selected_quote['author']}")
        quote_text = selected_quote['text']
        author = selected_quote['author']

        # --- 2. Generate Content with Gemini ---
        logging.info("Generating content using Gemini API...")
        # 2a. Generate Image Prompt
        logging.info("Generating image prompt...")
        image_prompt = generate_image_prompt(quote_text)
        if not image_prompt:
            logging.error("Failed to generate image prompt. Halting workflow.")
            return
        logging.info(f"Generated image prompt: {image_prompt[:100]}...")
        # 2b. Generate Image
        logging.info("Generating image...")
        image_data = generate_image_gemini_exp(image_prompt)
        if not image_data:
            logging.error("Failed to generate image. Halting workflow.")
            return
        logging.info("Image generated successfully (data received).")
        # 2c. Generate Explanation
        logging.info("Generating explanation...")
        explanation = generate_explanation(quote_text)
        if not explanation:
            logging.error("Failed to generate explanation. Halting workflow.")
            return
        logging.info(f"Generated explanation: {explanation[:100]}...")

        # --- 3. Embed Text on Image ---
        logging.info("Embedding text onto the generated image...")
        final_image_object = embed_text_on_image(
            image_data=image_data,
            quote_text=quote_text,
            author=author,
        )
        if not final_image_object:
            logging.error("Failed to embed text onto image. Halting workflow.")
            return
        logging.info("Text embedded successfully onto image.")

        # --- 4. Post to Telegram ---
        logging.info("Preparing to post to Telegram...")
        caption = f"{explanation}\n\n---\nQuote: \"{quote_text}\" - {author}"
        post_success = await post_to_telegram(
            bot_token=app_config['bot_token'],
            chat_id=app_config['target_chat_id'],
            image_object=final_image_object,
            caption_text=caption
        )
        if post_success:
            logging.info("Successfully posted to Telegram.")
            # --- 5. Update Quote Usage ---
            logging.info(f"Updating usage timestamp for quote ID {selected_quote.get('id', 'N/A')}...")
            update_success = update_quote_usage(selected_quote, app_config['quotes_file'])
            if update_success:
                logging.info("Quote usage timestamp updated successfully.")
            else:
                logging.warning("Failed to update quote usage timestamp.") # Log as warning, workflow succeeded overall
        else:
            logging.error("Failed to post to Telegram.")

        # --- End of Core Workflow ---
        logging.info("Core workflow steps completed.")

    except Exception as e:
        logging.exception("An unexpected error occurred during the main workflow execution.")
        # The script will continue to the final log message unless this exception is critical
    logging.info("Main workflow execution attempt finished.")
# --- Logging Setup ---
def setup_logging():
    """Configures logging to console and file."""
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_level = logging.INFO # Or load from config/env if needed

    # Root logger setup
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Console Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    # File Handler (optional, consider log rotation for long-running apps)
    # Ensure 'logs' directory exists or handle creation
    log_dir = "logs"
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except OSError as e:
            print(f"Error creating log directory {log_dir}: {e}")
            # Fallback to console only if directory creation fails
            return
    file_handler = logging.FileHandler(os.path.join(log_dir, "daily_stoic_bot.log"))
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    logging.info("Logging configured (Console & File)")

# --- Script Execution ---
if __name__ == "__main__":
    setup_logging()
    logging.info("Daily Stoic Bot script started.")

    try:
        asyncio.run(main_workflow())
    except Exception as e:
        logging.critical(f"Critical error in main execution block: {e}", exc_info=True)

    logging.info("Daily Stoic Bot script finished.")