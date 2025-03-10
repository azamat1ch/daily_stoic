import os
import json
import logging
import asyncio
import sys
logger = logging.getLogger(__name__)

try:
    from src.config import Config
    from src.quote_manager import load_quotes_from_json, select_quote, update_quote_usage
    from src.gemini_utils import generate_image_prompt, generate_explanation, generate_image_gemini
    from src.image_utils import embed_text_on_image
    from src.telegram_utils import post_to_telegram
except ImportError as e:
    # Log error before exiting
    logger.critical(f"Error importing critical modules: {e}. Ensure all required files exist and PYTHONPATH is set correctly.", exc_info=True)
    sys.exit(1) # Use sys.exit

def validate_configuration():
    """Validates that essential configuration variables are loaded."""
    logger.info("Validating configuration...")
    required_vars = {
        'TELEGRAM_BOT_TOKEN': Config.TELEGRAM_BOT_TOKEN,
        'TELEGRAM_CHANNEL_ID': Config.TELEGRAM_CHANNEL_ID,
        'GEMINI_API_KEY': Config.GEMINI_API_KEY
    }
    missing_vars = [name for name, value in required_vars.items() if value is None]

    if missing_vars:
        logger.error(f"Missing critical configuration variables: {', '.join(missing_vars)}. Check .env file and src/config.py.")
        return False

    # Check if essential files/dirs exist
    essential_paths = {
        "Quotes File": Config.QUOTES_FILE_PATH,
        "Regular Font": Config.FONT_PATH,
        "Italic Font": Config.ITALIC_FONT_PATH,
        "Log Directory": Config.LOG_DIR # Check dir, not file which might not exist yet
    }
    missing_paths = []
    for name, path in essential_paths.items():
        if not path.exists():
             # Special check for log dir - attempt creation later in setup_logging
             if name == "Log Directory":
                 continue # Don't fail validation here, handle in logging setup
             missing_paths.append(f"{name} (Expected at: {path})")

    if missing_paths:
        logger.error(f"Missing essential files/directories: {'; '.join(missing_paths)}")
        return False


    logger.info("Configuration validated successfully.")
    return True


async def main_workflow():
    """Orchestrates the daily stoic post generation and sending."""
    logger.info("Starting main workflow...")

    # Configuration is accessed directly via Config class
    # Validation happens at the start of the script execution

    try:
        # --- Core Workflow Logic ---

        # --- 1. Load and Select Quote ---
        logger.info(f"Loading quotes from {Config.QUOTES_FILE_PATH}...")
        try:
            # Use path from Config
            all_quotes = load_quotes_from_json(str(Config.QUOTES_FILE_PATH))
        except FileNotFoundError:
            # Error logged in load_quotes_from_json
            logger.error("Halting workflow because quotes file was not found.")
            return
        except (json.JSONDecodeError, Exception) as e:
            # Error logged in load_quotes_from_json
            logger.error(f"Failed to load or parse quotes: {e}. Halting workflow.")
            return

        if not all_quotes:
            logger.error("No valid quotes loaded from file (check format and content). Halting workflow.")
            return

        logger.info(f"Loaded {len(all_quotes)} quotes. Selecting one...")
        selected_quote = select_quote(all_quotes) # Pass the list of quotes

        if not selected_quote:
            logger.error("Failed to select a suitable quote (check timestamps and quote list). Halting workflow.")
            return # Exit workflow if quote selection fails
        logger.info(f"Selected quote: \"{selected_quote['text'][:50]}...\" by {selected_quote['author']}")
        quote_text = selected_quote['text']
        author = selected_quote['author']

        # --- 2. Generate Content with Gemini ---
        logger.info("Generating content using Gemini API...")
        # 2a. Generate Image Prompt
        logger.info("Generating image prompt...")
        image_prompt = generate_image_prompt(quote_text)
        if not image_prompt:
            logger.error("Failed to generate image prompt (check Gemini API key, quota, and prompt). Halting workflow.")
            return
        logger.info(f"Generated image prompt: {image_prompt[:100]}...")
        # 2b. Generate Image
        logger.info("Generating image...")
        # Use updated function name
        image_data = generate_image_gemini(image_prompt)
        if not image_data:
            logger.error("Failed to generate image (check Gemini API key, quota, and image prompt). Halting workflow.")
            return
        logger.info("Image generated successfully (data received).")
        # 2c. Generate Explanation
        logger.info("Generating explanation...")
        explanation = generate_explanation(quote_text)
        if not explanation:
            logger.error("Failed to generate explanation (check Gemini API key, quota). Halting workflow.")
            return
        logger.info(f"Generated explanation: {explanation[:100]}...")

        # --- 3. Embed Text on Image ---
        logger.info("Embedding text onto the generated image...")
        final_image_object = embed_text_on_image(
            image_data=image_data,
            quote_text=quote_text,
            author=author,
        )
        if not final_image_object:
            logger.error("Failed to embed text onto image (check image data and font files). Halting workflow.")
            return
        logger.info("Text embedded successfully onto image.")

        # --- 4. Post to Telegram ---
        logger.info("Preparing to post to Telegram...")
        # Use Config for bot token and chat ID
        post_success = await post_to_telegram(
            bot_token=Config.TELEGRAM_BOT_TOKEN,
            chat_id=Config.TELEGRAM_CHANNEL_ID,
            image_object=final_image_object,
            caption_text=explanation # Use the generated explanation as caption
        )
        if post_success:
            logger.info("Successfully posted to Telegram.")
            # --- 5. Update Quote Usage ---
            logger.info(f"Updating usage timestamp for quote by {selected_quote['author']}...")
            # Use path from Config
            update_success = update_quote_usage(selected_quote, str(Config.QUOTES_FILE_PATH))
            if update_success:
                logger.info("Quote usage timestamp updated successfully.")
            else:
                logger.warning("Failed to update quote usage timestamp (check file permissions?).") # Log as warning, workflow succeeded overall
        else:
            logger.error("Failed to post to Telegram (check bot token, chat ID, and network).")

        # --- End of Core Workflow ---
        logger.info("Core workflow steps completed.")

    except Exception as e:
        logger.exception("An unexpected error occurred during the main workflow execution.")
    logger.info("Main workflow execution attempt finished.")
def setup_logging():
    """Configures logging to console and file."""
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_level = logging.INFO # Or load from config/env if needed

    # Root logger setup
    root_logger = logging.getLogger() # Get root logger to configure handlers
    root_logger.setLevel(log_level)

    # Console Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    # Avoid adding handlers multiple times if script is re-run in same process
    if not root_logger.hasHandlers():
        root_logger.addHandler(stream_handler)
    elif not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
         root_logger.addHandler(stream_handler) # Add if missing

    # File Handler (optional, consider log rotation for long-running apps)
    # Ensure 'logs' directory exists or handle creation
    # Use Log directory from Config
    log_dir = Config.LOG_DIR
    if not os.path.exists(log_dir):
        try:
            # Use pathlib's mkdir
            log_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            # Use logger instead of print
            logger.error(f"Error creating log directory {log_dir}: {e}. File logging disabled.")
            # Fallback to console only if directory creation fails
            return # Exit setup if log dir fails
    # Use Log file path from Config
    log_file_path = Config.LOG_FILE
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(log_formatter)

    # Add file handler only if not already present
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == str(log_file_path) for h in root_logger.handlers):
        root_logger.addHandler(file_handler)

    logger.info(f"Logging configured (Console & File: {log_file_path})")

if __name__ == "__main__":
    setup_logging()
    logger.info("Daily Stoic Bot script started.")

    # Validate configuration before running workflow
    if validate_configuration():
        try:
            asyncio.run(main_workflow())
        except Exception as e:
            logger.critical(f"Critical error during main workflow execution: {e}", exc_info=True)
    else:
        logger.error("Halting script due to configuration validation errors.")


    logger.info("Daily Stoic Bot script finished.")