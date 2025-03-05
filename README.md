# Daily Stoic AI Telegram Channel

A Telegram bot that shares daily Stoic quotes with a modern twist, combining ancient wisdom with AI-generated insights and visual content.

## Project Overview

The Daily Stoic AI Telegram Channel project aims to create an engaging and educational Telegram bot that delivers daily Stoic quotes, enhanced with AI-generated insights and visual content. The bot will source quotes from classic Stoic texts (Marcus Aurelius, Epictetus, and Seneca) and present them in a modern, accessible format.

## Features

- Daily Stoic quotes from classic texts
- AI-generated insights and context
- Automated content scheduling
- Database-driven quote management
- Secure configuration management
- Comprehensive testing suite


## Project Structure

```
daily_stoic/
├── config/           # Database schema and configuration
├── data/            # Quote data and sources
├── src/             # Source code
│   ├── ingest_quotes.py       # Quote ingestion script
│   ├── parse_meditations_quotes.py  # Meditations quote parser
│   ├── database.py            # Database operations
│   └── config.py              # Configuration management
├── tests/           # Test files
└── deploy/          # Deployment scripts
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/azamat1ch/daily_stoic.git
   cd daily_stoic
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy the example environment file:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` with your configuration:
     - Get a Telegram Bot token from @BotFather
     - Create a Telegram channel and get its ID
     - Obtain API keys for your chosen LLM and image generation services
     - Set the desired posting time (UTC)

5. Initialize the database:
   ```bash
   python -m src.database init
   ```

6. Populate the database with quotes:
   ```bash
   python -m src.ingest_quotes
   ```

## Required API Keys

The project requires the following API keys:

1. **Telegram Bot Token**
   - Get from @BotFather on Telegram
   - Format: '1234567890:ABCdefGHIjklMNOpqrSTUVwxyz'

2. **LLM API Key**
   - Required for AI-generated insights
   - Supported providers: OpenAI, Anthropic, etc.
   - Get from your chosen provider's dashboard

3. **Image Generation API Key**
   - Required for generating visual content
   - Supported providers: DALL-E, Midjourney, etc.
   - Get from your chosen provider's dashboard

## Running the Bot

To start the bot:
```bash
python -m src.bot
```

The bot will automatically post quotes at the configured time (UTC).

## Database Setup

The project uses SQLite for storing quotes and scheduling information. The database schema is defined in `config/schema.sql`.

## Testing

The project includes a comprehensive test suite. Run tests using:
   ```bash
   python -m pytest
   ```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
