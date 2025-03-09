def test_config_display(capsys):
    """Test configuration display functionality and capture its output."""
    # Your original function
    from src.config import config, BASE_DIR
    
    # Disable logging for cleaner output
    import logging
    logging.disable(logging.CRITICAL)
    
    # Original code from test_config.py
    print("Daily Stoic Configuration Test")
    print("==============================")
    print(f"Project base directory: {BASE_DIR}")
    print("\nCurrent configuration values:")
    print(f"Telegram Bot Token: {config.TELEGRAM_BOT_TOKEN if config.TELEGRAM_BOT_TOKEN else '✗ Not set'}")
    print(f"Telegram Channel ID: {config.TELEGRAM_CHANNEL_ID if config.TELEGRAM_CHANNEL_ID else '✗ Not set'}")
    print(f"GEMINI_API_KEY: {config.GEMINI_API_KEY if config.GEMINI_API_KEY else '✗ Not set'}")

    
    # Validate configuration
    is_valid, missing_vars = config.validate()
    print("\nConfiguration validation:", "✓ Passed" if is_valid else "✗ Failed")
    if not is_valid:
        print("Missing required variables:", ", ".join(missing_vars))
    
    # Capture the output
    captured = capsys.readouterr()
    
    # Assert that key phrases are in the output
    assert "Daily Stoic Configuration Test" in captured.out
    assert "Project base directory:" in captured.out
    
    # Optionally, check if validation passed
    assert "✓ Passed" in captured.out, "Configuration validation failed"
    print("\n--- Captured Output ---")
    print(captured.out)
    print("----------------------")