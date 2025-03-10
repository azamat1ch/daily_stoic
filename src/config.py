#!/usr/bin/env python3
"""
Configuration module for the Daily Stoic project.
Handles loading and accessing environment variables and other configuration settings.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Define project base directory
# Logging setup is moved to main.py to centralize configuration
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file relative to BASE_DIR
load_dotenv()


class Config:
    """Static configuration class holding application settings."""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
    
    # AI Services Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    # Data Files Configuration
    QUOTES_FILENAME = 'quotes.json'
    QUOTES_FILE_PATH = BASE_DIR / 'data' / QUOTES_FILENAME

    # Font Configuration
    FONT_FILENAME = 'PTSerif-Regular.ttf'
    ITALIC_FONT_FILENAME = 'PTSerif-Italic.ttf'
    FONT_PATH = BASE_DIR / 'assets' / 'fonts' / FONT_FILENAME
    ITALIC_FONT_PATH = BASE_DIR / 'assets' / 'fonts' / ITALIC_FONT_FILENAME

    # Log Configuration
    LOG_DIR = BASE_DIR / "logs"
    LOG_FILE = LOG_DIR / "daily_stoic_bot.log"

