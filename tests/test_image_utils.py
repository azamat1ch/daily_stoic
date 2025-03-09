import pytest
import os  # Added for directory creation
from PIL import Image  # Import Image from PIL
from src.image_utils import embed_text_on_image

SAMPLE_QUOTE = "This is a sample quote for testing purposes."
SAMPLE_AUTHOR = "Test Author"
SAMPLE_IMAGE_PATH = "tests/assets/test_image.png"


def test_embed_text_runs_successfully():
    """
    Tests that embed_text_on_image runs without errors and returns a PIL Image object
    with the correct dimensions.
    """
    # Read the sample image data as bytes
    with open(SAMPLE_IMAGE_PATH, 'rb') as f:
        image_bytes = f.read()

    # Get original image dimensions
    with Image.open(SAMPLE_IMAGE_PATH) as img:
        original_width, original_height = img.size

    # Call the function under test
    result_image = embed_text_on_image(image_bytes, SAMPLE_QUOTE, SAMPLE_AUTHOR)

    # Assertions
    assert isinstance(result_image, Image.Image), "Function should return a PIL Image object"
    assert result_image.size == (original_width, original_height), "Output image dimensions should match input image dimensions"

    # Save the output image for visual inspection
    output_dir = "tests/output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "test_output_image.png")
    result_image.save(output_path)