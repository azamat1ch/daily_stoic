import io
import logging
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from src.config import Config

logger = logging.getLogger(__name__) # Use module-specific logger

def embed_text_on_image(image_data: bytes, quote_text: str, author: str) -> Image.Image | None:
    """
    Embeds quote text and author onto an image.

    Args:
        image_data: Bytes representing the image.
        quote_text: The main quote text to embed.
        author: The author of the quote.

    Returns:
        A Pillow Image object with the text embedded, or None if an error occurs.
    """
    try:
        # Load the image from bytes
        image = Image.open(io.BytesIO(image_data)).convert("RGBA")
        width, height = image.width, image.height

        # Create a drawing context
        draw = ImageDraw.Draw(image)

        # Load the font
        # Ensure the font path is a string
        font_path_str = str(Config.FONT_PATH) # Use static access Config.FONT_PATH
        # Use a relative size for the font, e.g., 5% of image height
        base_font_size = int(height * 0.05)
        quote_font = ImageFont.truetype(font_path_str, size=base_font_size)
        author_font_size = int(base_font_size * 0.7) # Slightly smaller for author
        # Construct path to italic font relative to the main font path
        italic_font_path_str = str(Config.ITALIC_FONT_PATH) # Use static access Config.ITALIC_FONT_PATH
        author_font = ImageFont.truetype(italic_font_path_str, size=author_font_size)

        # --- Text Metrics Calculation ---
        # Define max width for text wrapping (e.g., 80% of image width)
        max_text_width_ratio = 0.6
        max_text_width_pixels = int(width * max_text_width_ratio)

        # Wrap quote text based on pixel width
        wrapped_quote_lines = []
        words = quote_text.split(' ')
        current_line = ''
        for word in words:
            test_line = f"{current_line} {word}".strip()
            # Use textbbox for accurate width calculation
            line_bbox = draw.textbbox((0, 0), test_line, font=quote_font)
            line_width = line_bbox[2] - line_bbox[0]
            if line_width <= max_text_width_pixels:
                current_line = test_line
            else:
                wrapped_quote_lines.append(current_line)
                current_line = word
        wrapped_quote_lines.append(current_line) # Add the last line

        # Calculate dimensions needed for the text block
        line_spacing_multiplier = 1.3 # Increased spacing
        quote_line_heights = [draw.textbbox((0, 0), line, font=quote_font)[3] - draw.textbbox((0, 0), line, font=quote_font)[1] for line in wrapped_quote_lines]
        effective_quote_line_heights = [h * line_spacing_multiplier for h in quote_line_heights]
        total_quote_block_height = sum(effective_quote_line_heights)

        author_full_text = f"- {author}"
        author_bbox = draw.textbbox((0, 0), author_full_text, font=author_font)
        author_text_width = author_bbox[2] - author_bbox[0]
        author_text_height = (author_bbox[3] - author_bbox[1]) * line_spacing_multiplier # Apply spacing

        # Calculate the maximum width of any single line in the wrapped quote
        max_quote_line_width = max(draw.textbbox((0, 0), line, font=quote_font)[2] - draw.textbbox((0, 0), line, font=quote_font)[0] for line in wrapped_quote_lines) if wrapped_quote_lines else 0

        total_text_block_width = max(max_quote_line_width, author_text_width)
        spacing_between_quote_author = int(height * 0.02) # 2% of image height
        total_text_block_height = total_quote_block_height + spacing_between_quote_author + author_text_height

        # --- Centering Calculation ---
        block_start_x = (width - total_text_block_width) / 2
        block_start_y = (height - total_text_block_height) / 2

        # --- Readability Layer ---
        # Create a transparent overlay layer
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)

        # Draw the semi-transparent rectangle covering the whole image on the overlay
        background_color = (0, 0, 0, 128) # Black with 50% alpha
        draw_overlay.rectangle([0, 0, width, height], fill=background_color)

        # Composite the overlay onto the original image
        image = Image.alpha_composite(image.convert('RGBA'), overlay)
        # Re-create draw context for the composited image
        draw = ImageDraw.Draw(image)

        # --- Text Drawing (Centered) ---
        text_fill = 'white'
        current_y = block_start_y

        # Draw wrapped quote text line by line
        for i, line in enumerate(wrapped_quote_lines):
            line_bbox = draw.textbbox((0, 0), line, font=quote_font)
            line_width = line_bbox[2] - line_bbox[0]
            # Center each line horizontally within the text block width
            line_x = block_start_x + (total_text_block_width - line_width) / 2
            draw.text((line_x, current_y), line, font=quote_font, fill=text_fill)
            current_y += effective_quote_line_heights[i] # Move Y down by calculated height + spacing

        # Draw author text
        author_x = block_start_x + (total_text_block_width - author_text_width) / 2 # Center author within block
        author_y = block_start_y + total_quote_block_height + spacing_between_quote_author # Position below quote block
        draw.text((author_x, author_y), author_full_text, font=author_font, fill=text_fill)


        return image

    except FileNotFoundError:
        logger.error(f"Error: Font file not found at {Config.FONT_PATH}") # Use static access Config.FONT_PATH
        return None
    except IOError as e:
        logger.error(f"Error opening or processing image: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during text embedding: {e}", exc_info=True)
        return None