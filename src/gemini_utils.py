# src/gemini_utils.py
import os
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import logging
import json
from typing import Optional, List, Union, Dict, Any

from src.config import Config
logger = logging.getLogger(__name__) # Use module-specific logger

TEXT_MODEL_NAME = 'gemini-2.0-flash-thinking-exp' #'gemini-2.0-flash' 
IMAGE_GEN_MODEL_NAME = 'gemini-2.0-flash-exp-image-generation'
MULTIMODAL_MODEL_NAME = 'gemini-2.5-pro-exp-03-25'
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
    prompt = f"""Based on the Stoic quote: '{quote_text}', craft an evocative image prompt (max 150 words) for an AI image generator.

                1.  **Scene & Subject:** Describe a scene vividly capturing the quote's essence. Detail the main subject (this could be a statue, humans, animal, object, or even an abstract representation) and their action reflecting a Stoic principle (like acceptance, resilience, focus). Ensure the subject and scene are directly inspired by the quote.
                2.  **Setting & Atmosphere:** Paint a picture of the setting, specifying its atmosphere (e.g., a single focused individual amidst chaos, a simple room bathed in morning light).
                3.  **Visual Style:** Define a clear visual style. Aim for a **cinematic and atmospheric quality**, often utilizing **dramatic, focused, or chiaroscuro-style lighting**. Styles like **realistic digital painting, atmospheric 3D render, highly-detailed stylized illustration** fit well, but select the most appropriate for the specific quote.
                4.  **Color Palette:** Specify a fitting color palette. Try to make a photo a bit dimmed, so that it serves as the background. Often lean towards **dark, muted, deep, or contemplative tones (e.g., blues, grays, greens, earthy browns)**, but ensure it complements the scene's specific mood and subject.
                5.  **Mood:** Convey the overall mood clearly (e.g., contemplative, resilient, tranquil acceptance, quiet determination).
                6.  **Symbolism:** Include subtle, integrated symbolism related to the quote's core message.

                Ensure the final output is *only* the image prompt itself, ready for an image generation model. The prompt should explicitly mention "High-quality, 4K, stylized in 3:4 aspect ratio" to ensure proper mobile-friendly dimensions."""
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
    prompt = f"""Quote: '{quote_text}'

                Generate a readable explanation (under 100 words total) for the Stoic quote above. Focus on practical daily application and provide a key takeaway action.

                Structure the output as follows:

                1.  A section heading "Meaning & Application:" followed by an explanation of the quote's practical meaning and how to apply it daily (approx. 2-4 short sentences).
                2.  A section heading "Key Action:" followed by the core actionable step derived from the quote (approx. 1-2 short sentences).

                Formatting Instructions for the Output:
                *   Use ONLY <b>, <strong> tags for formatting. Do not use Markdown (*, _, etc.).
                *   Make the section headings ("Meaning & Application:", "Key Action:") bold using either <b> or <strong> tags.
                *   Use bold text for emphasis within the explanation sentences where appropriate, using either <b> or <strong> tags.
                *   Do NOT include other HTML tags like <p>, <a>, <code>, or <pre>.
                *   Ensure the final output is in text format. Make sure it's easy to read, uses short sentences, there is an ample white space between sections and is under the 100-word limit.
            """

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

def choose_best_image(quote_text: str, images: List[Image.Image]) -> Optional[int]:
    """
    Uses Gemini multimodal capabilities to choose the best image from a list
    based on a given quote text.

    Args:
        quote_text: The Stoic quote text to evaluate against.
        images: A list of PIL Image objects.

    Returns:
        The 0-based index of the best image in the list
    """
    client = _get_client()
    if not client:
        return None
    if not images:
        logger.warning("choose_best_image called with an empty image list.")
        return None

    num_images = len(images)
    image_indices = ", ".join(map(str, range(num_images)))
    
    model_name = MULTIMODAL_MODEL_NAME
    prompt = f"""Analyze the following Stoic quote: '{quote_text}'.
        You are provided with {num_images} images (indexed {image_indices}). Evaluate each image based on its visual quality and how well it represents the meaning and tone of the quote.

        Respond ONLY with a JSON object containing the following keys:
        - "best_image_index": The 0-based index ({image_indices}) of the image you deem the best fit.
        - "explanation": A brief explanation of why you chose that image, considering both quality and relevance to the quote.

        Use this JSON schema:
        {{
        "best_image_index": int,
        "explanation": str
        }}
        Ensure the output is only the JSON object.
    """

    try:
        contents = [prompt] + images

        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config={'response_mime_type': 'application/json'}
        )

        raw_response = response.text
        logger.info(f"Raw response from Gemini for image choice: {raw_response}")

        try:
            parsed_response = json.loads(raw_response)
            best_index = parsed_response.get("best_image_index")
            explanation = parsed_response.get("explanation") # Optional to log

            if best_index is not None and isinstance(best_index, int):
                if 0 <= best_index < num_images:
                    logger.info(f"Successfully parsed response. Best image index: {best_index}. Explanation: {explanation}")
                    return best_index
                else:
                    logger.error(f"Received invalid best_image_index: {best_index}. Number of images: {num_images}")
                    return None
            else:
                logger.error(f"Parsed JSON is missing 'best_image_index' or it's not an integer. Response: {parsed_response}")
                return None

        except json.JSONDecodeError:
            logger.error(f"Failed to parse Gemini response as JSON for image choice. Raw response was: {raw_response}")
            return None
        except Exception as e:
             logger.error(f"An error occurred after receiving/parsing image choice response: {e}", exc_info=True)
             return None

    except Exception as e:
        logger.error(f"Error during Gemini API call for image choice ({model_name}): {e}", exc_info=True)
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger.info("Running gemini_utils.py directly for testing...")

    if _get_client(): # Check if client initialization succeeded
        # Test the new image generation function
        # Correct indentation for the test prompt string
        test_prompt = """
        Portrait-oriented image in 4:5 aspect ratio. Cinematic and atmospheric realistic digital painting. A weathered blacksmith, face etched with determination, intensely hammers a glowing sword on an anvil in a dimly lit, rustic forge. Fiery sparks erupt with each strike. Dramatic chiaroscuro lighting emphasizes the blacksmith's focused gaze and the molten metal. Dark, muted color palette of earthy browns, deep reds, and soot-stained greys. Mood: quiet determination and resolute action. Symbolism: forging character through purposeful work.  Atmosphere of focused labor and inner strength.        """
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