# src/gemini_utils.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging
from typing import Optional

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_image_prompt(quote_text: str) -> Optional[str]:
    """
    Generates a concise, visually descriptive image prompt from a Stoic quote
    using the Gemini API.

    Args:
        quote_text: The Stoic quote text.

    Returns:
        A string containing the generated image prompt, or None if an error occurred,
        the API key is missing, or the generation resulted in no text.
    """
    load_dotenv()
    api_key: Optional[str] = os.getenv("GEMINI_API_KEY")

    if not api_key:
        logging.error("GEMINI_API_KEY not found in environment variables.")
        return None

    try:
        genai.configure(api_key=api_key)
        # Using the latest flash model as requested
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        prompt = f"""Generate a concise and evocative image prompt for an AI generator based on the Stoic quote: '{quote_text}'. Focus on creating a philosophical and inspirational image imbued with Stoic wisdom. The prompt must specify:

        *   **Subject & Action:** A central figure or element embodying a specific Stoic principle derived from the quote (e.g., resilience, acceptance, rationality). Describe posture, expression (if applicable), and interaction with the environment clearly.
        *   **Setting:** A background that contextually reinforces the philosophical theme, described with specific elements and atmosphere (e.g., 'minimalist environment', 'ancient Roman ruins at dawn', 'vast, calm sea', 'well-ordered study').
        *   **Visual Style:** A precisely defined artistic style (e.g., 'Minimalist philosophical illustration with classical Roman influences', 'Photorealistic, cinematic, shallow depth of field', 'Neo-classical oil painting style', 'Stylized graphic novel art').
        *   **Color Palette:** A specific, mood-enhancing color scheme (e.g., 'Muted earth tones (ochre, sienna, grey) with deep blues', 'Monochromatic grayscale with selective gold accents', 'Cool, serene blues and greens', 'Warm, contemplative sunrise hues').
        *   **Mood/Atmosphere:** The desired emotional tone (e.g., 'Stoic serenity', 'Quiet determination', 'Contemplative solitude', 'Profound acceptance', 'Focused rationality').
        *   **Symbolism:** Integration of relevant, clearly described Stoic visual symbols derived from the quote (e.g., 'subtly placed hourglass', 'steady flame', 'balanced geometric shapes', 'deep-rooted oak tree').
        *   **Composition & Lighting:** Clear guidance on framing and light (e.g., 'Centered composition, dramatic chiaroscuro lighting', 'Rule of thirds, wide-angle, soft golden hour light', 'Symmetrical balance, high-key lighting').

        The final output must be *only* the generated image prompt itself (max 100 words), coherent, rich in detail, visually appealing, and optimized for producing an image that clearly communicates Stoic philosophy based on the provided quote."""

        response = model.generate_content(prompt)

        # Check if response has text content
        if hasattr(response, 'text') and response.text:
            return response.text.strip()
        else:
            # Log potential reasons for empty response (e.g., safety filters)
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback and hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
                 block_reason_message = getattr(response.prompt_feedback, 'block_reason_message', 'No specific reason provided')
                 logging.warning(f"Image prompt generation blocked. Reason: {response.prompt_feedback.block_reason}. Message: {block_reason_message}")
            elif hasattr(response, 'candidates') and not response.candidates:
                 logging.warning("Image prompt generation failed: No candidates returned.")
            else:
                 logging.warning("Image prompt generation resulted in empty or non-text content.")
            return None

    except Exception as e:
        # Log the specific exception
        logging.error(f"Error during Gemini API call for image prompt generation: {e}", exc_info=True)
        return None


def generate_explanation(quote_text: str) -> Optional[str]:
    """
    Generates a concise explanation of a Stoic quote using the Gemini API.

    Args:
        quote_text: The Stoic quote text.

    Returns:
        A string containing the generated explanation, or None if an error occurred,
        the API key is missing, or the generation resulted in no text.
    """
    load_dotenv() # Load environment variables
    api_key: Optional[str] = os.getenv("GEMINI_API_KEY")

    if not api_key:
        logging.error("GEMINI_API_KEY not found in environment variables for explanation generation.")
        return None

    try:
        # Configure the client (redundant if called after generate_image_prompt, but safe)
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        prompt = f"For the Stoic quote: '{quote_text}', provide a brief (under 100 words) explanation focusing on how someone could apply this idea in their daily life. What's the key takeaway action?"

        response = model.generate_content(prompt)

        # Check if response has text content
        if hasattr(response, 'text') and response.text:
            return response.text.strip()
        else:
            # Log potential reasons for empty response
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback and hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
                 block_reason_message = getattr(response.prompt_feedback, 'block_reason_message', 'No specific reason provided')
                 logging.warning(f"Explanation generation blocked. Reason: {response.prompt_feedback.block_reason}. Message: {block_reason_message}")
            elif hasattr(response, 'candidates') and not response.candidates:
                 logging.warning("Explanation generation failed: No candidates returned.")
            else:
                 logging.warning("Explanation generation resulted in empty or non-text content.")
            return None

    except Exception as e:
        logging.error(f"Error generating explanation: {e}", exc_info=True)
        return None