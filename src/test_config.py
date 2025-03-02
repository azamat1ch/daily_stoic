#!/usr/bin/env python3
"""
Test script for the configuration module.
Run this to verify that environment variables are being loaded correctly.
"""

import logging
from config import config, BASE_DIR

def test_config():
    """Test the configuration loading and validation."""
    print("Daily Stoic Configuration Test")
    print("==============================")
    print(f"Project base directory: {BASE_DIR}")
    print("\nCurrent configuration values:")
    print(f"Telegram Bot Token: {'✓ Set' if config.TELEGRAM_BOT_TOKEN else '✗ Not set'}")
    print(f"Telegram Channel ID: {'✓ Set' if config.TELEGRAM_CHANNEL_ID else '✗ Not set'}")
    print(f"LLM API Key: {'✓ Set' if config.LLM_API_KEY else '✗ Not set'}")
    print(f"Image Generation API Key: {'✓ Set' if config.IMAGE_GEN_API_KEY else '✗ Not set'}")
    print(f"Database Path: {config.DATABASE_PATH}")
    print(f"Absolute Database Path: {config.get_absolute_db_path()}")
    print(f"Post Time: {config.POST_TIME}")
    print(f"Debug Mode: {config.DEBUG_MODE}")
    
    # Validate configuration
    is_valid, missing_vars = config.validate()
    print("\nConfiguration validation:", "✓ Passed" if is_valid else "✗ Failed")
    if not is_valid:
        print("Missing required variables:", ", ".join(missing_vars))

if __name__ == "__main__":
    # Disable logging for cleaner output
    logging.disable(logging.CRITICAL)
    test_config()
