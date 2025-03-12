# Daily Stoic AI Telegram Channel

A Telegram bot that shares daily Stoic quotes with a modern twist, combining ancient wisdom with AI-generated insights and visual content.

## Project Overview

The Daily Stoic AI Telegram Channel project aims to create an engaging and educational Telegram bot that delivers daily Stoic quotes, enhanced with AI-generated insights and visual content. The bot will source quotes from classic Stoic texts (Marcus Aurelius, Epictetus, and Seneca) and present them in a modern, accessible format.

![Example Image](tests/assets/example.jpg) 
   >**Meaning & Application:**
      When criticized, first ask yourself: is there truth in the accusation? If so, use it as a chance for self-improvement. If it's untrue, realize it's just noise and don't let it disturb your inner peace. Focus on your own actions, not others' opinions.
      
   >**Key Action:**
      When faced with negative comments, reflect on their validity. If true, improve; if false, ignore.
## Features

- Daily Stoic quotes from classic texts
- AI-generated insights and context
- Automated content scheduling
- Database-driven quote management
- Secure configuration management
- Comprehensive testing suite


## Project Structure

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

2. **Gemini API Key**
   - Required for AI-generated insights and generating visual content

