# AI Prompts (Gemini)

This document outlines the prompts used with the Google Gemini API (`gemini-1.5-flash-latest` model unless otherwise specified) via the `src/gemini_utils.py` module.

## 1. Generate Image Prompt (`generate_image_prompt`)

This prompt guides the LLM to create a detailed image generation prompt based on a Stoic quote.

**Current Active Prompt:**

```text
Generate a concise and evocative image prompt for an AI generator based on the Stoic quote: '{quote_text}'. Focus on creating a philosophical and inspirational image imbued with Stoic wisdom. The prompt must specify:

*   **Subject & Action:** A central figure or element embodying a specific Stoic principle derived from the quote (e.g., resilience, acceptance, rationality). Describe posture, expression (if applicable), and interaction with the environment clearly.
*   **Setting:** A background that contextually reinforces the philosophical theme, described with specific elements and atmosphere (e.g., 'minimalist environment', 'ancient Roman ruins at dawn', 'vast, calm sea', 'well-ordered study').
*   **Visual Style:** A precisely defined artistic style (e.g., 'Minimalist philosophical illustration with classical Roman influences', 'Photorealistic, cinematic, shallow depth of field', 'Neo-classical oil painting style', 'Stylized graphic novel art').
*   **Color Palette:** A specific, mood-enhancing color scheme (e.g., 'Muted earth tones (ochre, sienna, grey) with deep blues', 'Monochromatic grayscale with selective gold accents', 'Cool, serene blues and greens', 'Warm, contemplative sunrise hues').
*   **Mood/Atmosphere:** The desired emotional tone (e.g., 'Stoic serenity', 'Quiet determination', 'Contemplative solitude', 'Profound acceptance', 'Focused rationality').
*   **Symbolism:** Integration of relevant, clearly described Stoic visual symbols derived from the quote (e.g., 'subtly placed hourglass', 'steady flame', 'balanced geometric shapes', 'deep-rooted oak tree').
*   **Composition & Lighting:** Clear guidance on framing and light (e.g., 'Centered composition, dramatic chiaroscuro lighting', 'Rule of thirds, wide-angle, soft golden hour light', 'Symmetrical balance, high-key lighting').

The final output must be *only* the generated image prompt itself (max 100 words), coherent, rich in detail, visually appealing, and optimized for producing an image that clearly communicates Stoic philosophy based on the provided quote.
```

### Tested Variations (April 2025)

The following variations were tested using `src/test_image_prompt.py`. The "Original" prompt above was chosen as the active prompt.

**Variation 1 (Concise & Direct):**

```text
Create a visually striking image prompt (max 100 words) for an AI generator based on the Stoic quote: '{quote_text}'. The prompt must evoke Stoic philosophy and clearly define:
1. Subject/Action embodying a core principle from the quote.
2. Setting reinforcing the theme.
3. Specific Art Style (e.g., photorealistic, oil painting, minimalist illustration).
4. Mood & Color Palette (e.g., serene blues, determined earth tones).
5. Key Symbolism derived from the quote.
Output *only* the image prompt.
```

**Variation 2 (Technical Parameters):**

```text
Generate a detailed image prompt (max 100 words) for an AI generator from the Stoic quote: '{quote_text}'. Focus on philosophical depth and visual clarity. Specify:
*   Subject & Action: Central figure/element embodying a quote principle (posture, expression).
*   Setting: Contextual background (specific elements, atmosphere).
*   Visual Style: Precise artistic style (e.g., 'Cinematic photorealism', 'Classical oil painting', 'Stylized graphic art').
*   Color Palette: Mood-enhancing colors (e.g., 'Muted earth tones', 'Monochromatic grayscale', 'Sunrise hues').
*   Mood/Atmosphere: Desired tone (e.g., 'Stoic serenity', 'Quiet determination').
*   Symbolism: Relevant Stoic symbols from the quote.
*   Composition & Lighting: Framing and light (e.g., 'Centered, chiaroscuro', 'Rule of thirds, golden hour').
*   Parameters: Include '--ar 16:9 --style raw'. Add '--no text, words, signature' if appropriate.
Output *only* the image prompt itself.
```

**Variation 3 (Narrative Style):**

```text
Based on the Stoic quote: '{quote_text}', craft an evocative image prompt (max 100 words) for an AI generator. Describe a scene capturing the quote's essence. Detail the main subject and their action reflecting a Stoic principle. Paint a picture of the setting, specifying its atmosphere. Define a clear visual style (like photorealistic, illustration, or painting) and a fitting color palette. Convey the overall mood (e.g., contemplative, resilient). Include subtle symbolism related to the quote. Ensure the final output is *only* the image prompt.
```

## 2. Generate Explanation (`generate_explanation`)

This prompt guides the LLM to create a concise, action-oriented explanation of a Stoic quote.

```text
For the Stoic quote: '{quote_text}', provide a brief (under 100 words) explanation focusing on how someone could apply this idea in their daily life. What's the key takeaway action?