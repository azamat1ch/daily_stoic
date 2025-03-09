import logging
import io
from telegram import Bot
from telegram.error import TelegramError
from PIL import Image # To type hint image_object

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
    if not all([bot_token, chat_id, image_object, caption_text]):
        logging.error("Missing required arguments for post_to_telegram.")
        return False

    logging.info(f"Attempting to post image to Telegram chat ID: {chat_id}")

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
        logging.info(f"Successfully posted image with caption to chat ID: {chat_id}")
        return True

    except TelegramError as e:
        logging.error(f"Telegram API error while sending photo to {chat_id}: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred in post_to_telegram: {e}")
        return False

if __name__ == '__main__':
    import asyncio
    from dotenv import load_dotenv
    import os
    load_dotenv()
    TEST_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TEST_CHAT_ID = os.getenv("TELEGRAM_TARGET_CHAT_ID")

    if TEST_BOT_TOKEN and TEST_CHAT_ID:
        dummy_image = Image.new('RGB', (600, 400), color = 'red')
        dummy_caption = "This is a test post from telegram_utils.py"
        async def run_test():
            success = await post_to_telegram(TEST_BOT_TOKEN, TEST_CHAT_ID, dummy_image, dummy_caption)
            if success:
                print("Test post sent successfully.")
            else:
                print("Test post failed.")

        asyncio.run(run_test())
    else:
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_TARGET_CHAT_ID in your .env file for testing.")