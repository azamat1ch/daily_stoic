import os
import json
import random
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# 3. Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # 4. Load Environment & Configure API
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.error("GEMINI_API_KEY not found in environment variables.")
        return  # Exit if key is missing

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        logging.info("Gemini API configured successfully.")
    except Exception as e:
        logging.error(f"Failed to configure Gemini API: {e}")
        return

    # 5. Define Prompt Templates
    prompt_templates = {
        "Current": "Explain the core meaning and practical application of this Stoic quote in simple terms (max 100 words): '{quote_text}'",
        "Actionability": "For the Stoic quote: '{quote_text}', provide a brief (under 100 words) explanation focusing on how someone could apply this idea in their daily life. What's the key takeaway action?",
        "Core Concept": "Distill the central philosophical concept of the Stoic quote: '{quote_text}' into a clear, concise explanation (max 100 words). What is the fundamental principle being conveyed?",
        "Structured": "Analyze the Stoic quote: '{quote_text}'. Provide a structured explanation (max 100 words total) covering: 1. Core Meaning: [Brief summary]. 2. Modern Relevance/Application: [How it applies today]."
    }

    # 6. Load Quotes
    quotes_file_path = 'data/quotes.json'  # Relative path from project root
    try:
        with open(quotes_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_quotes = data.get('quotes', [])
        if not all_quotes:
            logging.error(f"No quotes found or 'quotes' key missing in {quotes_file_path}")
            return
        logging.info(f"Successfully loaded {len(all_quotes)} quotes from {quotes_file_path}")
    except FileNotFoundError:
        logging.error(f"Quotes file not found at {quotes_file_path}")
        return
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {quotes_file_path}")
        return
    except Exception as e:
        logging.error(f"An unexpected error occurred while loading quotes: {e}")
        return

    # 7. Select Sample Quotes
    num_samples = 4
    if len(all_quotes) < num_samples:
        logging.warning(f"Requested {num_samples} samples, but only {len(all_quotes)} quotes available. Using all available quotes.")
        num_samples = len(all_quotes)

    if num_samples == 0:
        logging.error("No quotes available to sample.")
        return

    sample_quotes = random.sample(all_quotes, num_samples)
    logging.info(f"Selected {len(sample_quotes)} random quotes for testing.")

    # 8. Test Prompts
    for i, sample_quote in enumerate(sample_quotes):
        quote_text = sample_quote.get('text')
        quote_author = sample_quote.get('author', 'Unknown Author')
        if not quote_text:
            logging.warning(f"Skipping quote index {i} due to missing 'text'.")
            continue

        print(f"\n--- Testing Quote {i+1}/{num_samples} ---")
        print(f"Quote: \"{quote_text}\" - {quote_author}")
        print("-" * 20)

        for template_name, template_string in prompt_templates.items():
            final_prompt = template_string.format(quote_text=quote_text)
            print(f"Testing Template: '{template_name}'")

            try:
                response = model.generate_content(final_prompt)
                # Check if response has parts and text attribute
                if response.parts:
                     explanation = response.text.strip() if hasattr(response, 'text') and response.text else "No explanation generated."
                else:
                     explanation = "No explanation generated (empty response parts)."

                print(f"Explanation ({template_name}):\n{explanation}\n")

            except Exception as e:
                logging.error(f"Error generating explanation for quote '{quote_text[:50]}...' with template '{template_name}': {e}")
                print(f"Error generating explanation for template '{template_name}'. See logs for details.\n")

        print("-" * 40) # Separator after all prompts for one quote

# 9. Run Guard
if __name__ == "__main__":
    main()
    logging.info("Script finished.")