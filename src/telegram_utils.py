import logging
import io
from telegram import Bot
from telegram.error import TelegramError
from PIL import Image # To type hint image_object
import asyncio 
import os
from src.config import Config

# Setup logger
logger = logging.getLogger(__name__)
async def post_to_telegram(bot_token: str, chat_id: str, image_object: Image.Image, caption_text: str) -> bool:
    """
    Sends a photo with a caption to the specified Telegram chat using python-telegram-bot (v20+).

    Args:
        bot_token: The Telegram Bot Token.
        chat_id: The target chat ID (can be a user ID or channel/group ID like '@channelusername').
        image_object: A PIL Image object to send.
        caption_text: The caption for the photo.

    Returns:
        True if the message was sent successfully, False otherwise.
    """
    # Added type check for image_object
    if not all([bot_token, chat_id, isinstance(image_object, Image.Image), caption_text]):
        logger.error(f"Missing or invalid required arguments for post_to_telegram. Got token: {'yes' if bot_token else 'no'}, chat_id: {chat_id}, image: {type(image_object)}, caption: {'yes' if caption_text else 'no'}")
        return False

    logger.info(f"Attempting to post image to Telegram chat ID: {chat_id}")

    try:
        bot = Bot(token=bot_token)

        # Convert PIL Image object to bytes in memory
        img_byte_arr = io.BytesIO()
        # Save the image to the byte array, specify format (e.g., PNG or JPEG)
        image_object.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0) # Rewind the buffer to the beginning

        # Note: send_photo expects the photo data as bytes or a file path.
        await bot.send_photo(
            chat_id=chat_id,
            photo=img_byte_arr,
            caption=caption_text
        )
        logger.info(f"Successfully posted image with caption to chat ID: {chat_id}")
        return True

    except TelegramError as e:
        logger.error(f"Telegram API error while sending photo to {chat_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred in post_to_telegram: {e}", exc_info=True)
        return False

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger.info("Running telegram_utils.py directly for testing...")


    TEST_BOT_TOKEN = Config.TELEGRAM_BOT_TOKEN
    TEST_CHAT_ID = Config.TELEGRAM_CHANNEL_ID

    logger.info(f"Test Config - Bot Token Loaded: {'Yes' if TEST_BOT_TOKEN else 'No'}")
    logger.info(f"Test Config - Chat ID Loaded: {'Yes' if TEST_CHAT_ID else 'No'}")

    if TEST_BOT_TOKEN and TEST_CHAT_ID:
        try:
            dummy_image = Image.new('RGB', (600, 400), color = 'red')
            dummy_caption = "This is a test post from telegram_utils.py"

            async def run_test():
                logger.info(f"Attempting test post to chat ID: {TEST_CHAT_ID}")
                success = await post_to_telegram(TEST_BOT_TOKEN, TEST_CHAT_ID, dummy_image, dummy_caption)
                if success:
                    logger.info("Test post sent successfully.")
                else:
                    logger.error("Test post failed. Check logs above for details (API errors, etc.).")

            # Run the async test function
            asyncio.run(run_test())
            logger.info("Test execution finished.")

        except Exception as e:
             logger.error(f"An error occurred during the test setup or execution: {e}", exc_info=True)

    else:
        logger.warning("Testing skipped: Required configuration (TELEGRAM_BOT_TOKEN and/or TELEGRAM_CHANNEL_ID) not found in Config. Check .env file.")