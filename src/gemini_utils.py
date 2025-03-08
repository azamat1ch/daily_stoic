# src/gemini_utils.py
import os
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import logging
from typing import Optional, List, Union

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Global Client Initialization ---
# Load API key once
load_dotenv()
API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    logging.error("FATAL: GEMINI_API_KEY not found in environment variables. Functions will fail.")
    # You might want to raise an exception here or handle it differently
    # depending on application requirements. For now, functions will check.
    CLIENT = None
else:
    try:
        # Use the client initialization pattern from gemini.md
        CLIENT = genai.Client(api_key=API_KEY)
        logging.info("Gemini Client initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize Gemini Client: {e}", exc_info=True)
        CLIENT = None

# --- Helper Function to Check Client ---
def _get_client() -> Optional[genai.Client]:
    """Returns the initialized client or logs an error and returns None."""
    if CLIENT is None:
        logging.error("Gemini Client is not initialized (check API key and initial setup).")
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

    model_name = 'gemini-2.0-flash' # Or 'gemini-2.0-flash' as per docs examples

    prompt = f"""Based on the Stoic quote: '{quote_text}', craft an evocative image prompt (max 100 words) for an AI image generator.

                1.  **Scene & Subject:** Describe a scene vividly capturing the quote's essence. Detail the main subject (this could be a statue, humans, animal, object, or even an abstract representation) and their action reflecting a Stoic principle (like acceptance, resilience, focus). Ensure the subject and scene are directly inspired by the quote.
                2.  **Setting & Atmosphere:** Paint a picture of the setting, specifying its atmosphere (e.g., a single focused individual amidst chaos, a simple room bathed in morning light).
                3.  **Visual Style:** Define a clear visual style. Aim for a **cinematic and atmospheric quality**, often utilizing **dramatic, focused, or chiaroscuro-style lighting**. Styles like **realistic digital painting, atmospheric 3D render, highly-detailed stylized illustration** fit well, but select the most appropriate for the specific quote.
                4.  **Color Palette:** Specify a fitting color palette. Try to make a photo a bit dimmed, so that it serves as the background. Often lean towards **dark, muted, deep, or contemplative tones (e.g., blues, grays, greens, earthy browns)**, but ensure it complements the scene's specific mood and subject.
                5.  **Mood:** Convey the overall mood clearly (e.g., contemplative, resilient, tranquil acceptance, quiet determination).
                6.  **Symbolism:** Include subtle, integrated symbolism related to the quote's core message.

                Ensure the final output is *only* the image prompt itself, ready for an image generation model."""
    try:
        # Use the client.models.generate_content structure from gemini.md
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt] # Pass prompt as a list
        )

        # Check response structure based on gemini.md examples
        if hasattr(response, 'text') and response.text:
            return response.text.strip()
        else:
            # Log potential reasons for empty response (e.g., safety filters)
            # Accessing feedback might differ slightly, adapt if needed based on actual response objects
            block_reason = "Unknown"
            block_message = "No specific reason provided"
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                 if hasattr(response.prompt_feedback, 'block_reason'):
                     block_reason = response.prompt_feedback.block_reason or "Reason not specified"
                 if hasattr(response.prompt_feedback, 'block_reason_message'):
                     block_message = response.prompt_feedback.block_reason_message or "Message not provided"
                 logging.warning(f"Image prompt generation potentially blocked. Reason: {block_reason}. Message: {block_message}")
            elif hasattr(response, 'candidates') and not response.candidates:
                 logging.warning("Image prompt generation failed: No candidates returned.")
            else:
                 logging.warning("Image prompt generation resulted in empty or non-text content.")
                 logging.debug(f"Full response for debugging: {response}") # Log full response if needed
            return None

    except Exception as e:
        logging.error(f"Error during Gemini API call for image prompt generation ({model_name}): {e}", exc_info=True)
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

    model_name = 'gemini-2.0-flash' # Or 'gemini-2.0-flash'

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
                     block_reason = response.prompt_feedback.block_reason or "Reason not specified"
                 if hasattr(response.prompt_feedback, 'block_reason_message'):
                     block_message = response.prompt_feedback.block_reason_message or "Message not provided"
                 logging.warning(f"Explanation generation potentially blocked. Reason: {block_reason}. Message: {block_message}")
            elif hasattr(response, 'candidates') and not response.candidates:
                 logging.warning("Explanation generation failed: No candidates returned.")
            else:
                 logging.warning("Explanation generation resulted in empty or non-text content.")
                 logging.debug(f"Full response for debugging: {response}")
            return None

    except Exception as e:
        logging.error(f"Error generating explanation ({model_name}): {e}", exc_info=True)
        return None

# --- Image Generation Function ---
def generate_image_gemini_exp(prompt_text: str) -> Optional[bytes]:
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

    model_name = 'gemini-2.0-flash-exp-image-generation'
    #model_name = 'imagen-3.0-generate-002'
    try:
        # Use the client.models.generate_content structure for image generation
        # Include the required response_modalities config
       
        # Extract image bytes based on gemini.md example structure
        image_bytes = None
        
        if model_name == 'imagen-3.0-generate-002':
            response = client.models.generate_images(
                model=model_name,
                prompt=prompt_text, # Pass prompt as a list
                config=types.GenerateImagesConfig(
                number_of_images= 1,
                )
            )   
            if response.generated_images and response.generated_images[0]:
                generated_image = response.generated_images[0]
                image_bytes = generated_image.image.image_bytes
                logging.info("Successfully extracted image bytes from response.")

        else:
            response = client.models.generate_content(
                model=model_name,
                contents=[prompt_text], # Pass prompt as a list
                config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image'] # Crucial based on gemini.md
                )
            )
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    # Check for inline_data which holds the image according to docs
                    if part.inline_data is not None and hasattr(part.inline_data, 'data'):
                        image_bytes = part.inline_data.data
                        logging.info("Successfully extracted image bytes from response.")
                        break # Found the image, no need to check other parts
                    elif part.text is not None:
                        logging.info(f"Received accompanying text part: '{part.text[:100]}...'") # Log text part if present

        if image_bytes:
            return image_bytes
        else:
            logging.warning(f"Image generation call succeeded ({model_name}) but no image data found in the expected response structure (parts[...].inline_data.data).")
            logging.debug(f"Full response for debugging: {response}")
            return None

    except Exception as e:
        logging.error(f"Error during Gemini experimental image generation ({model_name}): {e}", exc_info=True)
        return None

# --- Test Block ---
if __name__ == "__main__":
    # Ensure client is available for testing
    if _get_client():
        # Test the new image generation function
        test_prompt = """
                    Cinematic, atmospheric 3D render. A weathered, bronze statue of a blacksmith stands silhouetted against a raging wildfire encroaching on his village. He ignores the flames and chaos behind him, hammer raised mid-strike, intently shaping a gleaming sword on his anvil. Sparks fly, mirroring the distant fire but contained and controlled. Muted, earthy browns and deep oranges contrast sharply with the cool steel of the sword. Dramatic, chiaroscuro lighting focuses intensely on the blacksmith and his work, casting long, symbolic shadows. A single, unbroken chain forged from the fire's iron lays at his feet. Mood: Quiet determination amidst overwhelming adversity, embodying acceptance and purposeful action.
                """
        logging.info(f"Testing generate_image_gemini_exp with prompt: '{test_prompt}'")
        image_data = generate_image_gemini_exp(test_prompt)

        if image_data:
            logging.info("Test successful: Received image bytes.")
            output_filename = "test_image.png" # Save in project root
            try:
                # Use PIL to verify and save, similar to docs example
                img = Image.open(BytesIO(image_data))
                img.save(output_filename)
                logging.info(f"Successfully saved test image to {output_filename}")
                # Optionally show image if in interactive environment
                # img.show()
            except Exception as e:
                logging.error(f"Failed to open or save test image: {e}", exc_info=True)
        else:
            logging.error("Test failed: Did not receive image bytes from generate_image_gemini_exp.")

        # --- Optional: Test Text Generation Functions ---
        test_quote = "Waste no more time arguing about what a good man should be. Be one."

        logging.info(f"\nTesting generate_image_prompt with quote: '{test_quote}'")
        img_prompt = generate_image_prompt(test_quote)
        if img_prompt:
            logging.info(f"Generated image prompt: {img_prompt}") # Show partial prompt
        else:
            logging.error("Failed to generate image prompt.")

        logging.info(f"\nTesting generate_explanation with quote: '{test_quote}'")
        explanation = generate_explanation(test_quote)
        if explanation:
            logging.info(f"Generated explanation: {explanation}")
        else:
            logging.error("Failed to generate explanation.")
    else:
        logging.error("Cannot run tests: Gemini Client failed to initialize.")