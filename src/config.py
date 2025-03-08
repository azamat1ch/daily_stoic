#!/usr/bin/env python3
"""
Configuration module for the Daily Stoic project.
Handles loading and accessing environment variables and other configuration settings.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
env_path = BASE_DIR / '.env'
if env_path.exists():
    logger.info(f"Loading environment variables from {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    logger.warning(f"Environment file not found at {env_path}. Using default values where possible.")


class Config:
    """Configuration class to store and validate all config variables."""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
    
    # AI Services Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    # Font Configuration
    FONT_FILENAME = 'PTSerif-Regular.ttf' # Using the regular variant by default
    ITALIC_FONT_FILENAME = 'PTSerif-Italic.ttf' # Using the regular variant by default
    FONT_PATH = BASE_DIR / 'assets' / 'fonts' / FONT_FILENAME
    ITALIC_FONT_PATH = BASE_DIR / 'assets' / 'fonts' / ITALIC_FONT_FILENAME
    @classmethod
    def validate(cls):
        """
        Validate that all required configuration variables are set.
        Returns tuple: (is_valid, list_of_missing_vars)
        """
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_CHANNEL_ID',
            'GEMINI_API_KEY'
        ]
        
        missing_vars = [var for var in required_vars if getattr(cls, var) is None]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False, missing_vars
        
        return True, []
    
    @classmethod
    def get_absolute_db_path(cls):
        """Get the absolute path to the database file."""
        return BASE_DIR / cls.DATABASE_PATH


# Create a config instance for importing elsewhere
config = Config()

# Validate config on module import
is_valid, missing_vars = config.validate()
if not is_valid:
    logger.warning(
        "Configuration validation failed. Some features may not work correctly. "
        f"Please set the following environment variables: {', '.join(missing_vars)}"
    )
