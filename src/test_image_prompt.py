# src/test_image_prompt.py
import os
import json
import random
import google.generativeai as genai
from dotenv import load_dotenv
import logging
import sys

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Load Environment & Configure API
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.error("GEMINI_API_KEY not found in environment variables.")
        return

    try:
        genai.configure(api_key=api_key)
        # Using the latest flash model as specified in gemini_utils.py
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        logging.info("Gemini API configured successfully for image prompt testing.")
    except Exception as e:
        logging.error(f"Failed to configure Gemini API: {e}")
        return

    # Define Image Prompt Templates
    prompt_templates = {
        "Original": """Generate a concise and evocative image prompt for an AI generator based on the Stoic quote: '{quote_text}'. Focus on creating a philosophical and inspirational image imbued with Stoic wisdom. The prompt must specify:

        *   **Subject & Action:** A central figure or element embodying a specific Stoic principle derived from the quote (e.g., resilience, acceptance, rationality). Describe posture, expression (if applicable), and interaction with the environment clearly.
        *   **Setting:** A background that contextually reinforces the philosophical theme, described with specific elements and atmosphere (e.g., 'minimalist environment', 'ancient Roman ruins at dawn', 'vast, calm sea', 'well-ordered study').
        *   **Visual Style:** A precisely defined artistic style (e.g., 'Minimalist philosophical illustration with classical Roman influences', 'Photorealistic, cinematic, shallow depth of field', 'Neo-classical oil painting style', 'Stylized graphic novel art').
        *   **Color Palette:** A specific, mood-enhancing color scheme (e.g., 'Muted earth tones (ochre, sienna, grey) with deep blues', 'Monochromatic grayscale with selective gold accents', 'Cool, serene blues and greens', 'Warm, contemplative sunrise hues').
        *   **Mood/Atmosphere:** The desired emotional tone (e.g., 'Stoic serenity', 'Quiet determination', 'Contemplative solitude', 'Profound acceptance', 'Focused rationality').
        *   **Symbolism:** Integration of relevant, clearly described Stoic visual symbols derived from the quote (e.g., 'subtly placed hourglass', 'steady flame', 'balanced geometric shapes', 'deep-rooted oak tree').
        *   **Composition & Lighting:** Clear guidance on framing and light (e.g., 'Centered composition, dramatic chiaroscuro lighting', 'Rule of thirds, wide-angle, soft golden hour light', 'Symmetrical balance, high-key lighting').

        The final output must be *only* the generated image prompt itself (max 100 words), coherent, rich in detail, visually appealing, and optimized for producing an image that clearly communicates Stoic philosophy based on the provided quote.""",

        "Variation 1 (Concise)": """Create a visually striking image prompt (max 100 words) for an AI generator based on the Stoic quote: '{quote_text}'. The prompt must evoke Stoic philosophy and clearly define:
        1. Subject/Action embodying a core principle from the quote.
        2. Setting reinforcing the theme.
        3. Specific Art Style (e.g., photorealistic, oil painting, minimalist illustration).
        4. Mood & Color Palette (e.g., serene blues, determined earth tones).
        5. Key Symbolism derived from the quote.
        Output *only* the image prompt.""",

        "Variation 2 (Technical)": """Generate a detailed image prompt (max 100 words) for an AI generator from the Stoic quote: '{quote_text}'. Focus on philosophical depth and visual clarity. Specify:
        *   Subject & Action: Central figure/element embodying a quote principle (posture, expression).
        *   Setting: Contextual background (specific elements, atmosphere).
        *   Visual Style: Precise artistic style (e.g., 'Cinematic photorealism', 'Classical oil painting', 'Stylized graphic art').
        *   Color Palette: Mood-enhancing colors (e.g., 'Muted earth tones', 'Monochromatic grayscale', 'Sunrise hues').
        *   Mood/Atmosphere: Desired tone (e.g., 'Stoic serenity', 'Quiet determination').
        *   Symbolism: Relevant Stoic symbols from the quote.
        *   Composition & Lighting: Framing and light (e.g., 'Centered, chiaroscuro', 'Rule of thirds, golden hour').
        *   Parameters: Include '--ar 16:9 --style raw'. Add '--no text, words, signature' if appropriate.
        Output *only* the image prompt itself.""",

        "Variation 3 (Narrative)": """Based on the Stoic quote: '{quote_text}', craft an evocative image prompt (max 100 words) for an AI generator. Describe a scene capturing the quote's essence. Detail the main subject and their action reflecting a Stoic principle. Paint a picture of the setting, specifying its atmosphere. Define a clear visual style (like photorealistic, illustration, or painting) and a fitting color palette. Convey the overall mood (e.g., contemplative, resilient). Include subtle symbolism related to the quote. Ensure the final output is *only* the image prompt."""
    }

    # Load Quotes
    quotes_file_path = 'data/quotes.json'
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

    # Select Sample Quotes
    num_samples = 2
    if len(all_quotes) < num_samples:
        logging.warning(f"Requested {num_samples} samples, but only {len(all_quotes)} quotes available. Using all available quotes.")
        num_samples = len(all_quotes)

    if num_samples == 0:
        logging.error("No quotes available to sample.")
        return

    sample_quotes = random.sample(all_quotes, num_samples)
    logging.info(f"Selected {len(sample_quotes)} random quotes for testing image prompts.")

    # Test Prompts
    for i, sample_quote in enumerate(sample_quotes):
        quote_text = sample_quote.get('text')
        quote_author = sample_quote.get('author', 'Unknown Author')
        if not quote_text:
            logging.warning(f"Skipping quote index {i} due to missing 'text'.")
            continue

        print(f"\n===== TESTING QUOTE {i+1}/{num_samples} =====")
        print(f"Quote: \"{quote_text}\" - {quote_author}")
        print("=" * 30)

        for template_name, template_string in prompt_templates.items():
            final_prompt = template_string.format(quote_text=quote_text)
            print(f"\n--- Testing Template: '{template_name}' ---")

            try:
                # Generate content using the model
                response = model.generate_content(final_prompt)

                # Extract text safely, checking for potential blocking or empty responses
                generated_text = None
                if response.parts:
                    generated_text = response.text.strip() if hasattr(response, 'text') and response.text else None

                if generated_text:
                    print(f"Generated Prompt ({template_name}):\n{generated_text}\n")
                else:
                    # Log details if generation failed or was blocked
                    reason = "Unknown reason"
                    if hasattr(response, 'prompt_feedback') and response.prompt_feedback and hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
                         block_reason_message = getattr(response.prompt_feedback, 'block_reason_message', 'No specific reason provided')
                         reason = f"Blocked - Reason: {response.prompt_feedback.block_reason}, Message: {block_reason_message}"
                    elif not response.parts:
                         reason = "No content parts returned"
                    logging.warning(f"Image prompt generation failed for quote '{quote_text[:50]}...' with template '{template_name}'. Reason: {reason}")
                    print(f"Failed to generate prompt for template '{template_name}'. Reason: {reason}\n")

            except Exception as e:
                logging.error(f"Error generating image prompt for quote '{quote_text[:50]}...' with template '{template_name}': {e}", exc_info=True)
                print(f"Error generating prompt for template '{template_name}'. See logs for details.\n")

        print("=" * 30) # Separator after all prompts for one quote

# Run Guard
if __name__ == "__main__":
    main()
    logging.info("Image prompt testing script finished.")