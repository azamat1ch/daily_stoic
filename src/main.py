import os
import json
import logging
import asyncio
import sys
from PIL import Image
from io import BytesIO
logger = logging.getLogger(__name__)

try:
    from src.config import Config
    from src.quote_manager import select_next_quote
    from src.gemini_utils import generate_image_prompt, generate_explanation, generate_image_gemini, choose_best_image
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
        'GEMINI_API_KEY': Config.GEMINI_API_KEY,
        'GCS_BUCKET_NAME': Config.GCS_BUCKET_NAME # Added GCS bucket check
    }
    missing_vars = [name for name, value in required_vars.items() if value is None]

    if missing_vars:
        logger.error(f"Missing critical configuration variables: {', '.join(missing_vars)}. Check .env file and src/config.py.")
        return False

    # Check if essential files/dirs exist (Local quotes file check removed)
    essential_paths = {
        # "Quotes File": Config.QUOTES_FILE_PATH, # Removed - state is in GCS
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

        # --- 1. Select Next Quote (Handles GCS Load/Select/Save) ---
        logger.info("Selecting next quote using GCS state...")
        selected_quote = select_next_quote() # This function now handles GCS interaction

        if not selected_quote:
            # Errors during loading, selection, or saving are logged within select_next_quote
            logger.error("Failed to select next quote (check quote_manager logs for GCS issues). Halting workflow.")
            return # Exit workflow if quote selection/update fails

        logger.info(f"Selected quote: \"{selected_quote['text'][:50]}...\" by {selected_quote['author']}")
        quote_text = selected_quote['text']
        author = selected_quote['author']

        # --- 2. Generate Content with Gemini ---
        logger.info("Generating content using Gemini API...")
        num_images_to_generate = 4
        logger.info(f"Generating {num_images_to_generate} images based on prompt...")
        generated_images_data = [] # List to store tuples of (bytes, PIL.Image)

        for i in range(num_images_to_generate):
            # 2a. Generate Image Prompt
            logger.info(f"Generating image prompt {i+1}/{num_images_to_generate}...")
            image_prompt = generate_image_prompt(quote_text)
            if not image_prompt:
                logger.error(f"Failed to generate image prompt {i+1}/{num_images_to_generate} (check Gemini API key, quota, and prompt). Halting workflow.")
                return
            logger.info(f"Generated image prompt: {image_prompt[:100]}...")
            # 2b. Generate Image
            logger.info(f"Generating image {i+1}/{num_images_to_generate}...")
            image_data_bytes = generate_image_gemini(image_prompt)
            if not image_data_bytes:
                # Log error but potentially continue if other images were generated?
                # For now, halt if any image fails. Could be made more robust.
                logger.error(f"Failed to generate image {i+1} (check Gemini API key, quota, and image prompt). Halting workflow.")
                return
            try:
                # Store both bytes and PIL Image object
                pil_image = Image.open(BytesIO(image_data_bytes))
                pil_image.save(f"test_image_{i+1}.png")
                generated_images_data.append({'bytes': image_data_bytes, 'pil': pil_image})
                logger.info(f"Image {i+1} generated and processed successfully.")
            except Exception as e:
                logger.error(f"Failed to process generated image {i+1} data into PIL Image: {e}. Halting workflow.", exc_info=True)
                return

        if len(generated_images_data) != num_images_to_generate:
             logger.error(f"Expected {num_images_to_generate} images, but only processed {len(generated_images_data)}. Halting workflow.")
             return

        # 2c. Choose the Best Image
        logger.info("Choosing the best image using Gemini multimodal analysis...")
        pil_images_list = [img_data['pil'] for img_data in generated_images_data]
        best_image_index = choose_best_image(quote_text, pil_images_list)

        if best_image_index is None:
            logger.warning("Failed to determine the best image via Gemini. Falling back to using the first generated image.")
            best_image_index = 0 # Fallback to the first image
        else:
             logger.info(f"Gemini selected image at index {best_image_index} as the best.")

        # Select the *bytes* of the chosen image for embedding
        chosen_image_data_bytes = generated_images_data[best_image_index]['bytes']
        logger.info(f"Selected image data (bytes) from index {best_image_index}.")

        # 2d. Generate Explanation (Moved after image selection, but could be parallel)
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
            image_data=chosen_image_data_bytes, # Use the chosen image bytes
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