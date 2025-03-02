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
    LLM_API_KEY = os.getenv('LLM_API_KEY')
    IMAGE_GEN_API_KEY = os.getenv('IMAGE_GEN_API_KEY')
    
    # Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/quotes.db')
    
    # Application Settings
    POST_TIME = os.getenv('POST_TIME', '07:00')  # Default to 7 AM UTC
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() in ('true', '1', 't')
    
    @classmethod
    def validate(cls):
        """
        Validate that all required configuration variables are set.
        Returns tuple: (is_valid, list_of_missing_vars)
        """
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_CHANNEL_ID'
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
