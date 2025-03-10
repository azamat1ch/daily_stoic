# src/gemini_utils.py
import os
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import logging
from typing import Optional, List, Union, Dict, Any

from src.config import Config
logger = logging.getLogger(__name__) # Use module-specific logger

TEXT_MODEL_NAME = 'gemini-2.0-flash' 
IMAGE_GEN_MODEL_NAME = 'gemini-2.0-flash-exp-image-generation'

# --- Global Client Initialization ---
# Load API key from Config
API_KEY: Optional[str] = Config.GEMINI_API_KEY
CLIENT: Optional[genai.Client] = None # Initialize CLIENT as None

if not API_KEY:
    logger.error("FATAL: GEMINI_API_KEY not found in Config. Functions will fail.")
else:
    try:
        # Use the client initialization pattern from gemini.md
        CLIENT = genai.Client(api_key=API_KEY)
        logger.info("Gemini Client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini Client: {e}", exc_info=True)

# --- Helper Function to Check Client ---
def _get_client() -> Optional[genai.Client]:
    """Returns the initialized client or logs an error and returns None."""
    if CLIENT is None:
        logger.error("Gemini Client is not initialized (check API key and initial setup).")
    return CLIENT

# --- Text Generation Functions ---
def generate_image_prompt(quote_text: str) -> Optional[str]:
    """
    Generates a concise, visually descriptive image prompt from a Stoic quote
    using the Gemini API (updated API usage).

    Args:
        quote_text: The Stoic quote text.

    Returns:
        A string containing the generated image prompt, or None if an error occurred.
    """
    client = _get_client()
    if not client:
        return None

    model_name = TEXT_MODEL_NAME
    prompt = f"""Based on the Stoic quote: '{quote_text}', craft an evocative image prompt (max 100 words) for an AI image generator.

                1.  **Scene & Subject:** Describe a scene vividly capturing the quote's essence. Detail the main subject (this could be a statue, humans, animal, object, or even an abstract representation) and their action reflecting a Stoic principle (like acceptance, resilience, focus). Ensure the subject and scene are directly inspired by the quote.
                2.  **Setting & Atmosphere:** Paint a picture of the setting, specifying its atmosphere (e.g., a single focused individual amidst chaos, a simple room bathed in morning light).
                3.  **Visual Style:** Define a clear visual style. Aim for a **cinematic and atmospheric quality**, often utilizing **dramatic, focused, or chiaroscuro-style lighting**. Styles like **realistic digital painting, atmospheric 3D render, highly-detailed stylized illustration** fit well, but select the most appropriate for the specific quote.
                4.  **Color Palette:** Specify a fitting color palette. Try to make a photo a bit dimmed, so that it serves as the background. Often lean towards **dark, muted, deep, or contemplative tones (e.g., blues, grays, greens, earthy browns)**, but ensure it complements the scene's specific mood and subject.
                5.  **Mood:** Convey the overall mood clearly (e.g., contemplative, resilient, tranquil acceptance, quiet determination).
                6.  **Symbolism:** Include subtle, integrated symbolism related to the quote's core message.

                Ensure the final output is *only* the image prompt itself, ready for an image generation model."""
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt] # Pass prompt as a list
        )

        if hasattr(response, 'text') and response.text:
            return response.text.strip()
        else:
            block_reason = "Unknown"
            block_message = "No specific reason provided"
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                 if hasattr(response.prompt_feedback, 'block_reason'):
                     block_reason = str(getattr(response.prompt_feedback, 'block_reason', "Reason not specified")) # Ensure string
                 if hasattr(response.prompt_feedback, 'block_reason_message'):
                     block_message = str(getattr(response.prompt_feedback, 'block_reason_message', "Message not provided")) # Ensure string
                 logger.warning(f"Image prompt generation potentially blocked. Reason: {block_reason}. Message: {block_message}")
            elif hasattr(response, 'candidates') and not response.candidates:
                 logger.warning("Image prompt generation failed: No candidates returned.")
            else:
                 logger.warning("Image prompt generation resulted in empty or non-text content.")
                 logger.debug(f"Full response for debugging: {response}") # Log full response if needed
            return None

    except Exception as e:
        logger.error(f"Error during Gemini API call for image prompt generation ({model_name}): {e}", exc_info=True)
        return None


def generate_explanation(quote_text: str) -> Optional[str]:
    """
    Generates a concise explanation of a Stoic quote using the Gemini API
    (updated API usage).

    Args:
        quote_text: The Stoic quote text.

    Returns:
        A string containing the generated explanation, or None if an error occurred.
    """
    client = _get_client()
    if not client:
        return None

    model_name = TEXT_MODEL_NAME
    prompt = f"For the Stoic quote: '{quote_text}', provide a brief (under 100 words) explanation focusing on how someone could apply this idea in their daily life. What's the key takeaway action?"

    try:
        # Use the client.models.generate_content structure
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt] # Pass prompt as a list
        )

        # Check response structure
        if hasattr(response, 'text') and response.text:
            return response.text.strip()
        else:
            # Log potential reasons for empty response
            block_reason = "Unknown"
            block_message = "No specific reason provided"
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                 if hasattr(response.prompt_feedback, 'block_reason'):
                     block_reason = str(getattr(response.prompt_feedback, 'block_reason', "Reason not specified"))
                 if hasattr(response.prompt_feedback, 'block_reason_message'):
                     block_message = str(getattr(response.prompt_feedback, 'block_reason_message', "Message not provided"))
                 logger.warning(f"Explanation generation potentially blocked. Reason: {block_reason}. Message: {block_message}")
            elif hasattr(response, 'candidates') and not response.candidates:
                 logger.warning("Explanation generation failed: No candidates returned.")
            else:
                 logger.warning("Explanation generation resulted in empty or non-text content.")
                 logger.debug(f"Full response for debugging: {response}")
            return None

    except Exception as e:
        logger.error(f"Error generating explanation ({model_name}): {e}", exc_info=True)
        return None

# --- Image Generation Function ---
def generate_image_gemini(prompt_text: str) -> Optional[bytes]:
    """
    Generates an image using the experimental Gemini image generation model
    (updated API usage based on gemini.md).

    Args:
        prompt_text: The text prompt for image generation.

    Returns:
        The raw image bytes if successful, otherwise None.
    """
    client = _get_client()
    if not client:
        return None

    model_name = IMAGE_GEN_MODEL_NAME
    try:
        response = client.models.generate_content(
                model=model_name,
                contents=[prompt_text], # Pass prompt as a list
                config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image'] # Crucial based on gemini.md
                )
            )
        image_bytes = None
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                # Check for inline_data which holds the image according to original code
                if part.inline_data is not None and hasattr(part.inline_data, 'data'):
                    image_bytes = part.inline_data.data
                    logger.info("Successfully extracted image bytes from response.")
                    break # Found the image, no need to check other parts
                elif part.text is not None:
                     # Log text part if present (as in original)
                    logger.info(f"Received accompanying text part: '{part.text[:100]}...'")

        if image_bytes:
            return image_bytes
        else:
            logger.warning(f"Image generation call succeeded ({model_name}) but no image data found in the expected response structure (parts[...].inline_data.data).")
            logger.debug(f"Full response for debugging: {response}")
            return None

    except Exception as e:
        logger.error(f"Error during Gemini image generation ({model_name}): {e}", exc_info=True)
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger.info("Running gemini_utils.py directly for testing...")

    if _get_client(): # Check if client initialization succeeded
        # Test the new image generation function
        # Correct indentation for the test prompt string
        test_prompt = """Cinematic, atmospheric 3D render. A weathered, bronze statue of a blacksmith stands silhouetted against a raging wildfire encroaching on his village. He ignores the flames and chaos behind him, hammer raised mid-strike, intently shaping a gleaming sword on his anvil. Sparks fly, mirroring the distant fire but contained and controlled. Muted, earthy browns and deep oranges contrast sharply with the cool steel of the sword. Dramatic, chiaroscuro lighting focuses intensely on the blacksmith and his work, casting long, symbolic shadows. A single, unbroken chain forged from the fire's iron lays at his feet. Mood: Quiet determination amidst overwhelming adversity, embodying acceptance and purposeful action."""
        logger.info(f"Testing generate_image_gemini with prompt: '{test_prompt}'")
        image_data = generate_image_gemini(test_prompt)

        if image_data:
            logging.info("Test successful: Received image bytes.")
            # Ensure tests/assets directory exists
            output_dir = "tests/assets"
            os.makedirs(output_dir, exist_ok=True)
            output_filename = os.path.join(output_dir, "test_image.png")
            try:
                # Use PIL to verify and save, similar to docs example
                img = Image.open(BytesIO(image_data))
                img.save(output_filename)
                logging.info(f"Successfully saved test image to {output_filename}")
                # Optionally show image if in interactive environment
                # img.show()
            except Exception as e:
                logger.error(f"Failed to open or save test image: {e}", exc_info=True)
        else:
            logger.error("Test failed: Did not receive image bytes from generate_image_gemini.")

        # --- Optional: Test Text Generation Functions ---
        test_quote = "Waste no more time arguing about what a good man should be. Be one."

        logger.info(f"\nTesting generate_image_prompt with quote: '{test_quote}'")
        img_prompt = generate_image_prompt(test_quote)
        if img_prompt:
            logger.info(f"Generated image prompt: {img_prompt}")
        else:
            logger.error("Failed to generate image prompt.")

        logger.info(f"\nTesting generate_explanation with quote: '{test_quote}'")
        explanation = generate_explanation(test_quote)
        if explanation:
            logger.info(f"Generated explanation: {explanation}")
        else:
            logger.error("Failed to generate explanation.")
    else:
        logger.error("Cannot run tests: Gemini Client failed to initialize (check API Key in .env).")